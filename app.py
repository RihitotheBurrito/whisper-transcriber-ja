import os
import shutil
import whisper
import torch
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import logging
import time
from tqdm import tqdm
import tempfile
import threading
import json
import webbrowser
import socket
from threading import Timer
import io
import re
import sys
import contextlib

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Flaskのログレベルを変更してアクセスログを抑制
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.WARNING)  # WARNINGレベル以上のみ表示

app = Flask(__name__)
app.secret_key = "whisper-transcriber-secret-key"
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 最大100MB

# フォルダパスの設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "audiofile")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "output")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "processed")

# フォルダが存在しない場合は作成
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, PROCESSED_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# 許可するファイル拡張子
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'aac', 'ogg'}

# モデルとデバイスのグローバル変数
model = None
device = "cpu"

# 処理の進捗状況を保存するグローバル変数
transcription_progress = {
    "status": "idle",  # idle, loading_model, processing, completed, error
    "file": "",
    "progress": 0,
    "message": "",
    "time_elapsed": 0
}
transcription_lock = threading.Lock()
stop_progress_update = threading.Event()

# ブラウザを開いたかどうかのフラグ
browser_opened = False

# Whisper進捗バーの正規表現パターン
whisper_progress_pattern = re.compile(r'(\d+)%\|(.+?)\| (\d+)/(\d+)')

def update_progress(status, file="", progress=0, message="", time_elapsed=0):
    """進捗状況を更新するヘルパー関数"""
    global transcription_progress
    with transcription_lock:
        # 進捗値が0に戻る問題を防止（処理中の場合）
        if status == "processing" and progress == 0 and transcription_progress["progress"] > 0:
            # 既に進行中で、進捗が0に戻るのを防止（初期状態じゃない場合）
            if transcription_progress["file"] == file:
                # 同じファイルの処理中は進捗を0に戻さない
                progress = transcription_progress["progress"]
        
        transcription_progress["status"] = status
        transcription_progress["file"] = file
        transcription_progress["progress"] = progress
        transcription_progress["message"] = message
        transcription_progress["time_elapsed"] = time_elapsed

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_optimal_device():
    """最適なデバイスを検出"""
    if torch.cuda.is_available():
        return "cuda"
    # MPS (Apple Silicon) はWhisperと互換性がないため使用しない
    # MPSでもCPUを返すように修正
    return "cpu"

def load_model(model_name="base", device=None):
    """Whisperモデルをロード"""
    update_progress("loading_model", message=f"{model_name}モデルをロード中...")
    
    if device is None:
        device = get_optimal_device()
    
    start_time = time.time()
    try:
        model = whisper.load_model(
            model_name,
            device=device,
            download_root=os.path.join(os.path.expanduser("~"), ".cache", "whisper")
        )
        elapsed_time = time.time() - start_time
        update_progress("idle", message=f"{model_name}モデルを{device}デバイスで読み込みました（所要時間: {elapsed_time:.2f}秒）")
        logging.info(f"{model_name}モデルを{device}デバイスで読み込みました（所要時間: {elapsed_time:.2f}秒）")
        return model
    except Exception as e:
        logging.error(f"モデル読み込みエラー: {e}")
        # MPSの場合に失敗したら、CPUにフォールバック
        if device != "cpu":
            logging.info(f"{device}での読み込みに失敗しました。CPUにフォールバックします。")
            update_progress("loading_model", message=f"{device}での読み込みに失敗しました。CPUにフォールバックします。")
            return load_model(model_name, "cpu")
        update_progress("error", message=f"モデル読み込みエラー: {str(e)}")
        return None

@app.route('/')
def index():
    # 処理済みファイル一覧の取得の前に、ページロード時に完了状態をリセット
    global transcription_progress
    with transcription_lock:
        if transcription_progress["status"] == "completed":
            transcription_progress["status"] = "idle"
            transcription_progress["message"] = ""
            transcription_progress["progress"] = 0
    
    # 処理済みファイル一覧の取得
    output_files = []
    for file in os.listdir(OUTPUT_FOLDER):
        if file.endswith('.txt'):
            output_files.append({
                'name': file,
                'path': url_for('download_file', filename=file)
            })
    
    # 処理前のファイル一覧の取得
    pending_files = []
    for file in os.listdir(UPLOAD_FOLDER):
        if allowed_file(file):
            pending_files.append(file)
    
    return render_template('index.html', output_files=output_files, pending_files=pending_files)

@app.route('/progress')
def progress():
    """進捗状況を返すAPIエンドポイント"""
    return jsonify(transcription_progress)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('ファイルが選択されていません')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('ファイルが選択されていません')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        flash(f'ファイル {filename} がアップロードされました')
        return redirect(url_for('index'))
    else:
        flash('許可されていないファイル形式です')
        return redirect(request.url)

# 標準出力をキャプチャするためのコンテキストマネージャ
class WhisperProgressCapture:
    def __init__(self, selected_file, start_time):
        self.selected_file = selected_file
        self.start_time = start_time
        self.buffer = io.StringIO()
        self.old_stdout = None
    
    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = self.buffer
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.old_stdout
    
    def check_progress(self):
        # バッファの内容を取得
        output = self.buffer.getvalue()
        # バッファをリセット
        self.buffer.truncate(0)
        self.buffer.seek(0)
        
        # 進捗バーを検索
        for line in output.split('\n'):
            match = whisper_progress_pattern.search(line)
            if match:
                percent = int(match.group(1))
                # 進捗状況を更新（Whisperの進捗は0-100%）
                elapsed = time.time() - self.start_time
                update_progress("processing", file=self.selected_file, progress=percent, 
                             message=f"処理中... {percent}%完了", time_elapsed=elapsed)
                return percent
        return None

def process_transcription(selected_file, model_name, language, compute_type):
    """別スレッドで文字起こし処理を実行する関数"""
    global model, device, stop_progress_update, transcription_progress
    
    # 処理開始時に前回の完了状態をリセット
    with transcription_lock:
        if transcription_progress["status"] == "completed":
            transcription_progress["status"] = "idle"
            
    # 前回実行の進捗更新スレッドが残っていれば停止
    stop_progress_update.set()
    time.sleep(0.5)  # 確実に停止させるため
    stop_progress_update.clear()
    
    full_audio_path = os.path.join(UPLOAD_FOLDER, selected_file)
    
    try:
        # Whisperで文字起こし
        update_progress("processing", file=selected_file, progress=0, message="音声解析の準備中...")
        transcription_start = time.time()
        
        # 標準出力をキャプチャして進捗を監視
        with WhisperProgressCapture(selected_file, transcription_start) as progress_capture:
            # 進捗監視スレッド
            def monitor_progress():
                start_elapsed = time.time()
                current_progress = 0
                while not stop_progress_update.is_set():
                    # 進捗キャプチャを実行して現在の進行状況を取得
                    captured_progress = progress_capture.check_progress()
                    
                    # 有効な進捗が得られた場合は更新
                    if captured_progress is not None:
                        current_progress = captured_progress
                    
                    # Whisperが進捗を出力しない場合でも経過時間を更新
                    current_elapsed = time.time() - transcription_start
                    update_progress("processing", file=selected_file, 
                                   progress=current_progress,
                                   message=f"処理中... {current_progress}%完了" if current_progress > 0 else "処理中...",
                                   time_elapsed=current_elapsed)
                    time.sleep(0.5)  # 短い間隔で確認
            
            # 進捗監視スレッド開始
            monitor_thread = threading.Thread(target=monitor_progress)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # 実際の文字起こし処理
            logging.info(f"文字起こし処理開始: {selected_file}")
            result = model.transcribe(
                full_audio_path, 
                language=language,
                fp16=(compute_type == "float16"),
                verbose=True  # 進捗バーを表示するために有効化
            )
            logging.info(f"文字起こし処理完了: {selected_file}")
        
        # 進捗更新スレッドを停止
        stop_progress_update.set()
        
        transcription_time = time.time() - transcription_start
        
        # 出力ファイルの作成
        update_progress("processing", file=selected_file, progress=85, 
                      message="ファイル保存中...", time_elapsed=transcription_time)
        
        base_name = os.path.splitext(selected_file)[0]
        output_file = os.path.join(OUTPUT_FOLDER, f"{base_name}.txt")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        # 処理済みファイルを移動
        update_progress("processing", file=selected_file, progress=95, 
                      message="ファイルを移動中...", time_elapsed=transcription_time)
        
        shutil.move(full_audio_path, os.path.join(PROCESSED_FOLDER, selected_file))
        
        # 完了
        update_progress("completed", file=selected_file, progress=100, 
                      message=f"文字起こし完了（処理時間: {transcription_time:.2f}秒）。出力: {base_name}.txt", 
                      time_elapsed=transcription_time)
        
    except Exception as e:
        # エラー発生時は進捗更新スレッドを停止
        stop_progress_update.set()
        
        error_message = f'エラーが発生しました: {str(e)}'
        update_progress("error", file=selected_file, message=error_message)
        logging.error(error_message)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    global model, device
    
    # 現在処理中の場合は警告
    if transcription_progress["status"] in ["processing", "loading_model"]:
        flash('別の処理が進行中です。完了するまでお待ちください。')
        return redirect(url_for('index'))
    
    # モデル選択
    model_name = request.form.get('model', 'base')
    language = request.form.get('language', 'ja')
    compute_type = request.form.get('compute_type', 'float32')
    
    # モデルがロードされていないか、異なるモデルが選択された場合、新しくロード
    if model is None or request.form.get('reload_model', False):
        device = get_optimal_device()
        model = load_model(model_name, device)
        if model is None:
            flash('モデルのロードに失敗しました')
            return redirect(url_for('index'))
    
    # 処理対象のファイル
    selected_file = request.form.get('selected_file')
    if not selected_file:
        flash('ファイルが選択されていません')
        return redirect(url_for('index'))
    
    full_audio_path = os.path.join(UPLOAD_FOLDER, selected_file)
    if not os.path.exists(full_audio_path):
        flash(f'ファイル {selected_file} が見つかりません')
        return redirect(url_for('index'))
    
    # 別スレッドで処理を実行
    threading.Thread(
        target=process_transcription, 
        args=(selected_file, model_name, language, compute_type)
    ).start()
    
    flash(f'ファイル {selected_file} の文字起こしを開始しました。進捗状況を確認してください。')
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

@app.route('/delete_output/<filename>')
def delete_output(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'出力ファイル {filename} を削除しました')
    else:
        flash(f'ファイル {filename} が見つかりません')
    return redirect(url_for('index'))

@app.route('/delete_pending/<filename>')
def delete_pending(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'未処理ファイル {filename} を削除しました')
    else:
        flash(f'ファイル {filename} が見つかりません')
    return redirect(url_for('index'))

def is_port_in_use(port):
    """指定されたポートが使用中かどうかを確認するヘルパー関数"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def open_browser(url):
    """ブラウザを開く関数"""
    global browser_opened
    if not browser_opened:
        browser_opened = True
        webbrowser.open(url)

if __name__ == '__main__':
    # ポートが使用中の場合は別のポートを使用する
    port = 8080
    while is_port_in_use(port):
        port += 1
        if port > 8100:  # 最大で20個のポートを試す
            logging.warning(f"利用可能なポートが見つかりませんでした。手動でブラウザを開いてください。")
            break
    
    # サーバー起動後にブラウザを開く
    if port <= 8100:
        url = f"http://localhost:{port}"
        logging.info(f"ブラウザを開きます: {url}")
        # サーバー起動の少し後にブラウザを開く
        Timer(1.5, lambda: open_browser(url)).start()
    
    # 起動時にはモデルをロードしない（リクエスト時にロードする）
    # デバッグモードをオフにして、リロード時に複数ブラウザが開かないようにする
    app.run(debug=False, host='0.0.0.0', port=port) 
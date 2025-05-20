import os
import shutil
import whisper
import torch
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import logging
import time
from tqdm import tqdm
import tempfile

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

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
    if device is None:
        device = get_optimal_device()
    
    start_time = time.time()
    try:
        model = whisper.load_model(
            model_name,
            device=device,
            download_root=os.path.join(os.path.expanduser("~"), ".cache", "whisper")
        )
        logging.info(f"{model_name}モデルを{device}デバイスで読み込みました（所要時間: {time.time() - start_time:.2f}秒）")
        return model
    except Exception as e:
        logging.error(f"モデル読み込みエラー: {e}")
        # MPSの場合に失敗したら、CPUにフォールバック
        if device != "cpu":
            logging.info(f"{device}での読み込みに失敗しました。CPUにフォールバックします。")
            return load_model(model_name, "cpu")
        return None

@app.route('/')
def index():
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

@app.route('/transcribe', methods=['POST'])
def transcribe():
    global model, device
    
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
    
    try:
        # Whisperで文字起こし
        transcription_start = time.time()
        
        result = model.transcribe(
            full_audio_path, 
            language=language,
            fp16=(compute_type == "float16"),
            verbose=False
        )
        
        transcription_time = time.time() - transcription_start
        
        # 出力ファイルの作成
        base_name = os.path.splitext(selected_file)[0]
        output_file = os.path.join(OUTPUT_FOLDER, f"{base_name}.txt")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        # 処理済みファイルを移動
        shutil.move(full_audio_path, os.path.join(PROCESSED_FOLDER, selected_file))
        
        flash(f'文字起こし完了（処理時間: {transcription_time:.2f}秒）。出力: {base_name}.txt')
    except Exception as e:
        flash(f'エラーが発生しました: {str(e)}')
    
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

if __name__ == '__main__':
    # 起動時にはモデルをロードしない（リクエスト時にロードする）
    app.run(debug=True, host='0.0.0.0', port=8080) 
import os
import shutil
import whisper
import torch
import argparse
import logging
import time
from tqdm import tqdm

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def setup_parser():
    parser = argparse.ArgumentParser(description="Whisper音声文字起こしツール")
    parser.add_argument("--model", default="turbo", help="使用するWhisperモデル (tiny, base, small, medium, large)")
    parser.add_argument("--language", default="ja", help="文字起こしする言語")
    parser.add_argument("--device", default="cpu", help="使用するデバイス (cpu, cuda, auto)")
    parser.add_argument("--batch_size", type=int, default=16, help="バッチサイズ")
    parser.add_argument("--compute_type", default="float32", help="計算タイプ (float16, float32)")
    return parser

def get_optimal_device():
    """最適なデバイスを検出"""
    if torch.cuda.is_available():
        return "cuda"
    # MPS (Apple Silicon) はWhisperと互換性がないため使用しない
    return "cpu"

def transcribe_audio_files():
    # コマンドラインパラメータの解析
    parser = setup_parser()
    args = parser.parse_args()
    
    # デバイスの選択
    if args.device == "auto":
        device = get_optimal_device()
        logging.info(f"自動検出されたデバイス: {device}")
    else:
        device = args.device
    
    # CUDA情報の表示
    if device == "cuda":
        logging.info(f"CUDA バージョン: {torch.version.cuda}")
        logging.info(f"CUDA デバイス: {torch.cuda.get_device_name(0)}")
        logging.info(f"利用可能なGPUメモリ: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    
    # モデルのロード
    try:
        # 警告を避けるためweights_only=Trueを追加
        start_time = time.time()
        model = whisper.load_model(
            args.model,
            device=device,
            download_root=os.path.join(os.path.expanduser("~"), ".cache", "whisper")
        )
        logging.info(f"{args.model}モデルを{device}デバイスで読み込みました（所要時間: {time.time() - start_time:.2f}秒）")
        
        # システム情報を表示
        system_info = "RAM 16GB"
        if torch.cuda.is_available():
            system_info += f", GPU: {torch.cuda.get_device_name(0)}"
        else:
            system_info += ", CPU のみ"
        logging.info(f"システム情報: {system_info}")
        logging.info(f"計算タイプ: {args.compute_type}")
    except Exception as e:
        logging.error(f"モデル読み込みエラー: {e}")
        if device != "cpu":
            logging.info(f"{device}での読み込みに失敗しました。CPUにフォールバックします。")
            try:
                start_time = time.time()
                model = whisper.load_model(
                    args.model,
                    device="cpu",
                    download_root=os.path.join(os.path.expanduser("~"), ".cache", "whisper")
                )
                device = "cpu"
                logging.info(
                    f"{args.model}モデルをcpuデバイスで読み込みました（所要時間: {time.time() - start_time:.2f}秒）")
            except Exception as e_cpu:
                logging.error(f"CPUでのモデル読み込みも失敗しました: {e_cpu}")
                return
        else:
            return

    # 処理対象フォルダと出力フォルダを指定
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_folder = os.path.join(base_dir, "audiofile")
    output_folder = os.path.join(base_dir, "output")
    processed_folder = os.path.join(base_dir, "processed")

    # 必要なフォルダが存在しない場合は作成
    for folder in [audio_folder, output_folder, processed_folder]:
        os.makedirs(folder, exist_ok=True)

    # フォルダ内の音声ファイルを取得
    audio_files = [f for f in os.listdir(audio_folder) if f.lower().endswith((".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg"))]

    if audio_files:
        logging.info(f"{len(audio_files)}個の音声ファイルが見つかりました")
        
        # プログレスバーでの処理表示
        for audio_file in tqdm(audio_files, desc="文字起こし処理"):
            full_audio_path = os.path.join(audio_folder, audio_file)
            
            logging.info(f"処理中: {audio_file}")
            
            try:
                # Whisperで文字起こし
                transcription_start = time.time()
                
                result = model.transcribe(
                    full_audio_path, 
                    language=args.language,
                    fp16=(args.compute_type == "float16"),
                    verbose=False
                )
                
                transcription_time = time.time() - transcription_start
                
                # 出力ファイルの作成
                base_name = os.path.splitext(audio_file)[0]
                output_file = os.path.join(output_folder, f"{base_name}.txt")
                
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result["text"])
                
                # 音声ファイルの長さを取得（概算）
                audio_info = f"文字起こし完了（処理時間: {transcription_time:.2f}秒）"
                logging.info(f"{audio_info}")
                logging.info(f"テキストは {output_file} に保存されました")
                
                # 処理済みファイルを移動
                shutil.move(full_audio_path, os.path.join(processed_folder, audio_file))
                logging.info(f"処理済みファイルを {processed_folder} に移動しました")
                
            except Exception as e:
                logging.error(f"ファイル '{audio_file}' の処理中にエラーが発生しました: {e}")
    else:
        logging.warning("フォルダに音声ファイルが見つかりませんでした")
        print("フォルダに音声ファイルが見つかりませんでした。audiofileディレクトリに音声ファイルを配置してください。")

if __name__ == "__main__":
    start_time = time.time()
    transcribe_audio_files()
    total_time = time.time() - start_time
    logging.info(f"処理完了！合計時間: {total_time:.2f}秒")

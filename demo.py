#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Whisper デモスクリプト
サンプル音声でWhisperの動作を確認するためのスクリプト
"""

import os
import sys
import torch
import whisper
import argparse
import time
from urllib.request import urlretrieve
from tqdm import tqdm
import shutil
import logging

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# サンプル音声のURL (Creative Commons ライセンスの音声)
SAMPLE_AUDIO_URL = "https://github.com/openai/whisper/raw/main/tests/jfk.flac"
SAMPLE_AUDIO_FILENAME = "sample_jfk.flac"  # JFKのスピーチ（英語）

def download_sample_audio(output_dir):
    """サンプル音声をダウンロード"""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, SAMPLE_AUDIO_FILENAME)
    
    # すでにファイルが存在する場合はスキップ
    if os.path.exists(output_path):
        logging.info(f"サンプル音声ファイルは既に存在します: {output_path}")
        return output_path
    
    logging.info(f"サンプル音声をダウンロード中: {SAMPLE_AUDIO_URL}")
    try:
        urlretrieve(SAMPLE_AUDIO_URL, output_path)
        logging.info(f"サンプル音声をダウンロードしました: {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"サンプル音声のダウンロードに失敗しました: {e}")
        sys.exit(1)

def setup_parser():
    """コマンドライン引数の設定"""
    parser = argparse.ArgumentParser(description="Whisperデモ")
    parser.add_argument("--model", default="tiny", help="使用するWhisperモデル (tiny, base, small, medium, large)")
    parser.add_argument("--language", default="en", help="文字起こしする言語 (デモ音声は英語)")
    parser.add_argument("--device", default="auto", help="使用するデバイス (cpu, cuda, auto)")
    parser.add_argument("--compute_type", default="float32", help="計算タイプ (float16, float32)")
    return parser

def get_optimal_device():
    """最適なデバイスを検出"""
    if torch.cuda.is_available():
        return "cuda"
    # MPS (Apple Silicon) はWhisperと互換性がないため使用しない
    return "cpu"

def main():
    """メイン関数"""
    # コマンドライン引数の解析
    parser = setup_parser()
    args = parser.parse_args()
    
    # デバイスの選択
    if args.device == "auto":
        device = get_optimal_device()
        logging.info(f"自動検出されたデバイス: {device}")
    else:
        device = args.device
    
    # プロジェクトディレクトリの取得
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_folder = os.path.join(base_dir, "audiofile")
    output_folder = os.path.join(base_dir, "output")
    
    # サンプル音声のダウンロード
    sample_audio_path = download_sample_audio(audio_folder)
    
    # モデルのロード
    logging.info(f"{args.model} モデルを {device} デバイスで読み込み中...")
    start_time = time.time()
    
    try:
        model = whisper.load_model(
            args.model,
            device=device,
            download_root=os.path.join(os.path.expanduser("~"), ".cache", "whisper")
        )
        logging.info(f"モデル読み込み完了（所要時間: {time.time() - start_time:.2f}秒）")
    except Exception as e:
        logging.error(f"モデル読み込みエラー: {e}")
        # デバイスがCPUでなければCPUにフォールバック
        if device != "cpu":
            logging.info(f"{device}での読み込みに失敗しました。CPUにフォールバックします。")
            args.device = "cpu"
            main()  # CPUで再実行
            return
        return
    
    # 文字起こしの実行
    logging.info(f"サンプル音声の文字起こしを実行中...")
    transcription_start = time.time()
    
    try:
        result = model.transcribe(
            sample_audio_path,
            language=args.language,
            fp16=(args.compute_type == "float16"),
            verbose=False
        )
        
        transcription_time = time.time() - transcription_start
        logging.info(f"文字起こし完了（処理時間: {transcription_time:.2f}秒）")
        
        # 出力ファイルの作成
        output_file = os.path.join(output_folder, f"{os.path.splitext(SAMPLE_AUDIO_FILENAME)[0]}.txt")
        os.makedirs(output_folder, exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        logging.info(f"文字起こし結果をファイルに保存しました: {output_file}")
        
        # 結果を表示
        print("\n" + "="*50)
        print("文字起こし結果:")
        print("="*50)
        print(result["text"])
        print("="*50)
        
    except Exception as e:
        logging.error(f"文字起こし中にエラーが発生しました: {e}")
    
    # 文字起こしのベンチマーク情報を表示
    total_time = time.time() - start_time
    logging.info(f"合計処理時間: {total_time:.2f}秒")
    
    if device == "cuda":
        logging.info(f"CUDA デバイス: {torch.cuda.get_device_name(0)}")
        logging.info(f"CUDA メモリ使用量: {torch.cuda.max_memory_allocated() / 1024**3:.2f} GB")

if __name__ == "__main__":
    main()

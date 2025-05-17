#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CUDA 環境テストスクリプト
Whisper 音声文字起こしツールの環境をテストするためのスクリプト
"""

import os
import torch
import platform
import sys
import subprocess
import psutil
from colorama import init, Fore, Style

# カラー出力の初期化
init()

def print_success(message):
    """成功メッセージの表示"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    """エラーメッセージの表示"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_warning(message):
    """警告メッセージの表示"""
    print(f"{Fore.YELLOW}! {message}{Style.RESET_ALL}")

def print_info(message):
    """情報メッセージの表示"""
    print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")

def print_header(message):
    """ヘッダーの表示"""
    print(f"\n{Fore.BLUE}=== {message} ==={Style.RESET_ALL}")

def check_python():
    """Pythonバージョンの確認"""
    print_header("Python情報")
    version = sys.version.split()[0]
    print_info(f"Python バージョン: {version}")
    if tuple(map(int, version.split('.'))) >= (3, 8):
        print_success("Python 3.8 以上を使用しています")
    else:
        print_warning("Python 3.8 以上を推奨します")

def check_cuda():
    """CUDA環境の確認"""
    print_header("CUDA環境")
    
    if torch.cuda.is_available():
        cuda_version = torch.version.cuda
        device_name = torch.cuda.get_device_name(0)
        device_count = torch.cuda.device_count()
        cuda_capability = torch.cuda.get_device_capability(0)
        
        print_success(f"CUDA が利用可能です")
        print_info(f"CUDA バージョン: {cuda_version}")
        print_info(f"GPU デバイス: {device_name}")
        print_info(f"GPU 数: {device_count}")
        print_info(f"CUDA Capability: {cuda_capability[0]}.{cuda_capability[1]}")
        
        # メモリ情報
        total_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        free_mem = torch.cuda.memory_reserved(0) / (1024**3)
        print_info(f"GPU メモリ総量: {total_mem:.2f} GB")
        
        # Whisperモデルの推奨
        if total_mem >= 10:
            print_success("large モデルが使用可能です")
        elif total_mem >= 5:
            print_success("medium モデルが使用可能です")
        elif total_mem >= 2:
            print_warning("small または base モデルの使用を推奨します")
        else:
            print_warning("tiny モデルのみ使用可能です")
    else:
        print_error("CUDA は利用できません")
        
        if platform.system() == "Darwin" and platform.processor() == "arm":
            print_info("Apple Silicon (M1/M2) が検出されました")
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                print_success("MPS (Metal Performance Shaders) が利用可能です")
                print_warning("Whisper は MPS に完全に対応していない場合があります")
            else:
                print_warning("MPS が利用できません")
        
        print_warning("CPU のみで実行されます（処理が遅くなります）")

def check_whisper():
    """Whisperのインストール確認"""
    print_header("Whisper 環境")
    try:
        import whisper
        print_success("Whisper がインストールされています")
        if hasattr(whisper, "__version__"):
            print_info(f"Whisper バージョン: {whisper.__version__}")
    except ImportError:
        print_error("Whisper がインストールされていません")
        print_info("インストール方法: pip install -U openai-whisper")

def check_system():
    """システム情報の確認"""
    print_header("システム情報")
    print_info(f"OS: {platform.system()} {platform.release()}")
    print_info(f"プロセッサ: {platform.processor()}")
    
    # メモリ情報
    mem = psutil.virtual_memory()
    print_info(f"物理メモリ: {mem.total / (1024**3):.2f} GB")
    
    if mem.total < 8 * (1024**3):
        print_warning("8GB 以上のメモリを推奨します")
    else:
        print_success("メモリ容量は十分です")

def run_benchmark():
    """簡易ベンチマークの実行"""
    print_header("簡易ベンチマーク")
    
    if not torch.cuda.is_available():
        print_warning("CUDA が利用できないため、ベンチマークをスキップします")
        return
    
    print_info("CUDA テンソル計算のベンチマークを実行中...")
    
    # ウォームアップ
    x = torch.randn(1000, 1000).cuda()
    torch.matmul(x, x.T)
    torch.cuda.synchronize()
    
    # 計測
    import time
    start = time.time()
    
    for _ in range(10):
        x = torch.randn(2000, 2000).cuda()
        y = torch.matmul(x, x.T)
        z = y.sum()
        torch.cuda.synchronize()
    
    end = time.time()
    
    print_info(f"ベンチマーク結果: {(end - start):.4f} 秒")
    
    if end - start < 1.0:
        print_success("GPU パフォーマンスは非常に良好です")
    elif end - start < 3.0:
        print_success("GPU パフォーマンスは良好です")
    else:
        print_warning("GPU パフォーマンスが期待より低いです")

def print_recommended_command():
    """推奨コマンドの表示"""
    print_header("推奨コマンド")
    
    if torch.cuda.is_available():
        mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        if mem >= 10:
            model = "large"
        elif mem >= 5:
            model = "medium"
        elif mem >= 2:
            model = "small"
        else:
            model = "tiny"
        
        command = f"python audio_transcribe.py --model {model} --device cuda --compute_type float16"
        print_info(f"推奨コマンド: {command}")
        
        if model != "large":
            print_warning(f"注意: {model} モデルを推奨していますが、精度向上のためより大きなモデルを使用すると処理時間が増加します")
    else:
        print_info("推奨コマンド: python audio_transcribe.py --model base --device cpu")
        print_warning("CPU での実行は時間がかかります。小さなモデルの使用を推奨します")

def main():
    """メイン関数"""
    print(f"{Fore.CYAN}================================================{Style.RESET_ALL}")
    print(f"{Fore.CYAN}    Whisper 音声文字起こしツール 環境テスト    {Style.RESET_ALL}")
    print(f"{Fore.CYAN}================================================{Style.RESET_ALL}")
    
    check_python()
    check_system()
    check_cuda()
    check_whisper()
    
    try:
        run_benchmark()
    except Exception as e:
        print_error(f"ベンチマーク実行中にエラーが発生しました: {e}")
    
    print_recommended_command()
    
    print(f"\n{Fore.CYAN}テスト完了{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nテストが中断されました")
    except Exception as e:
        print_error(f"予期せぬエラーが発生しました: {e}")

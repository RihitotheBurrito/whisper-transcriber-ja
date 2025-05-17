#!/bin/bash
# Whisper 音声文字起こしツールのセットアップスクリプト

echo "Whisper 音声文字起こしツールのセットアップを開始します..."

# venv 環境を作成
python -m venv myenv

# 環境を有効化（OS に応じて異なる方法を表示）
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Windows が検出されました。"
    echo "環境を有効化します..."
    source myenv/Scripts/activate || . myenv/Scripts/activate
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS が検出されました。"
    echo "環境を有効化します..."
    source myenv/bin/activate
else
    echo "Linux が検出されました。"
    echo "環境を有効化します..."
    source myenv/bin/activate
fi

# 基本パッケージのインストール
pip install --upgrade pip
pip install -r requirements.txt

echo "環境チェック用の追加パッケージをインストールしています..."
pip install colorama psutil

# CUDA サポートの確認
if python -c "import torch; print(torch.cuda.is_available())" | grep -q "True"; then
    echo "CUDA が利用可能です。CUDA 対応の PyTorch をインストールします..."
    pip uninstall -y torch torchvision torchaudio
    # PyTorch CUDA バージョンのインストール
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
else
    echo "CUDA が利用できません。CPU 版の PyTorch を使用します。"
    
    # M1/M2 Mac (Apple Silicon) の検出
    if [[ "$OSTYPE" == "darwin"* ]] && [[ $(uname -m) == "arm64" ]]; then
        echo "Apple Silicon (M1/M2) が検出されました。"
        # 特別なインストールは不要（pip でインストールされるパッケージが適切に最適化されている）
    fi
fi

# 必要なディレクトリの確認
mkdir -p audiofile output processed

echo "セットアップが完了しました！"
echo "音声ファイルを 'audiofile' ディレクトリに配置し、以下のコマンドで実行できます:"
echo "python audio_transcribe.py"

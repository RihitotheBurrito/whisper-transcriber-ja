#!/bin/bash
# Whisper モデルのデモ実行

# 環境を有効化
source myenv/bin/activate 2>/dev/null || source myenv/Scripts/activate 2>/dev/null

echo "==== Whisper 音声文字起こしデモ ===="
echo "このスクリプトは、異なるモデルサイズで文字起こしをテストします"

# デモ用の音声ファイルがあるか確認
if [ ! -f "demo_sample.mp3" ]; then
    echo "デモ用の音声ファイルが見つかりません。サンプルファイルをダウンロードします..."
    # サンプル音声のダウンロード（適切なサンプルファイルに置き換えてください）
    if command -v curl &> /dev/null; then
        curl -L "https://github.com/openai/whisper/raw/main/tests/jfk.flac" -o demo_sample.mp3
    elif command -v wget &> /dev/null; then
        wget "https://github.com/openai/whisper/raw/main/tests/jfk.flac" -O demo_sample.mp3
    else
        echo "ダウンロードツール（curl または wget）が見つかりません。"
        echo "サンプル音声ファイルを手動で 'demo_sample.mp3' として保存してください。"
        exit 1
    fi
fi

# サンプル音声を audiofile ディレクトリにコピー
cp demo_sample.mp3 audiofile/

# 小さいモデルでテスト実行
echo -e "\n[1/3] tiny モデルでテスト中（高速だが精度が低い）..."
python audio_transcribe.py --model tiny

# 中間モデルでテスト実行 
echo -e "\n[2/3] base モデルでテスト中（バランスの取れた速度と精度）..."
python audio_transcribe.py --model base

# GPU の検出
if python -c "import torch; print(torch.cuda.is_available())" | grep -q "True"; then
    # GPU あり + より大きなモデルでテスト
    echo -e "\n[3/3] small モデルでテスト中 + CUDA GPU 使用（高精度）..."
    python audio_transcribe.py --model small --device cuda --compute_type float16
else
    # GPU なし
    echo -e "\n[3/3] small モデルでテスト中（高精度だが時間がかかる）..."
    python audio_transcribe.py --model small
fi

echo -e "\nデモが完了しました！output ディレクトリで結果を確認できます。"
echo "実際の使用では、以下のコマンドで各種モデルを指定できます："
echo "  python audio_transcribe.py --model tiny|base|small|medium|large|turbo"
echo "詳細は README.md を参照してください。"

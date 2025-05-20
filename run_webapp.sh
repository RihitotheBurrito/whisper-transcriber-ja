#!/bin/bash

echo "Whisper文字起こしウェブアプリを起動しています..."

# スクリプトのあるディレクトリに移動
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 必要なフォルダを作成
mkdir -p audiofile output processed

# 依存パッケージの確認とインストール
if ! pip list | grep -q "flask"; then
    echo "Flaskをインストールしています..."
    pip install -r requirements.txt
fi

# ウェブアプリを起動
echo "ウェブアプリを起動します（ブラウザが自動的に開きます）"
echo "もしブラウザが自動で開かない場合は、http://localhost:8080 にアクセスしてください"
python app.py 
#!/bin/bash
# Whisper 音声文字起こしツール 環境チェック

echo "Whisper 音声文字起こしツール 環境チェックを実行します..."

# 環境が有効化されているか確認
if [ -f "./myenv/bin/activate" ]; then
    echo "仮想環境を有効化します..."
    source ./myenv/bin/activate
else
    echo "警告: 仮想環境が見つかりません。セットアップを先に実行してください。"
    echo "setup.sh を実行してからこのスクリプトを再度実行してください。"
    read -p "Enterキーを押して終了..."
    exit 1
fi

# 環境チェックスクリプトを実行
python check_environment.py

# 終了
echo ""
echo "環境チェックが完了しました。"
read -p "Enterキーを押して終了..." 

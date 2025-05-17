# GitHub および環境セットアップ完全ガイド

このガイドでは、Whisper 音声文字起こしアプリケーションを GitHub にアップロードし、他のユーザーが簡単に使用できるようにする手順を説明します。

## 1. GitHub リポジトリの作成

1. [GitHub](https://github.com/) にアクセスし、アカウントにログインします
2. 右上の「+」アイコンをクリックし、「New repository」を選択
3. リポジトリ名を入力: `whisper-transcriber-ja`
4. リポジトリの説明を追加: 「OpenAI Whisper を使用した日本語音声文字起こしツール」
5. リポジトリを「Public」に設定
6. 「Initialize this repository with a README」のチェックは**外してください**（既に README.md があるため）
7. 「Create repository」をクリック

## 2. ローカルプロジェクトの準備

すでに適切な `.gitignore` ファイルがあるため、以下のファイルが除外されます:
- 個人的な音声ファイル (`processed/` フォルダ内)
- 出力されたテキストファイル (`output/` フォルダ内)
- Python 仮想環境 (`myenv/` フォルダ)

## 3. Git リポジトリの初期化とプッシュ

### Windows での手順 (Git Bash または WSL)

```bash
# プロジェクトディレクトリに移動
cd "/c/Users/licht/OneDrive - Aoyama Gakuin/myApp/whisper/audioVideoFile"

# Git リポジトリを初期化
git init

# 全てのファイルをステージング
git add .

# 初期コミットを作成
git commit -m "初期コミット: Whisper 音声文字起こしツール"

# メインブランチを設定
git branch -M main

# GitHub リモートリポジトリを追加（URL は作成したリポジトリに合わせて変更）
git remote add origin https://github.com/YOUR_USERNAME/whisper-transcriber-ja.git

# GitHub にプッシュ
git push -u origin main
```

## 4. GitHub リポジトリの設定

リポジトリをアップロードした後、GitHub 上で以下の設定を行います:

1. トピックの追加: Settings > Topics で以下を追加
   - `whisper`
   - `audio-transcription`
   - `speech-to-text`
   - `cuda`
   - `nvidia`
   - `deep-learning`

2. リリースの作成:
   - 「Releases」タブをクリック
   - 「Create a new release」をクリック
   - タグ: `v1.0.0`
   - タイトル: `初回リリース`
   - 説明文に機能と利用方法を簡潔に記載

## 5. 他のユーザーが利用するためのセットアップ手順

他のユーザーがあなたのリポジトリを使用するには、README.md で以下の点を明確に説明する必要があります:

### 必要条件

- Python 3.8 以上
- CUDA 対応 GPU（NVIDIA）※GPU 処理を使用する場合
- CUDA Toolkit 11.2 以上 ※詳細は `CUDA_SETUP.md` を参照

### インストール手順

```bash
# リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/whisper-transcriber-ja.git
cd whisper-transcriber-ja

# セットアップスクリプトを実行
# Windows の場合
setup.bat

# Linux/macOS の場合
chmod +x setup.sh
./setup.sh
```

### 使用方法

```bash
# 音声ファイルを audiofile フォルダに配置

# 文字起こし実行（基本）
python audio_transcribe.py

# CUDA 使用（高速処理）
python audio_transcribe.py --device cuda --compute_type float16

# 大きなモデル使用（高精度）
python audio_transcribe.py --model large
```

## 6. CUDA サポートの設定

CUDA サポートの詳細については、`CUDA_SETUP.md` ファイルを参照するよう README.md に記載してください。このファイルには:

- 必要な NVIDIA ドライバーバージョン
- CUDA Toolkit のインストール方法
- PyTorch と CUDA の互換性
- トラブルシューティング

が詳細に記載されています。

## 注意事項

- 初期コミット時に大きなバイナリファイルや個人データがリポジトリに含まれていないことを確認してください
- `git status` コマンドで、大きなファイルや個人データが `.gitignore` によって除外されていることを確認してください

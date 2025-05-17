# GitHub にアップロードする手順

以下の手順に従って、このプロジェクトを GitHub にアップロードしてください。

## 準備

1. GitHub アカウントを持っていない場合は、[GitHub](https://github.com/) で作成してください。
2. リポジトリを作成: GitHub のウェブサイトで「New repository」ボタンをクリックし、リポジトリ名を入力します（例: `whisper-transcription`）。

## コマンドラインでのアップロード

以下のコマンドを順番に実行してリポジトリをアップロードします：

```bash
# 現在のディレクトリで Git リポジトリを初期化
git init

# すべてのファイルをステージングに追加
git add .

# 最初のコミットを作成
git commit -m "初期コミット: Whisper 音声文字起こしツール"

# メインブランチを設定（新しい Git の場合）
git branch -M main

# GitHub リモートリポジトリを追加（URLは実際に作成したリポジトリのものに置き換えてください）
git remote add origin https://github.com/[your-username]/whisper-transcription.git

# リモートリポジトリにプッシュ
git push -u origin main
```

## GitHub Desktop を使用する場合

1. [GitHub Desktop](https://desktop.github.com/) をインストールして起動
2. 「File」→「Add local repository」を選択し、このプロジェクトのフォルダを選択
3. 「Publish repository」ボタンをクリックし、リポジトリ名を入力
4. 「Publish repository」ボタンをクリックして完了

## リポジトリの設定（オプション）

リポジトリをアップロードした後、GitHub 上で以下の設定を行うと良いでしょう：

1. README.md の内容が正しく表示されていることを確認
2. リポジトリの「About」セクションで説明とトピックを追加
   - Topics: whisper, audio-transcription, speech-to-text, cuda など
3. リリースを作成: 「Releases」→「Create a new release」
   - タグ: v1.0.0
   - タイトル: 初回リリース
   - 説明: 初期バージョンのリリースノート

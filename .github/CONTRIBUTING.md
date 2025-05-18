# 貢献ガイドライン

Whisper 日本語音声文字起こしツール (whisper-transcriber-ja) にご関心をお寄せいただきありがとうございます。このプロジェクトへの貢献を歓迎いたします。このドキュメントでは、貢献のプロセスを円滑に進めるためのガイドラインを提供します。

## 貢献の方法

以下のような方法でプロジェクトに貢献できます：

1. バグの報告
2. 新機能のリクエスト
3. コードの改善
4. ドキュメントの改善
5. テストの追加・改善
6. その他プロジェクトの価値を高める活動

## 開発環境のセットアップ

1. リポジトリをフォークしてクローンします
```bash
git clone https://github.com/[your-username]/whisper-transcriber-ja.git
cd whisper-transcriber-ja
```

2. 仮想環境を作成して依存関係をインストールします
```bash
python -m venv myenv
source myenv/bin/activate  # macOS/Linux
# または
myenv\Scripts\activate     # Windows

pip install -r requirements.txt
```

3. GPUサポートが必要な場合は、適切なバージョンのPyTorch（CUDA対応版）をインストールします
```bash
# CUDA 11.8 の場合
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Issue作成のガイドライン

Issueを作成する際には、以下の点に注意してください：

1. 同様の問題が既に報告されていないか確認する
2. 問題を明確に説明する
3. 問題の再現手順を詳細に記載する
4. 可能であれば、スクリーンショットやエラーメッセージを添付する
5. 使用している環境（OS、Pythonバージョン、使用しているモデルなど）を記載する

## Pull Requestのプロセス

1. 作業前に最新の`main`ブランチから新しいブランチを作成してください
```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

2. 変更を加え、適切なコミットメッセージを付けてコミットします
```bash
git add .
git commit -m "Add: 新機能の追加" # または "Fix: バグの修正" など
```

3. 変更をフォークしたリポジトリにプッシュします
```bash
git push origin feature/your-feature-name
```

4. GitHubウェブサイトからPull Requestを作成します

5. Pull Requestのタイトルと説明には、変更内容を明確に記載してください

## コーディング規約

- [PEP 8](https://pep8.org/) - Pythonのコーディングスタイルガイドに従ってください
- ドキュメント文字列（docstrings）を使用して関数やクラスを文書化してください
- コードには適切なコメントを追加してください
- 新しい機能には可能な限りテストを追加してください

## テスト

変更を加えた後は、既存のテストが通ることを確認してください。新しい機能を追加した場合は、対応するテストも追加してください。

## ドキュメント

コードやAPIに変更を加えた場合は、対応するドキュメントも更新してください。これには、README.md、ドキュメントファイル、およびコード内のコメントが含まれます。

## コミュニティ

質問やサポートが必要な場合は、Issueを作成するか、プロジェクトのディスカッションフォーラムを使用してください。

## ライセンス

このプロジェクトに貢献することで、あなたの貢献がプロジェクトと同じライセンスの下で公開されることに同意したものとみなします。

## 謝辞

あなたの貢献に感謝します！プロジェクトの改善に協力してくださる全ての方々のおかげで、このツールはより良いものになります。

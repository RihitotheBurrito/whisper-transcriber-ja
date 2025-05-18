# Whisper 日本語音声文字起こしツール (whisper-transcriber-ja)

このアプリケーションは、OpenAI の Whisper モデルを使用して、音声ファイルから自動的にテキストを生成するツールです。日本語音声の文字起こしに最適化されています。

## 機能

- 複数の音声フォーマット（MP3、WAV、M4A、FLAC、AAC、OGG）に対応
- 複数のWhisperモデル（tiny、base、small、medium、large、turbo）を選択可能
- GPU（CUDA）サポートによる高速処理
- バッチ処理により複数ファイルを一括で処理
- 処理済みファイルは自動的に別フォルダに移動

## インストール方法

### 必要条件

- Python 3.8 以上
- CUDA サポートに必要なもの（GPU で実行する場合）:
  - NVIDIA GPU（CUDA 対応）
  - NVIDIA ドライバー（450.80.02 以上推奨）
  - CUDA Toolkit 11.2 以上
  - 詳細は [`CUDA_SETUP.md`](CUDA_SETUP.md) を参照してください

### インストール手順

1. リポジトリをクローン:

```bash
git clone https://github.com/[your-username]/whisper-transcriber-ja.git
cd whisper-transcriber-ja/audioVideoFile
```

2. 仮想環境の作成（オプションですが推奨）:

```bash
# venv を使用する場合
python -m venv myenv
# Windows での有効化
myenv\Scripts\activate
# macOS/Linux での有効化
source myenv/bin/activate
```

3. 依存パッケージのインストール:

```bash
pip install -r requirements.txt
```

4. GPU サポートのための PyTorch（CUDA 対応版）のインストール:

```bash
# CUDA 11.8 の場合
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 使用方法

1. `audiofile` ディレクトリに音声ファイルを配置

2. スクリプトを実行:

```bash
python audio_transcribe.py
```

3. 追加のオプション:

```bash
# モデルサイズを指定（tiny, base, small, medium, large, turbo）
python audio_transcribe.py --model medium

# 言語を指定（デフォルトは日本語）
python audio_transcribe.py --language en

# GPU 使用を指定
python audio_transcribe.py --device cuda

# 計算タイプを指定（float16 は GPU 使用時に高速）
python audio_transcribe.py --device cuda --compute_type float16
```

## 環境チェック

CUDA や Whisper の設定が正しく行われているか確認するには、環境チェックスクリプトを実行します：

```bash
# Windows の場合
check_environment.bat

# Linux/macOS の場合
chmod +x check_environment.sh
./check_environment.sh
```

このスクリプトは以下の項目を確認します：
- Python バージョン
- システム情報（メモリ、プロセッサ）
- CUDA の利用可能性とバージョン
- GPU メモリと推奨 Whisper モデル
- 簡易ベンチマーク
- システムに最適な実行コマンドの提案

## ディレクトリ構成

- `audiofile/`: 文字起こしする音声ファイルを配置
- `output/`: 文字起こし結果のテキストファイルが保存される
- `processed/`: 処理済みの音声ファイルが移動される

## 注意事項

- 大きなモデル（large）を使用する場合は、十分なメモリ（RAM）が必要です
- GPU を使用すると処理が大幅に高速化されます

## ライセンス

このプロジェクトは [MIT ライセンス](LICENSE) の下で公開されています。

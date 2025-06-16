# Whisper 日本語音声文字起こしツール (whisper-transcriber-ja)

このアプリケーションは、OpenAI の Whisper モデルを使用して、音声ファイルから自動的にテキストを生成するツールです。日本語音声の文字起こしに最適化されています。

For an English version of this document, see [README_EN.md](README_EN.md).

## 機能

- 複数の音声フォーマット（MP3、WAV、M4A、FLAC、AAC、OGG）に対応
- 複数のWhisperモデル（tiny、base、small、medium、large、turbo）を選択可能
- GPU（CUDA）サポートによる高速処理
- バッチ処理により複数ファイルを一括で処理
- 処理済みファイルは自動的に別フォルダに移動
- **ウェブブラウザによる操作が可能なGUIインターフェース**
- **リアルタイム進捗状況表示機能**

## インストール方法

### 必要条件

- Python 3.8 以上
- CUDA サポートに必要なもの（GPU で実行する場合）:
  - NVIDIA GPU（CUDA 対応）
  - NVIDIA ドライバー（450.80.02 以上推奨）
  - CUDA Toolkit 11.2 以上
  - 詳細は [`CUDA_SETUP.md`](CUDA_SETUP.md) を参照してください

### 簡単セットアップ（初心者向け）

プログラミングの経験が少ない方でも簡単にセットアップできるスクリプトを用意しています。これらのスクリプトは、必要な環境を自動的に構築します。

#### Windows での簡単セットアップ

1. このリポジトリをダウンロードして解凍します
2. **setup.bat** ファイルをダブルクリックします
3. セットアップが自動的に実行され、以下の処理が行われます：
   - Python 仮想環境の作成
   - 必要なパッケージのインストール
   - CUDA が利用可能な場合は、CUDA 対応の PyTorch をインストール
   - 必要なフォルダの作成

#### macOS / Linux での簡単セットアップ

1. このリポジトリをダウンロードして解凍します
2. ターミナルを開き、解凍したフォルダに移動します
3. 以下のコマンドでセットアップスクリプトを実行可能にします：
   ```bash
   chmod +x setup.sh
   ```
4. 次のコマンドでセットアップを実行します：
   ```bash
   ./setup.sh
   ```
5. セットアップスクリプトは以下の処理を自動的に行います：
   - Python 仮想環境の作成と有効化
   - 必要なパッケージのインストール
   - お使いのコンピュータに合わせた最適な設定の適用
   - 必要なフォルダの作成

### 環境チェック（推奨）

セットアップ後、あなたのシステムが最適な状態で動作するかを確認するためのチェックスクリプトも提供しています。

#### Windows での環境チェック

1. **check_environment.bat** ファイルをダブルクリックします
2. スクリプトが以下の項目を自動的にチェックします：
   - Python のバージョン
   - システム情報（メモリ、プロセッサ）
   - GPU の有無と性能
   - 最適なモデルサイズの推奨
   - あなたのシステムに最適な実行コマンドを表示

#### macOS / Linux での環境チェック

1. ターミナルを開き、解凍したフォルダに移動します
2. 以下のコマンドでチェックスクリプトを実行可能にします：
   ```bash
   chmod +x check_environment.sh
   ```
3. 次のコマンドで環境チェックを実行します：
   ```bash
   ./check_environment.sh
   ```

### 手動でのインストール手順（上級者向け）

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

### デモの実行（初心者向け）

サンプル音声を使って簡単にツールを試せるデモスクリプトを用意しています。

#### Windows でのデモ実行

1. **run_demo.bat** ファイルをダブルクリックします
2. デモが自動的に実行され、サンプル音声の文字起こしが行われます
3. 結果は `output` フォルダに保存されます

#### macOS / Linux でのデモ実行

1. ターミナルを開き、解凍したフォルダに移動します
2. 以下のコマンドでデモスクリプトを実行可能にします：
   ```bash
   chmod +x run_demo.sh
   ```
3. 次のコマンドでデモを実行します：
   ```bash
   ./run_demo.sh
   ```

### コマンドライン版の実行

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

### ウェブブラウザGUI版の実行

ブラウザインターフェースでの操作を希望する場合は、以下のコマンドを実行します：

```bash
# Windows の場合
run_webapp.bat

# Linux/macOS の場合
chmod +x run_webapp.sh
./run_webapp.sh
```

ブラウザで `http://localhost:8080` にアクセスするとウェブインターフェースが表示されます。

#### ウェブGUIの使い方

1. **ファイルのアップロード**
   - 左側の「音声ファイルのアップロード」セクションで「ファイルを選択」ボタンをクリックし、音声ファイルを選択
   - 「アップロード」ボタンをクリックして音声ファイルをアップロード
   - アップロードした音声ファイルは「処理待ちファイル」セクションに表示されます

2. **文字起こしの実行**
   - 右側の「文字起こし実行」セクションで処理したいファイルを選択
   - 必要に応じてモデルのサイズ、言語、計算精度を設定
     - tiny: 処理が最も速いが精度は低い（小さな音声ファイル向け）
     - base: バランスの取れた速度と精度（デフォルト、通常の用途に推奨）
     - small/medium: より高い精度だが処理時間が長い
     - large: 最高精度だが処理時間が非常に長い（多くのメモリが必要）
   - 「文字起こし実行」ボタンをクリックして処理を開始

3. **進捗状況の確認**
   - 処理中は、リアルタイムで進捗状況がプログレスバーに表示されます
   - 現在の処理状態、経過時間、処理中のファイル名が表示されます
   - モデルのロード中や処理中の各ステップの状況が分かります

4. **結果の確認とダウンロード**
   - 処理が完了すると、「文字起こし結果」セクションに出力ファイルが表示されます
   - ダウンロードアイコンをクリックすることでテキストファイルをダウンロード可能
   - 不要になった結果は削除アイコンで削除できます

5. **ファイル管理**
   - 処理済みのファイルは自動的に「processed」フォルダに移動します
   - 処理待ちのファイルや出力ファイルはインターフェースから直接削除可能

#### 注意事項

- 処理中は別のファイルの処理を開始できません（1つのファイルの処理が完了するまで待つ必要があります）
- 大きなファイルや高品質なモデル（medium, large）を使用する場合は処理に時間がかかります
- Apple Silicon（M1/M2/M3）チップ搭載のMacでは、MPSアクセラレーションがWhisperと互換性がないため、CPUを使用して処理されます（より時間がかかります）

主な機能：
- ドラッグ＆ドロップによる音声ファイルのアップロード
- モデルや言語などの設定をブラウザから簡単に変更
- リアルタイム進捗状況表示でいつ完了するか把握可能
- 文字起こし結果のダウンロード
- ファイル管理機能（未処理/処理済みファイルの一覧表示と削除）

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
- `templates/`: ウェブインターフェース用のHTMLテンプレート
- `static/`: ウェブインターフェース用の静的ファイル（CSS、JS）

## 注意事項

- 大きなモデル（large）を使用する場合は、十分なメモリ（RAM）が必要です
- GPU を使用すると処理が大幅に高速化されます
- ウェブインターフェースはデフォルトでローカルネットワークのみからアクセス可能です

## ガイドとチュートリアル

プロジェクトに関する詳細なガイドやチュートリアルは以下のファイルで提供されています：

- [CUDA セットアップガイド](CUDA_SETUP.md) - NVIDIA GPU で CUDA を設定する方法
- [GitHub 完全ガイド](GITHUB_COMPLETE_GUIDE.md) - プロジェクトの GitHub 利用に関する包括的ガイド
- [GitHub アップロード手順](GITHUB_UPLOAD.md) - コードを GitHub にアップロードする方法

## ライセンス

このプロジェクトは [MIT ライセンス](LICENSE) の下で公開されています。

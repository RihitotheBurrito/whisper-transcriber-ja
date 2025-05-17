# CUDA 環境セットアップガイド

このガイドでは、Whisper 音声文字起こしツールを CUDA 対応環境で使用するための準備手順を説明します。

## CUDA 環境の必要条件

### ハードウェア要件
- NVIDIA GPU（CUDA 対応のモデル）
  - GeForce GTX 1060 以上推奨
  - RTX シリーズ推奨（Tensor コア搭載モデルはさらに高速）

### ソフトウェア要件
1. **NVIDIA ドライバー**
   - 最低バージョン: 450.80.02 以上
   - 推奨バージョン: 最新の安定版

2. **CUDA Toolkit**
   - バージョン 11.2 以上（11.8 推奨）

3. **cuDNN (CUDA Deep Neural Network library)**
   - CUDA Toolkit と互換性のあるバージョン

## インストール手順

### 1. NVIDIA ドライバーのインストール

#### Windows
1. [NVIDIA ドライバーダウンロードページ](https://www.nvidia.co.jp/Download/index.aspx?lang=jp) にアクセス
2. お使いの GPU モデルに合ったドライバーを選択してダウンロード
3. ダウンロードしたインストーラーを実行し、画面の指示に従ってインストール

#### Linux (Ubuntu)
```bash
sudo apt update
sudo apt install nvidia-driver-530  # バージョン番号は変更される可能性あり
sudo reboot
```

### 2. CUDA Toolkit のインストール

#### Windows
1. [NVIDIA CUDA ダウンロードページ](https://developer.nvidia.com/cuda-downloads) にアクセス
2. お使いの OS に合ったバージョンをダウンロード
3. インストーラーを実行し、「Express」または「Custom」インストールを選択
4. インストール完了後、システムを再起動

#### Linux (Ubuntu)
```bash
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run
```

### 3. 環境変数の設定

#### Windows
1. システム環境変数に以下を追加:
   - `CUDA_HOME`: C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8
   - `PATH`: %CUDA_HOME%\bin と %CUDA_HOME%\libnvvp を追加

#### Linux (Ubuntu)
```bash
echo 'export PATH=/usr/local/cuda-11.8/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### 4. インストールの確認

```bash
# CUDA バージョンの確認
nvcc --version

# GPU の認識確認
nvidia-smi
```

## PyTorch と CUDA の互換性

PyTorch のバージョンと CUDA の互換性は重要です。このプロジェクトでは以下の組み合わせを推奨:

| PyTorch バージョン | 推奨 CUDA バージョン |
|--------------------|----------------------|
| 2.0.0 以上         | CUDA 11.7 / 11.8     |
| 1.13.x             | CUDA 11.6 / 11.7     |
| 1.12.x             | CUDA 11.3 / 11.6     |

PyTorch のインストールは `setup.bat` または `setup.sh` スクリプト内で自動的に行われますが、特定のバージョンが必要な場合は以下のコマンドで手動インストール可能です:

```bash
# CUDA 11.8 用 PyTorch のインストール例
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## トラブルシューティング

### よくある問題と解決策

1. **「CUDA が利用できません」というエラーが表示される**
   - NVIDIA ドライバーが正しくインストールされているか確認
   - 環境変数が正しく設定されているか確認
   - `nvidia-smi` コマンドが正常に動作するか確認

2. **PyTorch が CUDA を認識しない**
   - PyTorch を再インストール: `pip uninstall torch torchvision torchaudio` の後、CUDA 対応バージョンをインストール
   - CUDA と PyTorch のバージョンの互換性を確認

3. **メモリ不足エラー**
   - より小さなモデル（medium や small）を使用
   - バッチサイズを小さくする: `python audio_transcribe.py --batch_size 8`
   - コンピュートタイプを float16 に変更: `python audio_transcribe.py --compute_type float16`

## 参考リンク

- [NVIDIA CUDA インストールガイド](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html)
- [PyTorch インストールガイド](https://pytorch.org/get-started/locally/)
- [Whisper GitHub リポジトリ](https://github.com/openai/whisper)

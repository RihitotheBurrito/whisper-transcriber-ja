@echo off
REM Whisper 音声文字起こしツールのセットアップスクリプト (Windows用)

echo Whisper 音声文字起こしツールのセットアップを開始します...

REM venv 環境を作成
python -m venv myenv

REM 環境を有効化
call myenv\Scripts\activate

REM 基本パッケージのインストール
pip install --upgrade pip
pip install -r requirements.txt

echo 環境チェック用の追加パッケージをインストールしています...
pip install colorama psutil

REM CUDA サポートの確認
python -c "import torch; print('CUDA_AVAILABLE=' + str(torch.cuda.is_available()))" > temp.txt
findstr "CUDA_AVAILABLE=True" temp.txt > nul
if %errorlevel% equ 0 (
    echo CUDA が利用可能です。CUDA 対応の PyTorch をインストールします...
    pip uninstall -y torch torchvision torchaudio
    REM PyTorch CUDA バージョンのインストール
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
) else (
    echo CUDA が利用できません。CPU 版の PyTorch を使用します。
)
del temp.txt

REM 必要なディレクトリの確認
if not exist audiofile mkdir audiofile
if not exist output mkdir output
if not exist processed mkdir processed

echo セットアップが完了しました！
echo 音声ファイルを 'audiofile' ディレクトリに配置し、以下のコマンドで実行できます:
echo python audio_transcribe.py

REM 環境を維持したままプロンプトを表示
cmd /k

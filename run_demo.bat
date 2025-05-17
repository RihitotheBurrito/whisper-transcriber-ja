@echo off
REM Whisper モデルのデモ実行 (Windows用)

REM 環境を有効化
call myenv\Scripts\activate

echo ==== Whisper 音声文字起こしデモ ====
echo このスクリプトは、異なるモデルサイズで文字起こしをテストします

REM デモ用の音声ファイルがあるか確認
if not exist demo_sample.mp3 (
    echo デモ用の音声ファイルが見つかりません。サンプルファイルをダウンロードします...
    REM サンプル音声のダウンロード
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/openai/whisper/raw/main/tests/jfk.flac' -OutFile 'demo_sample.mp3'"
    if %errorlevel% neq 0 (
        echo ダウンロードに失敗しました。
        echo サンプル音声ファイルを手動で 'demo_sample.mp3' として保存してください。
        exit /b 1
    )
)

REM サンプル音声を audiofile ディレクトリにコピー
copy demo_sample.mp3 audiofile\

REM 小さいモデルでテスト実行
echo.
echo [1/3] tiny モデルでテスト中（高速だが精度が低い）...
python audio_transcribe.py --model tiny

REM 中間モデルでテスト実行 
echo.
echo [2/3] base モデルでテスト中（バランスの取れた速度と精度）...
python audio_transcribe.py --model base

REM GPU の検出
python -c "import torch; print('CUDA_AVAILABLE=' + str(torch.cuda.is_available()))" > temp.txt
findstr "CUDA_AVAILABLE=True" temp.txt > nul
if %errorlevel% equ 0 (
    REM GPU あり + より大きなモデルでテスト
    echo.
    echo [3/3] small モデルでテスト中 + CUDA GPU 使用（高精度）...
    python audio_transcribe.py --model small --device cuda --compute_type float16
) else (
    REM GPU なし
    echo.
    echo [3/3] small モデルでテスト中（高精度だが時間がかかる）...
    python audio_transcribe.py --model small
)
del temp.txt

echo.
echo デモが完了しました！output ディレクトリで結果を確認できます。
echo 実際の使用では、以下のコマンドで各種モデルを指定できます：
echo   python audio_transcribe.py --model tiny^|base^|small^|medium^|large^|turbo
echo 詳細は README.md を参照してください。

REM 環境を維持したままプロンプトを表示
cmd /k

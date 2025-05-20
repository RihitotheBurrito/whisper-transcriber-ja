@echo off
setlocal

echo Whisper文字起こしウェブアプリを起動しています...

rem 必要なフォルダを作成
if not exist audiofile mkdir audiofile
if not exist output mkdir output
if not exist processed mkdir processed

rem 依存パッケージの確認とインストール
pip list | findstr "flask" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Flaskをインストールしています...
    pip install -r requirements.txt
)

rem ウェブアプリを起動
echo ウェブアプリを起動します（localhost:8080）
echo ブラウザで http://localhost:8080 を開いてください
python app.py

endlocal 
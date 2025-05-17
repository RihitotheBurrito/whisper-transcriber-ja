@echo off
REM Whisper 音声文字起こしツール 環境チェック

echo Whisper 音声文字起こしツール 環境チェックを実行します...

REM 環境が有効化されているか確認
if exist myenv\Scripts\activate (
    echo 仮想環境を有効化します...
    call myenv\Scripts\activate
) else (
    echo 警告: 仮想環境が見つかりません。セットアップを先に実行してください。
    echo setup.bat を実行してからこのスクリプトを再度実行してください。
    pause
    exit /b
)

REM 環境チェックスクリプトを実行
python check_environment.py

REM 終了
echo.
echo 環境チェックが完了しました。
pause

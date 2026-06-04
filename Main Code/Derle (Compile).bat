@echo off
echo Compiling code...
pip install pyinstaller
pip install Pillow
py -m PyInstaller --noconsole --onefile --clean --icon="logo.ico" --add-data "key.jpg;." --add-data "bsod.jpg;." --add-data "music.wav;." main.py
echo.
echo.
echo.
echo Job Done!
pause >nul
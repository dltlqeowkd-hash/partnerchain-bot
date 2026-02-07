@echo off
cd /d "%~dp0"
echo Building MultiBot EXE...
pyinstaller --noconfirm --onefile --windowed --name "MultiBot" --add-data "random_data.py;." multi_bot.py
echo Build Complete. Check the 'dist' folder.
pause

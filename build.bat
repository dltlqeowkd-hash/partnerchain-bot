@echo off
cd /d "%~dp0"
echo Building Project...
python build_release.py
pause

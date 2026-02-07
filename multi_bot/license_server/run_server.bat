@echo off
cd /d "%~dp0"
echo Starting License Server...
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
pause

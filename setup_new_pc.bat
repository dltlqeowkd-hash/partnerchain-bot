@echo off
echo ===================================================
echo [Migration] Installing all required libraries...
echo ===================================================

REM 1. Client Dependencies
echo [1/2] Installing Client libraries...
python -m pip install selenium webdriver-manager requests pyinstaller

REM 2. File Server Dependencies
echo [2/2] Installing Server libraries...
cd license_server
python -m pip install -r requirements.txt
cd ..

echo.
echo ===================================================
echo Use 'start_launcher.bat' to run the Client.
echo Use 'license_server/run_server.bat' to run the Server.
echo ===================================================
pause

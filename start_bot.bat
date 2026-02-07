@echo off
chcp 65001 >nul
echo ========================================================
echo  네이버 쇼핑 봇 자동 실행기
echo ========================================================

echo [1/2] 크롬 브라우저를 디버깅 모드로 실행합니다...
REM 크롬 실행 (기존 창이 있다면 무시될 수 있음)
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"

echo.
echo 크롬이 켜질 때까지 3초간 대기합니다...
timeout /t 3 /nobreak >nul

echo.
echo [2/2] 봇 프로그램을 실행합니다...
python final_bot.py

echo.
echo 프로그램이 종료되었습니다. 아무 키나 누르면 닫힙니다.
pause

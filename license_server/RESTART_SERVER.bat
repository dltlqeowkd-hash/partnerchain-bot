@echo off
chcp 65001 >nul
title 라이선스 서버 재시작

echo ========================================
echo   🔄 라이선스 서버 완전 재시작
echo ========================================
echo.
echo 1. 기존 실행 중인 서버 프로세스를 모두 종료합니다.
echo 2. 서버를 새로 시작합니다.
echo.
pause

echo [1/2] Python 서버 프로세스 종료 중...
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

echo [2/2] 라이선스 서버 시작 중...
cd /d "D:\bot\license_server"
start "License Server" cmd /k "python main.py"

echo.
echo ✅ 서버가 새 창에서 시작되었습니다.
echo.
echo [다음 단계]
echo 1. 새로 열린 서버 창에서 "Application startup complete" 메시지 확인
echo 2. D:\bot\multi_bot\debug_license.py 실행하여 memo 필드 확인
echo 3. 확인되면 봇 재실행
echo.
pause

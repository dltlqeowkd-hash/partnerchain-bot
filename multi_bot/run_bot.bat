@echo off
chcp 65001 >nul
echo ========================================================
echo  네이버 쇼핑/블로그 통합 봇 (Commercial Ver)
echo ========================================================
echo.
echo [1/2] 라이선스 확인 및 업데이트 체크...
echo.

REM 파이썬 스크립트 실행
python multi_bot.py

echo.
echo 프로그램이 종료되었습니다.
pause

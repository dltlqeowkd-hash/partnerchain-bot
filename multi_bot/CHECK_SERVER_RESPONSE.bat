@echo off
chcp 65001 >nul
title 서버 응답 확인

echo ========================================
echo   🔍 서버가 memo를 반환하는지 확인
echo ========================================
echo.

cd /d "D:\bot\multi_bot"
python debug_license.py

echo.
echo ========================================
echo 위 결과에서 "memo: 'ABC'" 라고 나오면 성공!
echo "memo: None" 이면 서버 재시작 필요
echo ========================================
pause

@echo off
chcp 65001 >nul
title 라이선스 초기화 및 재인증

echo ========================================
echo   🔄 라이선스 초기화 스크립트
echo ========================================
echo.
echo [주의] 이 스크립트는 기존 인증 정보를 삭제합니다.
echo 실행 후 새로운 시리얼 키(daowiz Inc.)로 재인증해야 합니다.
echo.
pause

cd /d "D:\bot\multi_bot"

if exist "license.dat" (
    del "license.dat"
    echo ✅ 기존 인증 정보 삭제 완료
) else (
    echo ℹ️ 삭제할 파일 없음
)

echo.
echo ========================================
echo  완료! 이제 봇을 실행하면 새 키를 입력할 수 있습니다.
echo ========================================
echo.
echo [다음 단계]
echo 1. 서버에서 "daowiz Inc." 메모가 있는 키를 복사
echo 2. run_bot.bat 실행
echo 3. 팝업창에 키 입력
echo.
pause

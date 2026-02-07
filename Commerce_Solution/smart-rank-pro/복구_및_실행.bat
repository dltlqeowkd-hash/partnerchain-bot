@echo off
chcp 65001
echo ==========================================
echo  Smart Rank Pro 복구 및 실행 도구
echo ==========================================
echo.
echo 1. 기존에 잘못 설치된 파일(node_modules)을 정리합니다...
if exist "node_modules" (
    rmdir /s /q "node_modules"
    echo  - 삭제 완료
) else (
    echo  - 삭제할 파일이 없습니다 (깨끗한 상태)
)

echo.
echo 2. 필요한 프로그램을 설치합니다 (npm install)...
echo    시간이 조금 걸릴 수 있습니다. 잠시만 기다려주세요.
call npm install

echo.
echo 3. 프로그램을 실행합니다 (npm run dev)...
echo    실행 후 인터넷 창에서 http://localhost:3000 으로 접속하세요.
echo ==========================================
echo.
call npm run dev

pause

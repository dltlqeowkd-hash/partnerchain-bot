@echo off
chcp 65001 >nul
echo ========================================================
echo  PartnerChain Admin Tool Build Script
echo ========================================================
echo.
echo [1/3] PyInstaller 설치 확인...
pip install pyinstaller pyperclip

echo.
echo [2/3] 관리자 도구(key_gen_gui.py) 빌드 중...
pyinstaller --noconfirm --onefile --windowed --name "PartnerChain_KeyGen_v1.0" --icon "NONE" key_gen_gui.py

echo.
echo [3/3] 빌드 완료! dist 폴더를 확인하세요.
echo.
pause

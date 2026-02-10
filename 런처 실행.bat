@echo off
chcp 65001 >nul
title 봇 런처

echo ================================
echo   봇 런처 시작
echo ================================
echo.

cd /d "%~dp0"
python launcher.py

if errorlevel 1 (
    echo.
    echo ================================
    echo   오류 발생!
    echo ================================
    echo.
    pause
)

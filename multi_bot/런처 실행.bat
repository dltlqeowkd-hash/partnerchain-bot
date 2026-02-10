@echo off
chcp 65001 >nul
title 네이버 쇼핑 봇 런처

echo ================================
echo   네이버 쇼핑 봇 런처 시작
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

@echo off
title Nandha Engineering College - College Complaint Management System
echo ======================================================================
echo    Nandha Engineering College - College Complaint System
echo ======================================================================
echo.

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Using system Python...
    python app.py
) else (
    if exist "C:\Users\sasis\Downloads\AI 2\python_env\python.exe" (
        echo [OK] Using Python environment from C:\Users\sasis\Downloads\AI 2\python_env...
        "C:\Users\sasis\Downloads\AI 2\python_env\python.exe" app.py
    ) else (
        echo [ERROR] Python not found. Please install Python or set it in your PATH.
        pause
    )
)
pause

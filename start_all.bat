@echo off
echo ======================================================
echo   Smart News Marathi - 24x7 Broadcast Starter
echo ======================================================
echo.

:: Try to find python - first try direct 'python', then 'py'
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_EXE=python
) else (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_EXE=py
    ) else (
        echo ERROR: Python not found! Please install Python 3.
        pause
        exit /b 1
    )
)

echo Using Python: %PYTHON_EXE%
echo.

:: 1. Ensure font assets exist
echo Ensuring font assets...
%PYTHON_EXE% "%~dp0backend\ensure_font.py"

timeout /t 2 >nul

:: 2. Start Backend
echo Starting Backend Service...
start "SNM-BACKEND" cmd /k "cd /d %~dp0backend && %PYTHON_EXE% main.py"

echo Waiting 8 seconds for backend to initialize...
timeout /t 8 >nul

:: 3. Start Stream Engine
echo Starting Stream Engine...
start "SNM-STREAM-ENGINE" cmd /k "cd /d %~dp0stream-engine && %PYTHON_EXE% streamer.py"

echo.
echo All services started in separate windows.
echo Check the windows for detailed logs.
pause

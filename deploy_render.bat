@echo off
setlocal
cd /d "%~dp0"
echo ===========================================
echo  VartaPravah Render Deployment Assistant
echo ===========================================
echo.
echo This script will help you push your changes to GitHub.
echo Current Directory: %CD%
echo.

set /p confirm="Continue with Git Push? (y/n): "
if /i "%confirm%" neq "y" (
    echo Deployment cancelled.
    pause
    exit /b
)

echo.
echo [1/3] Adding files to Git...
git add .

echo [2/3] Committing changes...
git commit -m "fix: render blueprint error and git setup"

echo [3/3] Pushing to GitHub (main branch)...
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Git push failed. 
    echo Possible reasons:
    echo 1. You haven't logged in to GitHub on this machine.
    echo 2. The repository doesn't exist yet.
    echo 3. Internet connection issue.
    echo.
    pause
    exit /b
)

echo.
echo ===========================================
echo  SUCCESS: Code pushed to GitHub!
echo ===========================================
echo.
echo Final Steps on Render:
echo 1. Go to: https://dashboard.render.com/blueprints
echo 2. Click "New Blueprint Instance"
echo 3. Select your "Smart-News-Marathi" repository
echo 4. Set the following secrets when prompted:
echo    - GEMINI_API_KEY
echo    - DATABASE_URL
echo    - YOUTUBE_STREAM_KEY
echo.
pause

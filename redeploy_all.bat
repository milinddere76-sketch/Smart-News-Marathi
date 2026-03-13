@echo off
set FLY=C:\Users\Priyansh Dere\.fly\bin\flyctl.exe

echo =============================================
echo  STEP 1: Deploying BACKEND
echo =============================================
cd /d "d:\Apps\Smart News Marathi\backend"
"%FLY%" deploy --remote-only
if %ERRORLEVEL% NEQ 0 (
    echo BACKEND DEPLOY FAILED! Check errors above.
    pause
    exit /b 1
)

echo =============================================
echo  STEP 2: Deploying STREAM ENGINE
echo =============================================
cd /d "d:\Apps\Smart News Marathi\stream-engine"
"%FLY%" deploy --remote-only
if %ERRORLEVEL% NEQ 0 (
    echo STREAM ENGINE DEPLOY FAILED! Check errors above.
    pause
    exit /b 1
)

echo =============================================
echo  STEP 3: Deploying FRONTEND
echo =============================================
cd /d "d:\Apps\Smart News Marathi\frontend"
"%FLY%" deploy --remote-only
if %ERRORLEVEL% NEQ 0 (
    echo FRONTEND DEPLOY FAILED! Check errors above.
    pause
    exit /b 1
)

echo =============================================
echo  ALL DONE!
echo  Backend:  https://snm-be-priyansh-dere.fly.dev
echo  Frontend: https://snm-fe-priyansh-dere.fly.dev
echo =============================================
pause

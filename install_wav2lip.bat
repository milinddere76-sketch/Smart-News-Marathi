@echo off
echo ============================================
echo Installing Wav2Lip for Smart News Marathi
echo ============================================

set WAV2LIP_DIR=D:\Wav2Lip
set VENV=D:\Apps\Smart News Marathi\backend\venv\Scripts

REM Step 1: Clone Wav2Lip
if exist "%WAV2LIP_DIR%" (
    echo Wav2Lip already cloned at %WAV2LIP_DIR%
) else (
    echo Cloning Wav2Lip from GitHub...
    git clone https://github.com/Rudrabha/Wav2Lip.git %WAV2LIP_DIR%
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: git clone failed. Make sure git is installed.
        pause
        exit /b 1
    )
    echo Cloned successfully.
)

REM Step 2: Create checkpoints folder
if not exist "%WAV2LIP_DIR%\checkpoints" (
    mkdir "%WAV2LIP_DIR%\checkpoints"
    echo Created checkpoints folder.
)

REM Step 3: Install Wav2Lip Python dependencies into backend venv
echo Installing Wav2Lip Python dependencies...
"%VENV%\pip.exe" install librosa==0.9.2 numpy==1.23.5 opencv-python batch_face
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Some packages may have failed. Check output above.
)

echo.
echo ============================================
echo NEXT STEP (MANUAL):
echo Download wav2lip_gan.pth from:
echo https://drive.google.com/file/d/1P4ifERyg9UMOkTl1MsEMW9DmknMd9jqf/view
echo Place it at: D:\Wav2Lip\checkpoints\wav2lip_gan.pth
echo ============================================
pause

@echo off
echo =============================================
echo Downloading Wav2Lip GAN model weights...
echo File size: ~436 MB — please wait
echo =============================================

set OUT=D:\Wav2Lip_Windows_GUI-main\src\Wav2Lip\checkpoints\wav2lip_gan.pth

REM Use PowerShell to download (no curl/wget needed on Windows)
powershell -Command "& { $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://huggingface.co/numz/wav2lip_studio/resolve/main/Wav2lip/wav2lip_gan.pth' -OutFile '%OUT%' -UseBasicParsing }"

if exist "%OUT%" (
    echo.
    echo SUCCESS! Model saved to:
    echo %OUT%
    echo.
    echo You can now restart run_all.ps1 to use Wav2Lip for lip-syncing.
) else (
    echo.
    echo DOWNLOAD FAILED. Try alternate source:
    echo https://huggingface.co/Nekochu/Wav2Lip/resolve/main/wav2lip_gan.pth
    powershell -Command "& { $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://huggingface.co/Nekochu/Wav2Lip/resolve/main/wav2lip_gan.pth' -OutFile '%OUT%' -UseBasicParsing }"
    if exist "%OUT%" (
        echo SUCCESS with alternate source!
    ) else (
        echo Both downloads failed. Please download manually and place at:
        echo %OUT%
    )
)
pause

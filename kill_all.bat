@echo off
echo Stopping all Smart News Marathi services...
taskkill /f /im python.exe /t
taskkill /f /im ffmpeg.exe /t
echo Done.
pause

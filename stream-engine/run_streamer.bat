@echo off
cd /d "D:\Apps\Smart News Marathi\stream-engine"
echo Starting SNM Streamer...
..\backend\venv\Scripts\python.exe streamer.py
pause

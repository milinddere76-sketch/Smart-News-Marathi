# Set terminal encoding to handle Marathi
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   VartaPravah Master Control Runtime Starter   " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Starting FastAPI Backend (Admin & Generator)...." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath "cmd.exe" -ArgumentList "/c cd backend && .\venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug"

Write-Host "Waiting 20 seconds for backend AI models to load into VRAM..."
Start-Sleep -Seconds 20

Write-Host "2. Starting Next.js Admin Dashboard...." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "cmd.exe" -ArgumentList "/c cd frontend && npm run dev"

Write-Host "Waiting 5 seconds for frontend..."
Start-Sleep -Seconds 5

Write-Host "3. Starting 24x7 Stream Engine...." -ForegroundColor Magenta
Write-Host "Warning: Ensure YOUTUBE_STREAM_KEY is set in .env" -ForegroundColor Red
Start-Process -NoNewWindow -FilePath "cmd.exe" -ArgumentList "/c cd stream-engine && ..\backend\venv\Scripts\activate && python -u streamer.py"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "All components launched!" -ForegroundColor Green
Write-Host "Backend API     -> http://localhost:8000"
Write-Host "Admin Dashboard -> http://localhost:3000"
Write-Host "Stream Engine   -> Streaming to YouTube RTMP"
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to terminate this orchestrator (Process windows will remain)."

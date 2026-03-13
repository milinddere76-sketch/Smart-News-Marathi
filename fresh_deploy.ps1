
$FLY = "'C:\Users\Priyansh Dere\.fly\bin\flyctl.exe'"
$ROOT = "D:\Apps\Smart News Marathi"

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host " VartaPravah - Fast Fresh Deployment   " -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# ---- Backend ----
Write-Host "[1/3] Deploying BACKEND..." -ForegroundColor Yellow
Set-Location "$ROOT\backend"
Invoke-Expression "& $FLY deploy --remote-only --wait-timeout 300"
if ($LASTEXITCODE -eq 0) { Write-Host "Backend OK!" -ForegroundColor Green }
else { Write-Host "Backend FAILED - check logs" -ForegroundColor Red }

# ---- Streamer ----
Write-Host "[2/3] Deploying STREAMER..." -ForegroundColor Yellow
Set-Location "$ROOT\stream-engine"
Invoke-Expression "& $FLY deploy --remote-only --wait-timeout 300"
if ($LASTEXITCODE -eq 0) { Write-Host "Streamer OK!" -ForegroundColor Green }
else { Write-Host "Streamer FAILED - check logs" -ForegroundColor Red }

# ---- Frontend ----
Write-Host "[3/3] Deploying FRONTEND..." -ForegroundColor Yellow
Set-Location "$ROOT\frontend"
Invoke-Expression "& $FLY deploy --remote-only --wait-timeout 300"
if ($LASTEXITCODE -eq 0) { Write-Host "Frontend OK!" -ForegroundColor Green }
else { Write-Host "Frontend FAILED - check logs" -ForegroundColor Red }

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host " DONE! Backend: https://snm-be-priyansh-dere.fly.dev" -ForegroundColor Green
Write-Host " Stream logs: fly logs --app dere-snm-streamer" -ForegroundColor White
Write-Host "=======================================" -ForegroundColor Cyan

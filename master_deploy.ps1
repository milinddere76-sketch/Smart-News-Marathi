# Smart News Marathi - Master Deployment Script
# This script automates the entire deployment process to Fly.io

$FLY = "C:\Users\Priyansh Dere\.fly\bin\flyctl.exe"
$ROOT = "d:\Apps\Smart News Marathi"

# 1. Unique App Names (Updated to avoid "Taken" errors)
$BE_APP = "snm-be-priyansh-dere"
$FE_APP = "snm-fe-priyansh-dere"

Write-Host "--- 1. Updating App Configs ---" -ForegroundColor Cyan
# Update backend fly.toml
(Get-Content "$ROOT\backend\fly.toml") -replace 'app = ".*"', "app = `"$BE_APP`"" | Set-Content "$ROOT\backend\fly.toml"
# Update frontend fly.toml
(Get-Content "$ROOT\frontend\fly.toml") -replace 'app = ".*"', "app = `"$FE_APP`"" | Set-Content "$ROOT\frontend\fly.toml"
(Get-Content "$ROOT\frontend\fly.toml") -replace 'NEXT_PUBLIC_API_URL = ".*"', "NEXT_PUBLIC_API_URL = `"https://$BE_APP.fly.dev`"" | Set-Content "$ROOT\frontend\fly.toml"

Write-Host "--- 2. Committing to Git ---" -ForegroundColor Cyan
Set-Location $ROOT
git add .
git commit -m "Deployment: Unique app names and Pseudo-Live mode"
git push origin main

Write-Host "--- 3. Creating Fly Apps ---" -ForegroundColor Cyan
& $FLY apps create $BE_APP --org personal --json | Out-Null
& $FLY apps create $FE_APP --org personal --json | Out-Null

Write-Host "--- 4. Deploying Backend ---" -ForegroundColor Cyan
Set-Location "$ROOT\backend"
& $FLY deploy --remote-only --detach

Write-Host "--- 5. Deploying Frontend ---" -ForegroundColor Cyan
Set-Location "$ROOT\frontend"
& $FLY deploy --remote-only --detach

Write-Host "--- DONE! ---" -ForegroundColor Green
Write-Host "Once finished, your site will be at: https://$FE_APP.fly.dev"

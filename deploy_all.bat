@echo off
setlocal

echo ===========================================
echo  STEP 1: Push changes to Git
echo ===========================================
echo Render uses Git-based deployments. Please ensure your
echo latest changes are committed and pushed to your repository.
echo.
echo 1. git add .
echo 2. git commit -m "Migrate to Render"
echo 3. git push origin main
echo.
echo ===========================================
echo  STEP 2: Deploy on Render
echo ===========================================
echo 1. Go to https://dashboard.render.com
echo 2. Click "New" -> "Blueprint"
echo 3. Connect your repository
echo 4. Render will automatically detect render.yaml
echo.
echo ALL DEPLOYMENTS ARE MANAGED BY RENDER (GIT-DRIVEN)
echo ===========================================
pause


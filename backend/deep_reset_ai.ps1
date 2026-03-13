# Deep Reset script for Smart News Marathi AI Environment
# This will recreate the venv and install matching AI libraries.

$BackendDir = Get-Location
$VenvPath = Join-Path $BackendDir "venv"
$PythonExe = "C:\Users\Priyansh Dere\AppData\Local\Programs\Python\Python310\python.exe"

Write-Host "--- STARTING DEEP RESET OF AI ENVIRONMENT ---" -ForegroundColor Cyan

# 1. Kill any hanging python processes
Write-Host "Cleaning up old processes..."
Stop-Process -Name "python" -ErrorAction SilentlyContinue

# 2. Delete existing venv
if (Test-Path $VenvPath) {
    Write-Host "Deleting existing venv..."
    Remove-Item -Recurse -Force $VenvPath
}

# 3. Create new venv
Write-Host "Creating fresh virtual environment..."
& $PythonExe -m venv venv

# 4. Activate and install core AI libraries
Write-Host "Installing Core AI Engines (PyTorch + CUDA 11.8)..."
& .\venv\Scripts\python.exe -m pip install --upgrade pip
& .\venv\Scripts\python.exe -m pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118

# 5. Install SadTalker requirements + setuptools + utilities
Write-Host "Installing SadTalker dependencies and utilities..."
& .\venv\Scripts\python.exe -m pip install setuptools python-dotenv requests
& .\venv\Scripts\python.exe -m pip install -r SadTalker/requirements.txt

# 6. Apply the basicsr patch automatically
Write-Host "Applying stability patch to basicsr..."
$PatchScript = @"
import os
import sys
basicsr_path = os.path.join(r'$BackendDir', 'venv', 'Lib', 'site-packages', 'basicsr', 'data', 'degradations.py')
if os.path.exists(basicsr_path):
    with open(basicsr_path, 'r') as f:
        content = f.read()
    new_content = content.replace('from torchvision.transforms.functional_tensor import rgb_to_grayscale', 'from torchvision.transforms.functional import rgb_to_grayscale')
    with open(basicsr_path, 'w') as f:
        f.write(new_content)
    print('Patch applied successfully!')
else:
    print('basicsr not found at expected path.')
"@
$PatchScript | Out-File -FilePath "apply_patch_tmp.py" -Encoding utf8
& .\venv\Scripts\python.exe apply_patch_tmp.py
Remove-Item "apply_patch_tmp.py"

Write-Host "--- [SUCCESS] DEEP RESET COMPLETE! ---" -ForegroundColor Green
Write-Host "You can now run: python debug_sadtalker_direct.py"

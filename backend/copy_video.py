import shutil
import os

src = r"d:\Apps\Smart News Marathi\backend\media\video\final_fa049ca929a64968ba56a7a76696e39c.mp4"
dst = r"C:\Users\Priyansh Dere\.gemini\antigravity\brain\25cad5f2-5c6a-4406-96b6-2e92303e585c\latest_preview.mp4"

try:
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print("Copy Successful")
    else:
        print(f"Source file not found: {src}")
except Exception as e:
    print(f"Error: {e}")

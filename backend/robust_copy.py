import shutil
import os

source = r"d:\Apps\Smart News Marathi\backend\media\video\final_fa049ca929a64968ba56a7a76696e39c.mp4"
dest = r"C:\Users\Priyansh Dere\.gemini\antigravity\brain\25cad5f2-5c6a-4406-96b6-2e92303e585c\latest_preview.mp4"

try:
    if not os.path.exists(source):
        print(f"FAILED: Source not found at {source}")
    else:
        shutil.copy2(source, dest)
        if os.path.exists(dest):
            print(f"SUCCESS: Copied to {dest}")
        else:
            print(f"FAILED: Destination not found after copy at {dest}")
except Exception as e:
    print(f"ERROR: {str(e)}")

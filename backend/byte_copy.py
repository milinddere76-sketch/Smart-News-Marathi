import os

src = r"d:\Apps\Smart News Marathi\backend\media\video\final_fa049ca929a64968ba56a7a76696e39c.mp4"
dst = r"C:\Users\Priyansh Dere\.gemini\antigravity\brain\25cad5f2-5c6a-4406-96b6-2e92303e585c\latest_preview.mp4"

try:
    with open(src, "rb") as f_in:
        with open(dst, "wb") as f_out:
            f_out.write(f_in.read())
    print(f"SUCCESS: Copied {os.path.getsize(dst)} bytes to {dst}")
except Exception as e:
    print(f"ERROR: {str(e)}")

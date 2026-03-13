import os
import requests
import subprocess

def log(msg):
    with open("diag_log.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

if os.path.exists("diag_log.txt"):
    os.remove("diag_log.txt")

log("--- DIAGNOSTIC START ---")

# 1. Check FFmpeg
ffmpeg_path = r"D:\ffmpeg\bin\ffmpeg.exe"
log(f"Checking FFmpeg at: {ffmpeg_path}")
if os.path.exists(ffmpeg_path):
    log("Binary exists on disk.")
    try:
        res = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True, timeout=5)
        log(f"FFmpeg Execution: OK (Return code {res.returncode})")
        log(f"FFmpeg Version: {res.stdout.splitlines()[0] if res.stdout else 'No output'}")
    except Exception as e:
        log(f"FFmpeg Execution FAILED: {e}")
else:
    log("Binary MISSING on disk.")

# 2. Check Backend
backend_url = "http://localhost:8000"
log(f"Checking Backend at: {backend_url}")
try:
    r = requests.get(f"{backend_url}/news/videos", timeout=5)
    log(f"Backend HTTP: {r.status_code}")
    log(f"Videos Found: {len(r.json().get('videos', []))}")
except Exception as e:
    log(f"Backend Connection FAILED: {e}")

log("--- DIAGNOSTIC END ---")

import os
import socket
import subprocess
import requests

output = []

def log(msg):
    print(msg)
    output.append(msg)

log("--- Stream Engine Diagnostic ---")

# 1. Check Port 8000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
if s.connect_ex(('127.0.0.1', 8000)) == 0:
    log("Port 8000: OPEN (Backend is running)")
else:
    log("Port 8000: CLOSED (Backend may not be running)")
s.close()

# 2. Check Processes
try:
    tasks = subprocess.check_output('tasklist /FI "IMAGENAME eq python.exe" /NH /V', shell=True).decode('utf-8', errors='ignore')
    log("\nPython Processes found:")
    log(tasks)
except:
    log("Could not run tasklist for python")

try:
    tasks_ff = subprocess.check_output('tasklist /FI "IMAGENAME eq ffmpeg.exe" /NH /V', shell=True).decode('utf-8', errors='ignore')
    log("\nFFmpeg Processes found:")
    log(tasks_ff)
except:
    log("Could not run tasklist for ffmpeg")

# 3. Check Stream Engine Config
env_path = "stream-engine/.env"
if os.path.exists(env_path):
    log(f"\nFound {env_path}:")
    with open(env_path, 'r') as f:
        for line in f:
            if "YOUTUBE_STREAM_KEY" in line or "BACKEND_URL" in line:
                log(f"  {line.strip()}")
else:
    log(f"\n{env_path} NOT FOUND!")

# 4. Check FFmpeg Capabilities
ffmpeg_path = r"D:\ffmpeg\bin\ffmpeg.exe"
if os.path.exists(ffmpeg_path):
    try:
        ver = subprocess.check_output([ffmpeg_path, "-version"], stderr=subprocess.STDOUT).decode('utf-8', errors='ignore').split('\n')[0]
        log(f"\nFFmpeg: {ver}")
        help_draw = subprocess.check_output([ffmpeg_path, "-h", "filter=drawtext"], stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
        if "text_shaping" in help_draw:
            log("  [OK] FFmpeg supports text_shaping=1")
        else:
            log("  [WARNING] FFmpeg DOES NOT support text_shaping=1 (this might crash the stream)")
    except Exception as e:
        log(f"Error checking ffmpeg: {e}")
else:
    log(f"\nFFmpeg NOT FOUND at {ffmpeg_path}!")

# 5. Check Backend API
try:
    r = requests.get("http://localhost:8000/news/videos", timeout=5)
    log(f"\nBackend API /news/videos: {r.status_code}")
    log(f"Response: {r.text[:200]}...")
except Exception as e:
    log(f"\nBackend API unreachable: {e}")

with open("debug_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

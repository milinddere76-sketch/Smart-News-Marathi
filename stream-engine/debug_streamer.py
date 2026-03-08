import os
import requests
import subprocess
import sys
from broadcaster import Broadcaster

def check_env():
    print("--- Environment Check ---")
    key = os.getenv("YOUTUBE_STREAM_KEY")
    url = os.getenv("BACKEND_URL", "http://localhost:8000")
    print(f"YOUTUBE_STREAM_KEY: {'[SET]' if key else '[MISSING]'}")
    print(f"BACKEND_URL: {url}")
    return key, url

def check_backend(url):
    print("\n--- Backend Connectivity ---")
    try:
        resp = requests.get(f"{url}/news/videos", timeout=5)
        if resp.ok:
            videos = resp.json().get("videos", [])
            print(f"Connection OK. Found {len(videos)} videos.")
            return True
        else:
            print(f"Connection failed: {resp.status_code}")
    except Exception as e:
        print(f"Connection error: {e}")
    return False

def check_ffmpeg():
    print("\n--- FFmpeg Check ---")
    ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")
    try:
        res = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True)
        if res.returncode == 0:
            print("FFmpeg is accessible.")
            return True
        else:
            print(f"FFmpeg failed with code {res.returncode}")
    except Exception as e:
        print(f"FFmpeg error: {e}")
    return False

if __name__ == "__main__":
    key, url = check_env()
    check_backend(url)
    check_ffmpeg()
    
    if not key:
        print("\n[!] ERROR: YOUTUBE_STREAM_KEY is not set.")
        print("Please set it with: $env:YOUTUBE_STREAM_KEY='your_key_here'")
    
    print("\n--- Diagnostic Finished ---")

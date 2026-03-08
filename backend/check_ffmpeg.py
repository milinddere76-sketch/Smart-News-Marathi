"""
FFmpeg Diagnostic Tool
=======================
Use this script to find where FFmpeg is installed and get the exact
lines to add to your .env file.
"""

import os
import shutil
import subprocess

def check():
    print("=" * 50)
    print("  FFmpeg Diagnostic for Smart News Marathi")
    print("=" * 50)

    # 1. Check if in PATH
    ffmpeg_in_path = shutil.which("ffmpeg")
    ffprobe_in_path = shutil.which("ffprobe")

    if ffmpeg_in_path:
        print(f"\n✅ FFmpeg found in PATH: {ffmpeg_in_path}")
    else:
        print("\n❌ FFmpeg NOT found in PATH.")

    # 2. Try common Windows install locations
    common_paths = [
        "C:\\ffmpeg\\bin\\ffmpeg.exe",
        "C:\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe",
        os.path.expandvars("%USERPROFILE%\\Downloads\\ffmpeg\\bin\\ffmpeg.exe"),
    ]
    
    found_manual = None
    for p in common_paths:
        if os.path.exists(p):
            found_manual = p
            print(f"🔍 Found FFmpeg at common location: {p}")
            break

    # 3. Output instructions
    if ffmpeg_in_path:
        print("\n✨ Everything looks good! If you still get errors, try restarting VS Code.")
    elif found_manual:
        print("\n🛠️  FFmpeg is installed but not in PATH. Add these lines to your backend/.env file:")
        print(f"\nFFMPEG_PATH={found_manual}")
        print(f"FFPROBE_PATH={found_manual.replace('ffmpeg.exe', 'ffprobe.exe')}")
        print("\nAfter adding these, restart your backend.")
    else:
        print("\n❗ FFmpeg is missing. Please follow these steps:")
        print("1. Download from: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip")
        print("2. Extract the folder to C:\\ffmpeg")
        print("3. Then run this script again.")

if __name__ == "__main__":
    check()

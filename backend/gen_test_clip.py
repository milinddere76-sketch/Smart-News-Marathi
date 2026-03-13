"""
Quick test: generate a single video clip using the fixed VideoGenerator
and verify it has a proper video stream.
"""
import os
import sys
import subprocess

sys.path.insert(0, r"D:\Apps\Smart News Marathi\backend")
os.chdir(r"D:\Apps\Smart News Marathi\backend")

# First delete old clips
video_dir = "media/video"
deleted = 0
for f in os.listdir(video_dir):
    if f.endswith(".mp4"):
        try:
            os.remove(os.path.join(video_dir, f))
            deleted += 1
        except Exception as e:
            print(f"Could not delete {f}: {e}")
print(f"Deleted {deleted} old clips")

# Now generate a fresh clip using fixed VideoGenerator
print("\nImporting VideoGenerator...")
from video_generator import VideoGenerator, FONT

print(f"Font Path: {FONT}")

# Create a test clip from the most recent audio file
audio_dir = "media/audio"
audio_files = sorted(
    [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith(".mp3")],
    key=os.path.getmtime, reverse=True
)

if not audio_files:
    print("No audio files found!")
    sys.exit(1)

audio_file = audio_files[0]
print(f"\nUsing audio: {os.path.basename(audio_file)}")

vg = VideoGenerator()
test_output = "media/video/test_fresh_clip.mp4"
result = vg.create_news_clip(
    os.path.abspath(audio_file),
    "स्मार्ट न्यूज मराठी — चाचणी",
    "Smart News Marathi",
    "test_fresh_clip.mp4",
    None
)

if result and os.path.exists(result):
    size = os.path.getsize(result)
    print(f"\nSUCCESS! Created: {result} ({size:,} bytes)")
    
    # Probe for video stream
    ffprobe = r"D:\ffmpeg\bin\ffprobe.exe"
    probe = subprocess.run(
        [ffprobe, "-v", "error", "-show_streams", "-print_format", "json", result],
        capture_output=True, text=True
    )
    if '"codec_type": "video"' in probe.stdout:
        print("✅ Video stream CONFIRMED in output clip!")
    else:
        print("❌ No video stream found in output clip!")
        print(probe.stdout)
else:
    print("FAILED to generate clip!")

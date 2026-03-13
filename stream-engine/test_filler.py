import os
import subprocess

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
ffmpeg_path = r"D:\ffmpeg\bin\ffmpeg.exe"
font_path = os.path.join(script_dir, "..", "backend", "media", "assets", "news_font.ttf")
font_path = os.path.normpath(font_path)

# Ensure font exists for test
if not os.path.exists(font_path):
    os.makedirs(os.path.dirname(font_path), exist_ok=True)
    import shutil
    shutil.copy(r"C:\Windows\Fonts\arial.ttf", font_path)

# FFmpeg escaped font path
esc_font = font_path.replace(":", "\\:")

output_file = os.path.join(script_dir, "filler_test.mp4")

cmd = [
    ffmpeg_path, "-y",
    "-f", "lavfi", "-i", "color=c=0x0a0f1e:s=1920x1080:d=3",
    "-vf", f"drawtext=text='TEST FILLER':fontfile='{esc_font}':fontsize=100:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
    output_file
]

print(f"Running: {' '.join(cmd)}")
try:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    print("SUCCESS")
    print(f"File created: {output_file} ({os.path.getsize(output_file)} bytes)")
except subprocess.CalledProcessError as e:
    print("FAILED")
    print("Stderr:", e.stderr)
except Exception as e:
    print("ERROR:", str(e))

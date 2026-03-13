import subprocess
import os

ffmpeg_path = r"D:\ffmpeg\bin\ffmpeg.exe"
font_path = r"d:\Apps\Smart News Marathi\backend\media\assets\news_font.ttf"
output_file = r"d:\Apps\Smart News Marathi\backend\media\video\test_render.mp4"

# Ensure local font exists for test
os.makedirs(os.path.dirname(font_path), exist_ok=True)
if not os.path.exists(font_path):
    import shutil
    shutil.copy(r"C:\Windows\Fonts\arial.ttf", font_path)

cmd = [
    ffmpeg_path, "-y",
    "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=3",
    "-vf", f"drawtext=text='FFmpeg Test':fontfile='{font_path}':fontsize=50:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
    output_file
]

print(f"Running: {' '.join(cmd)}")
try:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    print("SUCCESS")
    print(f"Output File Size: {os.path.getsize(output_file)}")
except subprocess.CalledProcessError as e:
    print("FAILED")
    print("Stdout:", e.stdout)
    print("Stderr:", e.stderr)
except Exception as e:
    print("ERROR:", str(e))

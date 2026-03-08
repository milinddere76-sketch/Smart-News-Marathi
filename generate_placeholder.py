import subprocess
import os

os.makedirs("stream-engine/media/assets", exist_ok=True)
os.makedirs("stream-engine/media/video", exist_ok=True)
os.makedirs("stream-engine/media/ads", exist_ok=True)

output_file = "stream-engine/media/assets/placeholder_loop.mp4"

if not os.path.exists(output_file):
    print("Generating placeholder video...")
    command = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=black:s=1920x1080:d=10",
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-c:v", "libx264", "-c:a", "aac", "-shortest",
        output_file
    ]
    subprocess.run(command)
    print("Done!")
else:
    print("Placeholder already exists.")

import subprocess
import os

font_path = "D:/snm_font.ttf"
if os.path.exists(font_path):
    safe_font = font_path.replace(":", "\\:")
else:
    safe_font = "Arial"

text = "महाराष्ट्रातील मोठी बातमी: 'सत्य · निर्भय · निष्पक्ष'"
text_esc = text.replace("'", "\u2019").replace(":", "\\:").replace(".", "\\.")

cmd = [
    "ffmpeg", "-y",
    "-f", "lavfi", "-i", "color=c=navy:s=640x360:d=1",
    "-vf", f"drawtext=text='{text_esc}':fontfile='{safe_font}':fontsize=30:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
    "-frames:v", "1",
    "marathi_test_v2.png"
]

with open("marathi_debug.log", "w", encoding="utf-8") as f:
    f.write(f"Running command: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    f.write(f"Return code: {result.returncode}\n")
    f.write(f"STDOUT: {result.stdout}\n")
    f.write(f"STDERR: {result.stderr}\n")

print("Finished. check marathi_debug.log")

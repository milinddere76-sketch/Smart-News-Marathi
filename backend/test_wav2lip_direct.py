import os
import sys
import subprocess
import logging

WAV2LIP_DIR = r"D:\Wav2Lip_Windows_GUI-main\src\Wav2Lip"
WAV2LIP_MODEL = os.path.join(WAV2LIP_DIR, "checkpoints", "wav2lip_gan.pth")
INFERENCE_PY = os.path.join(WAV2LIP_DIR, "inference.py")

# Try to find a real anchor photo and audio to test with
audio_path = r"D:\Apps\Smart News Marathi\backend\media\audio\test_voice.mp3"
photo_path = r"D:\Apps\Smart News Marathi\backend\media\anchor\male_anchor_1.jpg"
output_path = r"D:\Apps\Smart News Marathi\backend\media\video\test_wav2lip_out.mp4"

if not os.path.exists(audio_path):
    print(f"ERROR: Audio missing: {audio_path}")
if not os.path.exists(photo_path):
    # Try alternate
    photo_path = r"D:\Apps\Smart News Marathi\backend\media\anchor\female_anchor_1.jpg"
    if not os.path.exists(photo_path):
        print(f"ERROR: Photo missing: {photo_path}")

print(f"Testing Wav2Lip with:")
print(f"  Model: {WAV2LIP_MODEL}")
print(f"  Audio: {audio_path}")
print(f"  Photo: {photo_path}")

cmd = [
    sys.executable,
    INFERENCE_PY,
    "--checkpoint_path", WAV2LIP_MODEL,
    "--face", photo_path,
    "--audio", audio_path,
    "--outfile", output_path,
    "--nosmooth" # Faster for testing
]

print(f"Running command: {' '.join(cmd)}")

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    with open("wav2lip_diag.txt", "w", encoding="utf-8") as f:
        f.write(f"Return Code: {result.returncode}\n")
        f.write("--- STDOUT ---\n")
        f.write(result.stdout)
        f.write("\n--- STDERR ---\n")
        f.write(result.stderr)
    print("Test finished. Check wav2lip_diag.txt")
except Exception as e:
    with open("wav2lip_diag.txt", "w", encoding="utf-8") as f:
        f.write(f"Exception: {str(e)}")
    print(f"Exception occurred: {e}")

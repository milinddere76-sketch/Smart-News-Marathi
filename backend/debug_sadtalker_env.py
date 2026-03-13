import os
import sys
import shutil

log_file = r"d:\Apps\Smart News Marathi\backend\debug_sadtalker.log"

def log(msg):
    print(msg)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

if os.path.exists(log_file):
    os.remove(log_file)

log("--- Environment Check ---")
log(f"Python: {sys.version}")
log(f"Executable: {sys.executable}")

try:
    import torch
    log(f"Torch Version: {torch.__version__}")
    log(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        log(f"CUDA Device: {torch.cuda.get_device_name(0)}")
except ImportError:
    log("ERROR: torch not installed")

dependencies = ["cv2", "numpy", "PIL", "yaml", "gfpgan", "realesrgan"]
for dep in dependencies:
    try:
        if dep == "PIL":
            import PIL
        elif dep == "cv2":
            import cv2
        elif dep == "yaml":
            import yaml
        elif dep == "gfpgan":
            import gfpgan
        elif dep == "realesrgan":
            import realesrgan
        log(f"{dep}: OK")
    except ImportError:
        log(f"ERROR: {dep} not installed")

log("\n--- Checkpoints Check ---")
sadtalker_dir = os.path.join(os.getcwd(), "SadTalker")
checkpoint_dir = os.path.join(sadtalker_dir, "checkpoints")

if not os.path.exists(checkpoint_dir):
    log(f"ERROR: {checkpoint_dir} does not exist!")
else:
    log(f"Checkpoint dir found: {checkpoint_dir}")
    log("Contents:")
    try:
        log(", ".join(os.listdir(checkpoint_dir)))
    except Exception as e:
        log(f"Error listing dir: {e}")

# Also check for GFPGAN weights
gfpgan_weights = os.path.join(sadtalker_dir, "gfpgan", "weights")
if os.path.exists(gfpgan_weights):
    log(f"GFPGAN weights found: {gfpgan_weights}")
else:
    log(f"GFPGAN weights NOT found: {gfpgan_weights}")

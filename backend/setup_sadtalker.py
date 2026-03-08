"""
SadTalker One-Click Setup
==========================
Run this ONCE to install SadTalker and download model weights.

Requirements:
  - Python 3.8+
  - Git installed
  - ~4 GB disk space for model weights
  - GPU recommended (NVIDIA with CUDA) — works on CPU but is much slower

Usage:
  cd backend
  python setup_sadtalker.py
"""

import subprocess
import os
import sys
import urllib.request

SADTALKER_DIR = os.path.join(os.path.dirname(__file__), "SadTalker")
CHECKPOINTS   = os.path.join(SADTALKER_DIR, "checkpoints")
GFPGAN        = os.path.join(SADTALKER_DIR, "gfpgan", "weights")

# Model weights URLs (from SadTalker official releases)
WEIGHTS = {
    "checkpoints/SadTalker_V0.0.2_512.safetensors":
        "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors",
    "checkpoints/mapping_00109-model.pth.tar":
        "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar",
    "checkpoints/mapping_00229-model.pth.tar":
        "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar",
    "gfpgan/weights/GFPGANv1.4.pth":
        "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth",
    "gfpgan/weights/detection_Resnet50_Final.pth":
        "https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth",
}


def run(cmd, cwd=None):
    print(f"\n▶  {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"❌  Command failed: {' '.join(cmd)}")
        sys.exit(1)


def download(url, dest):
    """Download a file with progress output."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest):
        print(f"  ✓ Already exists: {os.path.basename(dest)}")
        return

    print(f"  ↓ Downloading: {os.path.basename(dest)} ...")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"  ✓ Saved: {dest}")
    except Exception as e:
        print(f"  ⚠  Download failed ({e}) — you may need to download manually.")


def main():
    print("=" * 60)
    print("  SadTalker Setup for Smart News Marathi")
    print("=" * 60)

    # ── Step 1: Clone SadTalker ───────────────────────────────────
    if not os.path.exists(SADTALKER_DIR):
        print("\n[1/4] Cloning SadTalker repository...")
        run(["git", "clone", "https://github.com/OpenTalker/SadTalker.git",
             SADTALKER_DIR])
    else:
        print("\n[1/4] SadTalker already cloned ✓")

    # ── Step 2: Install Python dependencies ──────────────────────
    print("\n[2/4] Installing / Upgrading core build tools...")
    run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])

    print("\n[3/4] Installing SadTalker Python dependencies...")
    req = os.path.join(SADTALKER_DIR, "requirements.txt")
    # Using --use-pep517 as a fallback for some source builds
    run([sys.executable, "-m", "pip", "install", "-r", req])

    # ── Step 3: Download model weights ────────────────────────────
    print("\n[4/4] Downloading model weights (~4 GB total)...")
    for rel_path, url in WEIGHTS.items():
        dest = os.path.join(SADTALKER_DIR, rel_path.replace("/", os.sep))
        download(url, dest)

    # ── Step 4: Verify ────────────────────────────────────────────
    print("\n[4/4] Verifying install...")
    inference = os.path.join(SADTALKER_DIR, "inference.py")
    checkpoint = os.path.join(CHECKPOINTS, "SadTalker_V0.0.2_512.safetensors")
    ok = os.path.exists(inference) and os.path.exists(checkpoint)

    if ok:
        print("\n✅  SadTalker is ready!")
        print("   The anchor generator will now use AI talking head mode.")
        print("   Restart the backend: python -m uvicorn main:app --reload --port 8000")
    else:
        print("\n⚠   Some files may be missing. The backend will use FFmpeg silhouette fallback.")
        print("   Check logs above for download errors.")


if __name__ == "__main__":
    main()

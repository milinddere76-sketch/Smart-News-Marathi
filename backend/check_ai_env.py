import os
import sys

def check_env():
    results = []
    results.append(f"Python: {sys.version}")
    
    try:
        import torch
        results.append(f"Torch: {torch.__version__} (CUDA: {torch.cuda.is_available()})")
    except ImportError:
        results.append("Torch: NOT INSTALLED")
        
    try:
        import gfpgan
        results.append("GFPGAN: installed")
    except ImportError:
        results.append("GFPGAN: NOT INSTALLED")
        
    ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")
    results.append(f"FFMPEG_PATH: {ffmpeg_path}")
    
    import subprocess
    try:
        res = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True)
        results.append("FFmpeg: Working")
    except Exception as e:
        results.append(f"FFmpeg: Error ({e})")
        
    with open("env_check.txt", "w") as f:
        f.write("\n".join(results))

if __name__ == "__main__":
    check_env()

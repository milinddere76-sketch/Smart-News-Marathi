import os
import sys
import subprocess
import logging
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Ensure we can see the errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def debug_direct():
    # 1. Setup paths
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    sadtalker_dir = os.path.join(backend_dir, "SadTalker")
    ffmpeg_exe = os.getenv("FFMPEG_PATH", "ffmpeg")
    
    # 2. Create assets if missing
    audio_path = os.path.join(backend_dir, "media", "audio", "test_debug.mp3")
    image_path = os.path.join(backend_dir, "media", "assets", "anchor_male.jpg")
    out_dir = os.path.join(backend_dir, "media", "anchor", "debug_out")
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(audio_path):
        logger.info("Generating test audio...")
        subprocess.run([ffmpeg_exe, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "3", audio_path])

    # 3. Build Command
    # We turn OFF the enhancer for this debug run to see if it makes it faster/prevents hanging
    use_enhancer = os.getenv("SADTALKER_USE_ENHANCER", "false").lower() == "true"
    
    cmd = [
        sys.executable,
        os.path.join(sadtalker_dir, "inference.py"),
        "--driven_audio", os.path.abspath(audio_path),
        "--source_image", os.path.abspath(image_path),
        "--result_dir",   os.path.abspath(out_dir),
        "--still",
        "--preprocess", "crop",
        "--size",       "512",
        "--cpu",
    ]
    
    if use_enhancer:
        cmd.extend(["--enhancer", "gfpgan"])

    logger.info("--- STARTING SADTALKER DIRECT DEBUG ---")
    logger.info(f"Command: {' '.join(cmd)}")
    
    # Inject FFmpeg into PATH
    env = os.environ.copy()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    if ffmpeg_dir:
        env["PATH"] = ffmpeg_dir + os.pathsep + env.get("PATH", "")

    # RUN DIRECTLY SO CRASH IS VISIBLE
    try:
        logger.info("Starting subprocess (Streaming output to terminal)...")
        # Direct execution to terminal so user can see progress bar and errors immediately
        result = subprocess.run(
            cmd, 
            cwd=sadtalker_dir, 
            env=env
            # Removed capture_output so it prints to terminal in real-time
        )
        
        if result.returncode == 0:
            logger.info("--- [SUCCESS] SADTALKER WORKED! ---")
        else:
            logger.error(f"Sadtalker failed with exit code {result.returncode}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    debug_direct()

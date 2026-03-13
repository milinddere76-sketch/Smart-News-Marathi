"""
AI Anchor Generator
====================
Generates a virtual anchor (talking head) video from an audio file.

Priority:
  1. SadTalker  — AI talking head (realistic, requires GPU or slow CPU)
  2. FFmpeg      — Animated studio silhouette (instant, always works)

Usage:
  from anchor_generator import AnchorGenerator
  gen = AnchorGenerator()
  clip = gen.generate_anchor_clip("media/audio/news_xxx.mp3", "media/anchor/anchor_xxx.mp4")
"""

import os
import subprocess
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

import sys

# ── FFmpeg Configuration ──────────────────────────────────────────────────────
_env_ffmpeg = os.getenv("FFMPEG_PATH", "ffmpeg")
_env_ffprobe = os.getenv("FFPROBE_PATH", "ffprobe")

# Robust check: if the env path doesn't exist, use the command name (for Linux/Docker)
FFMPEG_EXE = _env_ffmpeg if os.path.exists(_env_ffmpeg) else "ffmpeg"
FFPROBE_EXE = _env_ffprobe if os.path.exists(_env_ffprobe) else "ffprobe"

logger.info(f"Using FFmpeg: {FFMPEG_EXE}")


# ── Paths ──────────────────────────────────────────────────────────────────────
ASSETS_DIR    = "static_assets" if os.path.exists("static_assets") else "media/assets"

# Primary local paths
ANCHOR_MALE   = os.path.join(ASSETS_DIR, "anchor_male.jpg")
ANCHOR_FEMALE = os.path.join(ASSETS_DIR, "anchor_female.jpg")

SADTALKER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "SadTalker"))
# Wav2Lip — user downloaded Wav2Lip_Windows_GUI from GitHub, actual code lives in src/Wav2Lip
WAV2LIP_DIR   = os.getenv("WAV2LIP_DIR", r"D:\Wav2Lip_Windows_GUI-main\src\Wav2Lip")
WAV2LIP_MODEL = os.path.join(WAV2LIP_DIR, "checkpoints", "wav2lip_gan.pth")
OUTPUT_DIR    = "media/anchor"

def get_font_path():
    """
    Returns a valid font path for FFmpeg drawtext, cross-platform.
    Works on Windows (local dev) and Linux (Docker/Fly.io).
    """
    import shutil
    import platform

    # Linux / Docker paths (Fly.io runs Debian)
    linux_fonts = [
        "/app/static_assets/news_font.ttf", # included via Docker COPY
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for p in linux_fonts:
        if os.path.exists(p):
            return p

    # Windows paths (local dev)
    no_space_font = "D:/snm_font.ttf"
    if not os.path.exists(no_space_font):
        source_fonts = [
            "D:/Apps/Smart News Marathi/backend/media/assets/news_font.ttf",
            "C:/Windows/Fonts/Nirmala.ttf",
            "C:/Windows/Fonts/arial.ttf"
        ]
        for pf in source_fonts:
            if os.path.exists(pf):
                try:
                    shutil.copy(pf, no_space_font)
                    break
                except Exception:
                    pass
    if os.path.exists(no_space_font):
        return no_space_font.replace(":", "\\:")
    for p in ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/Nirmala.ttf"]:
        if os.path.exists(p):
            return p.replace(":", "\\:")

    return ""  # Empty string = FFmpeg uses default font (no fontfile= arg needed)

FONT = get_font_path()

# ── Studio Dimensions ──────────────────────────────────────────────────────────
ANCHOR_W = 280       # left zone width
ANCHOR_H = 408       # content zone height (480 - top bar 40 - ticker 30 - gold 2) - must be even!

class AnchorGenerator:
    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(ASSETS_DIR, exist_ok=True)
        # Wav2Lip (local GPU, best quality)
        self._wav2lip_ok = self._check_wav2lip()
        # SadTalker (fallback AI)
        self._sadtalker_ok = self._check_sadtalker() if not self._wav2lip_ok else False
        if self._wav2lip_ok:
            mode = "Wav2Lip (GPU)"
        elif self._sadtalker_ok:
            mode = "SadTalker"
        else:
            mode = "FFmpeg Static/Silhouette"
        logger.info(f"AnchorGenerator initialised — mode: {mode}")

    # ── Public API ─────────────────────────────────────────────────────────────

    def generate_anchor_clip(self, audio_path: str, output_path: str, is_male: bool = False) -> str:
        """
        Generate a {ANCHOR_W}x{ANCHOR_H} anchor video synced to the given audio.
        Returns output_path on success, '' on failure.
        """
        # 1. Resolve Best Photo
        anchor_photo = ANCHOR_MALE if is_male else ANCHOR_FEMALE
        if not os.path.exists(anchor_photo):
            logger.error(f"Critical asset missing: {anchor_photo}")
            anchor_photo = ""

        # 2. Wav2Lip (local GPU — best quality lip-sync)
        if self._wav2lip_ok and anchor_photo:
            result = self._run_wav2lip(audio_path, output_path, anchor_photo)
            if result:
                return result
            logger.warning("Wav2Lip failed — falling back.")

        # 3. SadTalker (fallback AI, if Wav2Lip not present)
        if self._sadtalker_ok and anchor_photo:
            result = self._run_sadtalker(audio_path, output_path, anchor_photo)
            if result:
                return result
            logger.warning("SadTalker failed — falling back to FFmpeg animation.")

        # 4. FFmpeg (Static Zoom or Silhouette — always works)
        return self._run_ffmpeg_silhouette(audio_path, output_path, anchor_photo)

    # ── Wav2Lip (Primary, Local GPU) ──────────────────────────────────────────

    def _check_wav2lip(self) -> bool:
        """Returns True if Wav2Lip is installed with model weights."""
        return (
            os.path.isdir(WAV2LIP_DIR)
            and os.path.isfile(os.path.join(WAV2LIP_DIR, "inference.py"))
            and os.path.isfile(WAV2LIP_MODEL)
        )

    def _run_wav2lip(self, audio_path: str, output_path: str, anchor_photo: str) -> str:
        """
        Runs Wav2Lip inference to produce a realistic lip-synced anchor video.
        Requires GPU (CUDA). Falls back gracefully on failure.
        """
        try:
            inference_py = os.path.join(WAV2LIP_DIR, "inference.py")
            env = os.environ.copy()
            ffmpeg_dir = os.path.dirname(FFMPEG_EXE)
            if ffmpeg_dir:
                env["PATH"] = ffmpeg_dir + os.pathsep + env.get("PATH", "")

            cmd = [
                sys.executable,
                inference_py,
                "--checkpoint_path", WAV2LIP_MODEL,
                "--face",           os.path.abspath(anchor_photo),
                "--audio",          os.path.abspath(audio_path),
                "--outfile",        os.path.abspath(output_path),
                "--resize_factor",  "1",
                "--nosmooth",
            ]

            logger.info(f"Running Wav2Lip inference...")
            result = subprocess.run(
                cmd,
                cwd=WAV2LIP_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=600,  # 10 min max
                env=env,
            )

            if result.returncode != 0:
                logger.error(f"Wav2Lip failed (rc={result.returncode}):\n{result.stderr[-500:]}")
                return ""

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                # Resize to anchor zone dimensions
                resized = output_path.replace(".mp4", "_resized.mp4")
                duration = self._audio_duration(audio_path)
                self._resize_to_anchor_zone(output_path, resized, duration)
                if os.path.exists(resized):
                    os.replace(resized, output_path)
                logger.info(f"✅ Wav2Lip anchor clip: {output_path}")
                return output_path

            logger.error("Wav2Lip produced no output file.")
            return ""

        except subprocess.TimeoutExpired:
            logger.error("Wav2Lip timed out (>10 min).")
            return ""
        except Exception as exc:
            logger.exception(f"Wav2Lip error: {exc}")
            return ""

    # ── SadTalker (Fallback AI) ────────────────────────────────────────────────

    def _check_sadtalker(self) -> bool:
        """Returns True if SadTalker is cloned and inference.py is present."""
        inference = os.path.join(SADTALKER_DIR, "inference.py")
        return os.path.exists(inference)

    def _run_sadtalker(self, audio_path: str, output_path: str, anchor_photo: str) -> str:
        """
        Calls SadTalker inference to produce a talking head video.
        """
        try:
            duration = self._audio_duration(audio_path)
            sadtalker_out_dir = os.path.join(OUTPUT_DIR, "sadtalker_tmp")
            os.makedirs(sadtalker_out_dir, exist_ok=True)

            # Determine device (Use GPU if torch.cuda.is_available() is True)
            device_flag = "--cpu"
            try:
                import torch
                if torch.cuda.is_available():
                    device_flag = "" # Use GPU (default in SadTalker)
                    logger.info("CUDA detected! Using GPU for lip-syncing (Fast).")
                else:
                    logger.warning("No CUDA detected. Using CPU for lip-syncing (Slow).")
            except Exception:
                pass

            cmd = [
                sys.executable,
                os.path.join(SADTALKER_DIR, "inference.py"),
                "--driven_audio", os.path.abspath(audio_path),
                "--source_image", os.path.abspath(anchor_photo),
                "--result_dir",   os.path.abspath(sadtalker_out_dir),
                "--still",                   
                "--preprocess", "crop",      
                "--size",       "256",
            ]
            if device_flag:
                cmd.append(device_flag)

            logger.info(f"Running SadTalker inference (Timeout: 1 hour)...")
            # Inject FFMPEG_PATH directory into PATH so SadTalker can find it
            env = os.environ.copy()
            ffmpeg_dir = os.path.dirname(FFMPEG_EXE)
            if ffmpeg_dir:
                env["PATH"] = ffmpeg_dir + os.pathsep + env.get("PATH", "")

            result = subprocess.run(
                cmd,
                cwd=SADTALKER_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=3600,  # 1-hour timeout for long news segments on CPU
                env=env
            )

            if result.returncode != 0:
                logger.error(f"SadTalker failed with return code {result.returncode}")
                logger.error(f"SadTalker stdout: {result.stdout}")
                logger.error(f"SadTalker stderr: {result.stderr}")
                return ""

            # Find the generated video in the output dir
            for f in sorted(os.listdir(sadtalker_out_dir), reverse=True):
                if f.endswith(".mp4"):
                    raw = os.path.join(sadtalker_out_dir, f)
                    # Resize to anchor zone dimensions
                    self._resize_to_anchor_zone(raw, output_path, duration)
                    logger.info(f"✅ SadTalker anchor clip: {output_path}")
                    return output_path

            logger.error("SadTalker produced no MP4 output.")
            return ""

        except subprocess.TimeoutExpired:
            logger.error("SadTalker timed out (>10 min).")
            return ""
        except Exception as exc:
            logger.exception(f"SadTalker error: {exc}")
            return ""

    def _resize_to_anchor_zone(self, src: str, dst: str, duration: float):
        """Scale + pad a SadTalker output to exactly ANCHOR_W x ANCHOR_H."""
        cmd = [
            FFMPEG_EXE, "-y",
            "-i", src,
            "-vf", (
                f"scale={ANCHOR_W}:{ANCHOR_H}:force_original_aspect_ratio=decrease,"
                f"pad={ANCHOR_W}:{ANCHOR_H}:(ow-iw)/2:(oh-ih)/2:color=0x0a0f1e,format=yuv420p"
            ),
            "-t", str(duration),
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-an",  # audio added later in the compositor
            dst,
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _run_static_photo_anchor(self, audio_path: str, output_path: str, anchor_photo: str) -> str:
        """
        Creates a subtle zoom animation on the static photo.
        Better than a silhouette if SadTalker is unavailable.
        """
        try:
            duration = self._audio_duration(audio_path)
            # Subtle zoom filter
            zoom_vf = (
                f"zoompan=z='min(zoom+0.0005,1.5)':d={duration*30}:s={ANCHOR_W}x{ANCHOR_H}:fps=30,"
                f"drawtext=text='AI ANCHOR':fontfile='{FONT}':fontsize=22:fontcolor=white@0.8:x=20:y=20,"
                f"drawtext=text='VIRTUAL':fontfile='{FONT}':fontsize=14:fontcolor=gold@0.8:x=20:y=45"
            )
            
            cmd = [
                FFMPEG_EXE, "-y",
                "-loop", "1", "-i", anchor_photo,
                "-vf", zoom_vf,
                "-t", str(duration),
                "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                "-an",
                output_path
            ]
            logger.info("Rendering static photo anchor...")
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return output_path
            else:
                logger.error("Static photo anchor rendering failed or produced 0-byte file.")
                return ""
        except Exception:
            return ""

    # ── FFmpeg Silhouette (Option 2) ───────────────────────────────────────────

    def _run_ffmpeg_silhouette(self, audio_path: str, output_path: str, anchor_photo: str) -> str:
        """
        Creates an animated anchor silhouette using only FFmpeg.
        """
        try:
            # If we have a photo but SadTalker failed/is missing,
            # we can create a nice Ken-Burns style static zoom instead of a silhouette.
            if os.path.exists(anchor_photo):
                return self._run_static_photo_anchor(audio_path, output_path, anchor_photo)

            duration = self._audio_duration(audio_path)
            
            # Silhouette colours
            BG    = "0x0a0f1e"
            LIGHT = "0x111f3a"
            BODY  = "0x1e3a5f"
            HEAD  = "0x1e3a5f"

            # Pre-calculate all coordinates
            cx = ANCHOR_W // 2
            head_r = 60
            head_cy = ANCHOR_H // 3
            body_top = head_cy + head_r + 10
            body_bot = ANCHOR_H - 12
            
            spot_x = cx - 120
            spot_y = head_cy - 120
            head_x = cx - head_r
            head_y = head_cy - head_r
            head_w = head_r * 2
            
            # Safely handle fontfile argument for FFmpeg list syntax
            font_arg1 = f":fontfile='{FONT}'" if FONT else ""
            font_arg2 = f":fontfile='{FONT}'" if FONT else ""
            
            fg = (
                f"drawbox=x={spot_x}:y={spot_y}:w=240:h={ANCHOR_H}:color={LIGHT}@0.35:t=fill,"
                f"drawbox=x={cx-90}:y={body_top}:w=180:h={body_bot-body_top}:color={BODY}@0.9:t=fill,"
                f"drawbox=x={cx-70}:y={body_top-15}:w=140:h=30:color={BODY}@0.9:t=fill,"
                f"drawbox=x={head_x}:y={head_y}:w={head_w}:h={head_w}:color={HEAD}@0.95:t=fill,"
                f"drawbox=x=0:y={body_bot}:w={ANCHOR_W}:h=4:color=0x1a3a6a:t=fill,"
                # Labeling (omits fontfile= if FONT is empty)
                f"drawtext=text='AI ANCHOR'{font_arg1}:fontsize=14:fontcolor=0xf5a623@0.8:x=({ANCHOR_W}-text_w)/2:y={ANCHOR_H-35},"
                f"drawtext=text='LIVE'{font_arg2}:fontsize=10:fontcolor=0xcc0000@0.9:x=12:y=12"
            )

            cmd = [
                FFMPEG_EXE, "-y",
                "-f", "lavfi",
                "-i", f"color=c={BG}:s={ANCHOR_W}x{ANCHOR_H}:r=30:d={duration}",
                "-vf", fg,
                "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                "-an",
                output_path,
            ]

            logger.info("Rendering FFmpeg silhouette anchor...")
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                text=True, encoding='utf-8', errors='replace'
            )

            if result.returncode != 0 or not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                err_text = result.stderr if result.stderr else "No error output"
                logger.error(f"FFmpeg silhouette error or file missing/empty:\n{err_text[-1000:]}")
                # DEBUG: Write exactly why it failed to a public text file we can fetch
                with open("media/ffmpeg_error_log.txt", "w", encoding="utf-8") as f:
                    f.write(err_text)
                return ""

            logger.info(f"✅ FFmpeg silhouette anchor: {output_path}")
            return output_path

        except Exception as exc:
            logger.exception(f"FFmpeg silhouette error: {exc}")
            return ""

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _audio_duration(audio_path: str) -> float:
        try:
            r = subprocess.run(
                [FFPROBE_EXE, "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                text=True, encoding='utf-8', errors='replace'
            )
            return float(r.stdout.strip()) if r.stdout else 60.0
        except Exception:
            return 60.0


# ── Standalone test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    audio = sys.argv[1] if len(sys.argv) > 1 else "media/audio/test.mp3"
    out   = "media/anchor/test_anchor.mp4"
    gen   = AnchorGenerator()
    result = gen.generate_anchor_clip(audio, out)
    print(f"Anchor clip: {result}")

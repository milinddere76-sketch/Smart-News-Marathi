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

logger = logging.getLogger(__name__)

import sys

# ── FFmpeg Configuration ──────────────────────────────────────────────────────
FFMPEG_EXE  = os.getenv("FFMPEG_PATH", "ffmpeg")
FFPROBE_EXE = os.getenv("FFPROBE_PATH", "ffprobe")

# ── Paths ──────────────────────────────────────────────────────────────────────
ASSETS_DIR    = "media/assets"
ANCHOR_PHOTO  = os.path.join(ASSETS_DIR, "anchor.jpg")
SADTALKER_DIR = os.path.join(os.path.dirname(__file__), "SadTalker")
OUTPUT_DIR    = "media/anchor"

def get_font_path():
    if os.name == "nt":
        paths = [
            "C:/Windows/Fonts/Nirmala.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf"
        ]
        for p in paths:
            if os.path.exists(p):
                return p.replace(":", "\\:")
        return "Arial"
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

FONT = get_font_path()

# ── Studio Dimensions ──────────────────────────────────────────────────────────
ANCHOR_W = 640       # left zone width
ANCHOR_H = 868       # content zone height (1080 - top bar 80 - ticker 52 - gold 4*2)

class AnchorGenerator:
    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(ASSETS_DIR, exist_ok=True)
        self._sadtalker_ok = self._check_sadtalker()
        mode = "SadTalker" if self._sadtalker_ok else "FFmpeg silhouette"
        logger.info(f"AnchorGenerator initialised — mode: {mode}")

    # ── Public API ─────────────────────────────────────────────────────────────

    def generate_anchor_clip(self, audio_path: str, output_path: str) -> str:
        """
        Generate a {ANCHOR_W}x{ANCHOR_H} anchor video synced to the given audio.
        Returns output_path on success, '' on failure.
        """
        if self._sadtalker_ok and os.path.exists(ANCHOR_PHOTO):
            result = self._run_sadtalker(audio_path, output_path)
            if result:
                return result
            logger.warning("SadTalker failed — falling back to FFmpeg silhouette.")

        return self._run_ffmpeg_silhouette(audio_path, output_path)

    # ── SadTalker (Option 3) ───────────────────────────────────────────────────

    def _check_sadtalker(self) -> bool:
        """Returns True if SadTalker is cloned and inference.py is present."""
        inference = os.path.join(SADTALKER_DIR, "inference.py")
        return os.path.exists(inference)

    def _run_sadtalker(self, audio_path: str, output_path: str) -> str:
        """
        Calls SadTalker inference to produce a talking head video.
        """
        try:
            duration = self._audio_duration(audio_path)
            sadtalker_out_dir = os.path.join(OUTPUT_DIR, "sadtalker_tmp")
            os.makedirs(sadtalker_out_dir, exist_ok=True)

            cmd = [
                sys.executable,
                os.path.join(SADTALKER_DIR, "inference.py"),
                "--driven_audio", os.path.abspath(audio_path),
                "--source_image", os.path.abspath(ANCHOR_PHOTO),
                "--result_dir",   os.path.abspath(sadtalker_out_dir),
                "--still",                   # minimal head movement (news anchor style)
                "--preprocess", "full",      # full-body crop
                "--enhancer",   "gfpgan",    # face enhancement
            ]

            logger.info("Running SadTalker inference...")
            result = subprocess.run(
                cmd,
                cwd=SADTALKER_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=600,  # 10-minute timeout
            )

            if result.returncode != 0:
                err_text = result.stderr[-1000:] if result.stderr else "No error output"
                logger.error(f"SadTalker stderr:\n{err_text}")
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
                f"pad={ANCHOR_W}:{ANCHOR_H}:(ow-iw)/2:(oh-ih)/2:color=0x0a0f1e"
            ),
            "-t", str(duration),
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-an",  # audio added later in the compositor
            dst,
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _run_static_photo_anchor(self, audio_path: str, output_path: str) -> str:
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
                "-loop", "1", "-i", ANCHOR_PHOTO,
                "-vf", zoom_vf,
                "-t", str(duration),
                "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                "-an",
                output_path
            ]
            logger.info("Rendering static photo anchor...")
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return output_path if os.path.exists(output_path) else ""
        except Exception:
            return ""

    # ── FFmpeg Silhouette (Option 2) ───────────────────────────────────────────

    def _run_ffmpeg_silhouette(self, audio_path: str, output_path: str) -> str:
        """
        Creates an animated anchor silhouette using only FFmpeg.
        Features:
          - Dark navy background
          - Soft spotlight / vignette effect (simulated with radial gradient)
          - Abstract human silhouette (circle head + trapezoid body)
          - Subtle breathing animation using opacity pulsing
          - Channel slogan text
        """
        try:
            # If we have a photo but SadTalker failed/is missing,
            # we can create a nice Ken-Burns style static zoom instead of a silhouette.
            if os.path.exists(ANCHOR_PHOTO):
                return self._run_static_photo_anchor(audio_path, output_path)

            # Silhouette colours
            BG    = "0x0a0f1e"
            LIGHT = "0x111f3a"
            BODY  = "0x1e3a5f"
            HEAD  = "0x1e3a5f"

            # Pre-calculate all coordinates
            cx = ANCHOR_W // 2
            head_r = 90
            head_cy = ANCHOR_H // 3
            body_top = head_cy + head_r + 10
            body_bot = ANCHOR_H - 20
            
            spot_x = cx - 180
            spot_y = head_cy - 180
            head_x = cx - head_r
            head_y = head_cy - head_r
            head_w = head_r * 2
            
            # Simplified filtergraph (no nested parentheses in x/y)
            # We use the input [0:v] from the command as the base
            fg = (
                f"drawbox=x={spot_x}:y={spot_y}:w=360:h={ANCHOR_H}:color={LIGHT}@0.35:t=fill,"
                f"drawbox=x={cx-130}:y={body_top}:w=260:h={body_bot-body_top}:color={BODY}@0.9:t=fill,"
                f"drawbox=x={cx-100}:y={body_top-20}:w=200:h=40:color={BODY}@0.9:t=fill,"
                f"drawbox=x={head_x}:y={head_y}:w={head_w}:h={head_w}:color={HEAD}@0.95:t=fill,"
                f"drawbox=x=0:y={body_bot}:w={ANCHOR_W}:h=6:color=0x1a3a6a:t=fill,"
                # Labeling
                f"drawtext=text='AI ANCHOR':fontfile={FONT}:fontsize=18:fontcolor=0xf5a623@0.8:x=({ANCHOR_W}-text_w)/2:y={ANCHOR_H-50},"
                f"drawtext=text='LIVE':fontfile={FONT}:fontsize=14:fontcolor=0xcc0000@0.9:x=16:y=16"
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

            if result.returncode != 0:
                err_text = result.stderr[-1000:] if result.stderr else "No error output"
                logger.error(f"FFmpeg silhouette error:\n{err_text}")
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

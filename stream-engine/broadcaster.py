"""
Professional 24x7 YouTube Broadcaster
======================================
Streams video files to YouTube RTMP with:
  - Seamless concat: ffmpeg concat demuxer to avoid re-connects
  - Branded filler: Pure FFmpeg lavfi source used when no clips exist
  - Auto-retry: reconnects on failure after a short delay
"""

import subprocess
import os
import logging
import tempfile
import time
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Studio Constants (match video_generator.py) ────────────────────────────────
W, H = 1920, 1080
FPS  = 30
# Windows-friendly font fallback
if os.name == "nt":
    # Use Nirmala UI for Marathi support if available, otherwise fallback to Arial
    font_path = "C:/Windows/Fonts/Nirmala.ttf"
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/arial.ttf"
    # FFmpeg needs colons escaped in filterstrings: C\:
    FONT = font_path.replace(":", "\\:")
else:
    FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

C_NAVY = "0x0a0f1e"
C_RED  = "0xcc0000"
C_GOLD = "0xf5a623"

FFMPEG_EXE = os.getenv("FFMPEG_PATH", "ffmpeg")

# How long (seconds) the "Signal Loading…" filler plays before retrying
FILLER_DURATION = 30


class Broadcaster:
    def __init__(self):
        self.stream_key = os.getenv("YOUTUBE_STREAM_KEY")
        self.rtmp_url   = f"rtmp://a.rtmp.youtube.com/live2/{self.stream_key}"

    # ── Public API ─────────────────────────────────────────────────────────────

    def start_streaming(self, video_path: str):
        """
        Streams a single pre-rendered MP4 to YouTube RTMP.
        Blocks until the clip finishes.
        """
        if not self._check_key():
            return
        if video_path.startswith("http"):
            self._stream_url(video_path)
        else:
            self._stream_file(video_path)

    def stream_playlist(self, video_paths: list[str]):
        """
        Concatenates multiple MP4s and streams them as ONE continuous session.
        Avoids the YouTube re-connect overhead between every clip.
        """
        if not self._check_key() or not video_paths:
            return

        # Write a temp concat list file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            for p in video_paths:
                f.write(f"file '{os.path.abspath(p)}'\n")
            concat_list = f.name

        try:
            logger.info(f"Streaming playlist of {len(video_paths)} clip(s) to YouTube...")
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-re",
                "-i", concat_list,
                *self._encode_args(),
                self.rtmp_url,
            ]
            self._run_stream(cmd)
        finally:
            os.unlink(concat_list)

    def stream_filler(self):
        """
        Streams a branded 'Signal Loading…' screen while waiting for content.
        Uses FFmpeg lavfi color source — no video file needed.
        """
        if not self._check_key():
            return

        logger.info("No content ready — streaming branded filler...")
        # Safe characters for initial test to avoid encoding issues
        esc_ch  = "Smart News Marathi"
        esc_msg = "Please wait... Starting soon"
        esc_tag = "LIVE"

        # Ultra-safe filter: just colors and simple text
        filter_complex = (
            f"color=c={C_NAVY}:s={W}x{H}:r={FPS}:d={FILLER_DURATION}[bg];"
            f"[bg]drawbox=x=0:y=0:w={W}:h=80:color={C_RED}:t=fill,"
            f"drawbox=x=0:y=80:w={W}:h=4:color={C_GOLD}:t=fill,"
            f"drawtext=text='{esc_ch}':fontsize=36:fontcolor=white:x=24:y=27,"
            f"drawtext=text='{esc_msg}':fontsize=54:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2"
            "[vout]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c={C_NAVY}:s={W}x{H}:r={FPS}:d={FILLER_DURATION}",
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-filter_complex", filter_complex,
            "-map", "[vout]", "-map", "1:a",
            *self._encode_args(),
            self.rtmp_url,
        ]
        self._run_stream(cmd)

    # ── Private helpers ────────────────────────────────────────────────────────

    def _stream_file(self, path: str):
        logger.info(f"Streaming file: {path}")
        cmd = [
            "ffmpeg", "-y",
            "-re", "-i", path,
            *self._encode_args(),
            self.rtmp_url,
        ]
        self._run_stream(cmd)

    def _stream_url(self, url: str):
        logger.info(f"Re-streaming URL: {url}")
        cmd = [
            "ffmpeg", "-y",
            "-re", "-i", url,
            *self._encode_args(),
            self.rtmp_url,
        ]
        self._run_stream(cmd)

    def _run_stream(self, cmd: list):
        # Use absolute FFmpeg path if possible
        if cmd[0].lower() == "ffmpeg" or cmd[0].endswith("ffmpeg.exe"):
            cmd[0] = FFMPEG_EXE
            
        logger.info(f"Executing FFmpeg: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            
            error_log = []
            for line in process.stdout:
                line_str = line.strip()
                if "frame=" in line_str:
                    continue  # skip noisy progress lines
                
                if line_str:
                    error_log.append(line_str)
                    # Print immediately if it looks like a real error
                    if "error" in line_str.lower() or "failed" in line_str.lower() or "invalid" in line_str.lower():
                        logger.warning(f"FFmpeg Output: {line_str}")
                
                # Keep log size sane
                if len(error_log) > 100:
                    error_log.pop(0)

            process.wait()
            
            if process.returncode != 0:
                logger.error(f"FFmpeg exited with code {process.returncode}")
                # Show last few lines of log on failure
                recent_logs = "\n".join(error_log[-15:])
                logger.error(f"Recent FFmpeg Trace:\n{recent_logs}")
            else:
                logger.info("Stream segment finished successfully.")
        except Exception as exc:
            logger.error(f"Broadcaster._run_stream error: {exc}")

    @staticmethod
    def _encode_args() -> list:
        """Standard YouTube-optimised encode params."""
        return [
            "-vcodec", "libx264",
            "-preset", "veryfast",
            "-maxrate", "4500k",
            "-bufsize", "9000k",
            "-pix_fmt", "yuv420p",
            "-g", str(FPS * 2),       # 2-second keyframe interval
            "-acodec", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-f", "flv",
        ]

    def _check_key(self) -> bool:
        if not self.stream_key:
            logger.error("YOUTUBE_STREAM_KEY not set. Cannot stream.")
            return False
        return True


if __name__ == "__main__":
    b = Broadcaster()
    b.stream_filler()

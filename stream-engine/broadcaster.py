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
from dotenv import load_dotenv  # type: ignore

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Studio Constants (match video_generator.py) ────────────────────────────────
W, H = 1280, 720
FPS  = 30
def get_font_path():
    """
    Returns a font path that works for both:
      - Local Windows (uses copy at D:/snm_font.ttf)
      - Cloud Linux/Docker (uses installed Noto Devanagari for Marathi)
    """
    import platform
    
    if platform.system() == "Linux":
        # Linux (Fly.io, Docker) — use installed Noto fonts for Marathi/Devanagari
        linux_candidates = [
            "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for path in linux_candidates:
            if os.path.exists(path):
                # FFmpeg needs the colon escaped on windows, but NOT on Linux
                return path
        # Last resort on Linux
        return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    
    # Windows path — copy to a space-free location
    no_space_font = "D:/snm_font.ttf"
    if not os.path.exists(no_space_font):
        for src in ["D:/Apps/Smart News Marathi/backend/media/assets/news_font.ttf",
                    "C:/Windows/Fonts/nirmala.ttf",
                    "C:/Windows/Fonts/Nirmala.ttf",
                    "C:/Windows/Fonts/arial.ttf"]:
            if os.path.exists(src):
                try:
                    import shutil
                    shutil.copy(src, no_space_font)
                    break
                except Exception:
                    pass

    if os.path.exists(no_space_font):
        return no_space_font.replace(":", "\\:")
    for p in ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/Nirmala.ttf"]:
        if os.path.exists(p):
            return p.replace(":", "\\:")
    return "Arial"

FONT = get_font_path()

C_NAVY = "0x0a0f1e"
C_RED  = "0xcc0000"
C_GOLD = "0xf5a623"

FFMPEG_EXE = os.getenv("FFMPEG_PATH", "ffmpeg")

# How long (seconds) the "Signal Loading…" filler plays before retrying
FILLER_DURATION = 600


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
                # IMPORTANT: FFmpeg concat demuxer on Windows prefers forward slashes
                clean_path = p if p.startswith("http") else os.path.abspath(p).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")
            concat_list = f.name

        try:
            logger.info(f"Streaming playlist of {len(video_paths)} clip(s) to YouTube...")
            cmd = [
                FFMPEG_EXE, "-y",
                "-protocol_whitelist", "file,http,https,tcp,tls,rtmp",
                "-f", "concat",
                "-safe", "0",
                "-re",
                "-i", concat_list,
                "-map", "0:v", "-map", "0:a?",
                *self._encode_args(),
                self.rtmp_url,
            ]
            self._run_stream(cmd)
        finally:
            if os.path.exists(concat_list):
                os.unlink(concat_list)

    def stream_filler(self):
        """
        Streams a branded 'Channel Dashboard' or local promo video.
        """
        if not self._check_key():
            return

        # Priority 1: Use local promotion video if it exists (loops indefinitely until news ready)
        promo_path = os.getenv("PROMO_VIDEO_PATH", "media/assets/promo.mp4")
        if os.path.exists(promo_path):
            logger.info("Streaming Promotion Video as filler...")
            # We use -stream_loop -1 without -t here because the Streamer 
            # will kill the process when news is ready, or use stream_video_loop for fixed durations.
            cmd = [
                FFMPEG_EXE, "-y",
                "-re",
                "-stream_loop", "-1",
                "-i", promo_path,
                *self._encode_args(),
                self.rtmp_url,
            ]
            self._run_stream(cmd)
            return

        # Fallback: Generated Screen
        filter_complex = (
            f"color=c={C_NAVY}:s={W}x{H}:r={FPS}:d={FILLER_DURATION}[bg];"
            f"[bg]"
            # ... existing screen logic ...
            f"drawbox=x=0:y=0:w={W}:h=72:color={C_RED}:t=fill,"
            f"drawbox=x=0:y=72:w={W}:h=4:color={C_GOLD}:t=fill,"
            f"drawtext=fontfile='{FONT}':text='VARTAPRAVAH 24x7':fontsize=34:fontcolor=white:x=24:y=20,"
            f"drawtext=fontfile='{FONT}':text='COMING SOON - Lavkarach Yet Ahot':fontsize=22:fontcolor={C_GOLD}:x=24:y=52,"
            f"drawtext=fontfile='{FONT}':text='Latest Marathi News Starting Shortly...':fontsize=40:fontcolor=white:"
            f"x=(w-text_w)/2:y=(h-text_h)/2-20,"
            f"drawtext=fontfile='{FONT}':text='Subscribe to VARTAPRAVAH on YouTube':fontsize=26:fontcolor={C_GOLD}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2+40"
            f"[vout]"
        )

        cmd = [
            FFMPEG_EXE, "-y",
            "-f", "lavfi", "-i", f"color=c={C_NAVY}:s={W}x{H}:r={FPS}:d={FILLER_DURATION}",
            "-f", "lavfi", "-i", f"anoisesrc=d={FILLER_DURATION}:c=pink:a=0.1",
            "-filter_complex", filter_complex,
            "-map", "[vout]", "-map", "1:a",
            *self._encode_args(),
            self.rtmp_url,
        ]
        logger.info("Streaming Generated filler to YouTube...")
        self._run_stream(cmd)

    def stream_video_loop(self, path: str, duration_sec: int):
        """
        Loops a video file for a fixed duration.
        """
        if not self._check_key():
            return
        
        logger.info(f"Streaming looped file: {path} for {duration_sec}s")
        cmd = [
            FFMPEG_EXE, "-y",
            "-re",
            "-stream_loop", "-1",
            "-i", path,
            "-t", str(duration_sec),
            *self._encode_args(),
            self.rtmp_url,
        ]
        self._run_stream(cmd)

    # ── Private helpers ────────────────────────────────────────────────────────

    def _stream_file(self, path: str):
        logger.info(f"Streaming file: {path}")
        cmd = [
            FFMPEG_EXE, "-y",
            "-protocol_whitelist", "file,http,https,tcp,tls,rtmp",
            "-re", "-i", path,
            *self._encode_args(),
            self.rtmp_url,
        ]
        self._run_stream(cmd)

    def _stream_url(self, url: str):
        logger.info(f"Re-streaming URL: {url}")
        cmd = [
            FFMPEG_EXE, "-y",
            "-protocol_whitelist", "file,http,https,tcp,tls,rtmp",
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
        
        log_file = "broadcaster_ffmpeg.log"
        try:
            with open(log_file, "wb") as f_out:
                process = subprocess.Popen(
                    cmd,
                    stdout=f_out,
                    stderr=subprocess.STDOUT,
                    bufsize=0,
                )
                
                logger.info(f"Broadcaster: FFmpeg started (PID: {process.pid}). Monitoring log: {log_file}...")
                
                # Wait for the process to complete or be interrupted
                process.wait()
                
            if process.returncode != 0:
                logger.error(f"FFmpeg failed with exit code {process.returncode}")
                # Read the log file at the end
                try:
                    with open(log_file, "r", encoding='utf-8', errors='replace') as f_err:
                        lines = f_err.readlines()
                        logger.error("Recent FFmpeg output:")
                        for line in lines[-20:]:
                            logger.error(f"  > {line.strip()}")
                except Exception as e:
                    logger.error(f"Could not read FFmpeg log: {e}")
            else:
                logger.info("Stream segment finished successfully.")
        except Exception as exc:
            logger.error(f"Broadcaster._run_stream error: {exc}")

    @staticmethod
    def _encode_args() -> list:
        """Optimal YouTube RTMP settings for 720p30 streaming with Anti-Buffering."""
        return [
            "-nostdin",
            "-hide_banner",
            "-loglevel", "info",       # Light logging
            "-c:v", "libx264",
            "-preset", "ultrafast",     # Essential for real-time performance
            "-tune", "zerolatency",
            "-threads", "0",            # Use all available CPU cores
            "-r", str(FPS),
            "-s", f"{W}x{H}",
            "-b:v", "2500k",
            "-minrate", "2500k",
            "-maxrate", "2500k",
            "-bufsize", "5000k",
            "-x264-params", "nal-hrd=cbr:force-cfr=1:sync-lookahead=0", 
            "-pix_fmt", "yuv420p",
            "-g", str(FPS * 2),
            "-flags", "+global_header",
            "-af", "aresample=async=1:min_hard_comp=0.1:first_pts=0",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-ac", "2",
            "-f", "flv",
            "-flvflags", "no_duration_filesize",
            "-max_muxing_queue_size", "1024"
        ]

    def _check_key(self) -> bool:
        if not self.stream_key:
            logger.error("YOUTUBE_STREAM_KEY not set. Cannot stream.")
            return False
        return True


if __name__ == "__main__":
    b = Broadcaster()
    b.stream_filler()

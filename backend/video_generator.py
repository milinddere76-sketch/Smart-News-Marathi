"""
Professional News Studio Video Compositor — with Virtual Anchor
================================================================
Generates broadcast-quality 1080p30 news clips using FFmpeg's complex filtergraph.
When an anchor_video_path is provided, it appears in the left 1/3 of the content zone.

Studio Layout — 1920x1080:
┌─────────────────────────────────────────────────────────────────┐
│  [LOGO]  स्मार्ट न्यूज मराठी         ● LIVE          [TIME]     │ ← Top bar (80px, red)
├──────────────────┬──────────────────────────────────────────────┤
│                  │                                              │
│  ANCHOR VIDEO    │   NEWS HEADLINE / CONTENT ZONE              │
│   (640x868px)    │         (1280px wide)                        │
│                  │   ─ Lower-third: BREAKING + headline         │
│                  │   ─ Slogan                                   │
├──────────────────┴──────────────────────────────────────────────┤
│  ताज्या बातम्या ›  [scrolling ticker text]                       │ ← Ticker (52px)
└─────────────────────────────────────────────────────────────────┘
"""

import subprocess
import os
import logging
import time
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Studio Design Constants ────────────────────────────────────────────────────
W, H  = 1280, 720
FPS   = 30
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
            "C:/Windows/Fonts/nirmala.ttf",
            "C:/Windows/Fonts/Nirmala.ttf",
            "C:/Windows/Fonts/arial.ttf"
        ]
        for pf in source_fonts:
            if os.path.exists(pf):
                try:
                    shutil.copy(pf, no_space_font)
                    logger.info(f"Copied font to space-free path: {no_space_font}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to copy font {pf}: {e}")

    if os.path.exists(no_space_font):
        return no_space_font.replace(":", "\\:")
    
    # Fallback to system fonts at a safe path
    for p in ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/Nirmala.ttf"]:
        if os.path.exists(p):
            return p.replace(":", "\\:")

    return ""  # Empty string = FFmpeg uses default font

FONT = get_font_path()

TOP_BAR_H  = 70
TICKER_H   = 45
GOLD       = 3             # gold accent line height
CONTENT_H  = 602           # 720 - 70 - 3 - 45 = 602
ANCHOR_W   = 420           # approx 1/3 of 1280
NEWS_X     = ANCHOR_W      
NEWS_W     = W - ANCHOR_W  

LOWER_H    = 150           
LOWER_Y    = H - TICKER_H - LOWER_H

TICKER_SPEED = 240

# Colours
C_NAVY     = "0x0a0f1e"
C_PANEL    = "0x0d1528"
C_ANCHOR   = "0x080d18"   # anchor zone background
C_RED      = "0xcc0000"
C_RED_DARK = "0x8b0000"
C_GOLD     = "0xf5a623"
C_WHITE    = "0xffffff"
C_BLACK    = "0x000000"
C_TICKER   = "0x0d0d0d"


# ── FFmpeg Configuration ──────────────────────────────────────────────────────
_env_ffmpeg = os.getenv("FFMPEG_PATH", "ffmpeg")
_env_ffprobe = os.getenv("FFPROBE_PATH", "ffprobe")

# Robust check: if the env path doesn't exist, use the command name (for Linux/Docker)
FFMPEG_EXE = _env_ffmpeg if os.path.exists(_env_ffmpeg) else "ffmpeg"
FFPROBE_EXE = _env_ffprobe if os.path.exists(_env_ffprobe) else "ffprobe"

logger.info(f"Using FFmpeg: {FFMPEG_EXE}")


class VideoGenerator:
    def __init__(self):
        self.output_dir = "media/video"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs("media/assets", exist_ok=True)

    # ── Public API ─────────────────────────────────────────────────────────────

    def create_news_clip(
        self,
        audio_path: str,
        headline: str,
        ticker_text: str,
        output_filename: str,
        anchor_video_path: Optional[str] = None,
        category: str = "Breaking News",
    ) -> str:
        """
        Renders a professional 720p30 broadcast news clip.
        anchor_video_path: pre-rendered anchor video (optional).
        Returns the output file path on success, or '' on failure.
        """
        output_path = os.path.join(self.output_dir, output_filename)
        temp_path = output_path.replace(".mp4", "_temp.mp4")

        try:
            duration = self._get_audio_duration(audio_path)
            if duration <= 0:
                duration = 60

            logger.info(
                f"Compositing studio clip | anchor={'YES' if anchor_video_path else 'NO'} "
                f"| duration={duration:.1f}s"
            )

            hl  = self._esc(headline)
            tkr = self._esc("वार्ताप्रवाह (VARTAPRAVAH) — " + ticker_text)
            ch  = self._esc("वार्ताप्रवाह | VartaPravah")
            brk = self._esc("BREAKING NEWS")
            slg = self._esc("सत्य · निर्भय · निष्पक्ष")
            now = time.strftime("%H\\:%M  %d %b %Y")

            # Verify FFmpeg exists
            import shutil
            if not shutil.which(FFMPEG_EXE):
                logger.error(f"CRITICAL: {FFMPEG_EXE} not found. Please set FFMPEG_PATH in .env or add it to your system PATH and restart your terminal.")
                return ""

            has_anchor = (
                anchor_video_path
                and os.path.exists(anchor_video_path)
            )

            # Check if we have a b-roll background for this category
            assets_dir = "backend/media/assets" if os.path.exists("backend/media/assets") else "media/assets"
            bg_path = os.path.abspath(f"{assets_dir}/bg_{category}.jpg")
            
            # Brain directory fallback for backgrounds
            BRAIN_DIR = r"C:\Users\Priyansh Dere\.gemini\antigravity\brain\4c6ecebf-949b-4e1b-8a17-265d9ccfda14"
            BG_FALLBACKS = {
                "Breaking News": "bg_breaking_1773086956279.png",
                "Technology": "bg_tech_1773086971821.png",
                "India": "bg_india_1773086989515.png"
            }

            if not os.path.exists(bg_path) and category in BG_FALLBACKS:
                fb_path = os.path.join(BRAIN_DIR, BG_FALLBACKS[category])
                if os.path.exists(fb_path):
                    bg_path = fb_path

            has_bg = os.path.exists(bg_path)
            
            # Logo Check
            logo_path = os.path.abspath(f"{assets_dir}/channel_logo.png")
            has_logo = os.path.exists(logo_path)

            if has_anchor:
                logger.info(f"Anchor file detected: {anchor_video_path}")
                cmd = self._build_cmd_with_anchor(
                    audio_path, anchor_video_path, temp_path,
                    duration, hl, tkr, ch, brk, slg, now,
                    bg_path if has_bg else None,
                    logo_path if has_logo else None
                )
            else:
                logger.warning(f"No anchor file found at: {anchor_video_path}")
                cmd = self._build_cmd_no_anchor(
                    audio_path, temp_path,
                    duration, hl, tkr, ch, brk, slg, now,
                    bg_path if has_bg else None,
                    logo_path if has_logo else None
                )

            logger.info(f"FFmpeg Command: {' '.join(cmd)}")
            logger.info("Running FFmpeg studio compositor...")
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                text=True, encoding='utf-8', errors='replace'
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg failed with code {result.returncode}")
                if result.stderr:
                    logger.error(f"FFmpeg stderr: {result.stderr[-1000:]}")  # type: ignore
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return ""

            if os.path.exists(temp_path):
                os.rename(temp_path, output_path)
                logger.info(f"✅ Studio clip ready: {output_path}")
            else:
                logger.error(f"FFmpeg claimed success but output file missing: {temp_path}")
                return ""
            
            return output_path

        except Exception as exc:
            import traceback
            logger.error(f"create_news_clip failed: {exc}")
            logger.error(traceback.format_exc())
            return ""

    def create_promo_clip(self, output_filename: str) -> str:
        """
        Generates a 10-second high-energy promotional clip urging viewers to subscribe.
        Returns the output file path.
        """
        output_path = os.path.join(self.output_dir, output_filename)
        temp_path = output_path + ".tmp"
        try:
            duration = 10
            safe_font = FONT

            # Dynamic zoom background + text animations
            filter_complex = (
                f"color=c={C_NAVY}:s={W}x{H}:d={duration}[bg];"
                # Animated Sub/Like Box
                f"color=c={C_RED}:s=600x120:d={duration}[box];"
                f"[bg][box]overlay=x=(W-w)/2:y=(H-h)/2+100[bg1];"
                # Text Layers
                f"[bg]drawtext=text='VARTAPRAVAH':fontfile='{safe_font}':fontsize=45:fontcolor={C_WHITE}:"
                f"x=(w-text_w)/2:y=(h-text_h)/2-60:text_shaping=1:"
                f"shadowcolor=black:shadowx=2:shadowy=2[bg2];"
                
                f"[bg2]drawtext=text='सत्य · निर्भय · निष्पक्ष':fontfile='{safe_font}':fontsize=20:fontcolor={C_GOLD}:"
                f"x=(w-text_w)/2:y=(h-text_h)/2-20:text_shaping=1[bg3];"
                
                f"[bg3]drawtext=text='SUBSCRIBE NOW':fontfile='{safe_font}':fontsize=30:fontcolor={C_WHITE}:"
                f"x=(w-text_w)/2:y=(h-text_h)/2+50:text_shaping=1[vout]"
            )

            cmd = [
                FFMPEG_EXE, "-y",
                "-f", "lavfi", "-i", f"anoisesrc=d={duration}:c=pink:a=0.1", # silent pink noise for audio track
                "-filter_complex", filter_complex,
                "-map", "[vout]", "-map", "0:a",
                "-c:v", "libx264", "-preset", "ultrafast", "-threads", "2",
                "-b:v", "3000k", "-maxrate", "3000k", "-minrate", "3000k",
                "-bufsize", "6000k", "-x264-params", "nal-hrd=cbr",
                "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                "-t", str(duration),
                "-movflags", "+faststart",
                temp_path
            ]
            
            logger.info("Generating Promo Clip...")
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                text=True, encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0 and os.path.exists(temp_path):
                os.rename(temp_path, output_path)
                logger.info(f"✅ Promo clip ready: {output_path}")
                return output_path
            elif os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            logger.error(f"Failed to generate promo clip: {e}")
            
        return ""

    # ── Build FFmpeg commands ──────────────────────────────────────────────────

    def _build_cmd_with_anchor(
        self, audio, anchor_vid, output,
        duration, hl, tkr, ch, brk, slg, now, bg_image=None, logo_image=None
    ):
        """Builds FFmpeg command with anchor video and branding."""
        graphics = self._studio_graphics(
            has_anchor=True, duration=duration,
            hl=hl, tkr=tkr, ch=ch, brk=brk, slg=slg, now=now, has_bg=bool(bg_image)
        )

        inputs = [
            "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={duration}",
            "-stream_loop", "-1", "-i", anchor_vid
        ]
        
        bg_idx = ""
        anchor_idx = "[1:v]"
        audio_idx = "2:a"
        last_idx = 2

        if bg_image:
            inputs.extend(["-loop", "1", "-i", bg_image])
            last_idx += 1
            bg_idx = f"[{last_idx}:v]scale={W}:{H},setpts=PTS-STARTPTS[broll];[0:v][broll]overlay=0:0[canvas];"
            audio_idx = f"{last_idx+1}:a"
        else:
            bg_idx = "[0:v]copy[canvas];"
            
        inputs.extend(["-i", audio])
        audio_in_idx = last_idx + 1
        
        logo_overlay = ""
        if logo_image:
            inputs.extend(["-i", logo_image])
            logo_idx = audio_in_idx + 1
            logo_overlay = f"[{logo_idx}:v]scale=90:-1[logo];[vout_pre][logo]overlay=10:5[vout];"
            audio_final_idx = f"{audio_in_idx}:a"
        else:
            logo_overlay = "[vout_pre]copy[vout];"
            audio_final_idx = f"{audio_in_idx}:a"

        filter_complex = (
            f"{bg_idx}"
            f"[canvas]{graphics}[bg_g];"
            f"{anchor_idx}scale={ANCHOR_W}:{CONTENT_H}:force_original_aspect_ratio=decrease,format=yuv420p,"
            f"pad={ANCHOR_W}:{CONTENT_H}:(ow-iw)/2:(oh-ih)/2:color={C_ANCHOR}[av];"
            f"[bg_g][av]overlay=0:{TOP_BAR_H}[vout_pre];"
            f"{logo_overlay}"
        )

        return [
            FFMPEG_EXE, "-y",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", audio_final_idx,
            "-c:v", "libx264", "-preset", "ultrafast", "-threads", "2",
            "-b:v", "3000k", "-maxrate", "3000k", "-minrate", "3000k",
            "-bufsize", "6000k", "-x264-params", "nal-hrd=cbr",
            "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
            "-t", str(duration),
            "-f", "mp4",
            "-movflags", "+faststart",
            output,
        ]

    def _build_cmd_no_anchor(
        self, audio, output,
        duration, hl, tkr, ch, brk, slg, now, bg_image=None, logo_image=None
    ):
        """Single canvas source — full-width layout, no anchor zone."""
        graphics = self._studio_graphics(
            has_anchor=False, duration=duration,
            hl=hl, tkr=tkr, ch=ch, brk=brk, slg=slg, now=now, has_bg=bool(bg_image)
        )

        inputs = [
            "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={duration}",
        ]
        
        bg_idx = ""
        last_idx = 0
        if bg_image:
            inputs.extend(["-loop", "1", "-i", bg_image])
            last_idx += 1
            bg_idx = f"[{last_idx}:v]scale={W}:{H},setpts=PTS-STARTPTS[broll];[0:v][broll]overlay=0:0[canvas];"
        else:
            bg_idx = "[0:v]copy[canvas];"
            
        inputs.extend(["-i", audio])
        audio_in_idx = last_idx + 1

        logo_overlay = ""
        if logo_image:
            inputs.extend(["-i", logo_image])
            logo_idx = audio_in_idx + 1
            logo_overlay = f"[{logo_idx}:v]scale=90:-1[logo];[vout_pre][logo]overlay=10:5[vout];"
            audio_final_idx = f"{audio_in_idx}:a"
        else:
            logo_overlay = "[vout_pre]copy[vout];"
            audio_final_idx = f"{audio_in_idx}:a"

        filter_complex = f"{bg_idx}[canvas]{graphics}[vout_pre];{logo_overlay}"

        return [
            FFMPEG_EXE, "-y",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", audio_final_idx,
            "-c:v", "libx264", "-preset", "ultrafast", "-threads", "2",
            "-b:v", "3000k", "-maxrate", "3000k", "-minrate", "3000k",
            "-bufsize", "6000k", "-x264-params", "nal-hrd=cbr",
            "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
            "-shortest",
            "-f", "mp4",
            "-movflags", "+faststart",
            output,
        ]

    # ── Studio Filtergraph ─────────────────────────────────────────────────────

    def _studio_graphics(
        self, has_anchor: bool, duration: float,
        hl, tkr, ch, brk, slg, now, has_bg: bool = False
    ) -> str:
        """Returns the drawbox/drawtext chain."""
        TEXT_X = f"{NEWS_X + 20}" if has_anchor else "24"
        TEXT_W = NEWS_W if has_anchor else W

        LOWER_TEXT_Y1 = LOWER_Y + 10
        LOWER_TEXT_Y2 = LOWER_Y + 50
        TICKER_TEXT_Y = int(H - TICKER_H + (TICKER_H - 20) / 2)

        safe_font = FONT
        bg_color_layer = f"drawbox=x=0:y=0:w={W}:h={H}:color={C_NAVY}:t=fill," if not has_bg else ""
        
        anchor_panel = ""
        if not has_anchor and not has_bg:
            anchor_panel = f"drawbox=x=0:y={TOP_BAR_H}:w={W}:h={CONTENT_H}:color={C_PANEL}:t=fill,"

        fg = (
            bg_color_layer + 
            anchor_panel +
            f"drawbox=x=0:y=0:w={W}:h={TOP_BAR_H}:color={C_RED}:t=fill,"
            f"drawbox=x=0:y={TOP_BAR_H}:w={W}:h={GOLD}:color={C_GOLD}:t=fill,"

            # Dual-language Channel Name
            f"drawtext=text='{ch}':fontfile='{safe_font}':fontsize=22:fontcolor={C_WHITE}:"
            f"x=115:y=({TOP_BAR_H}-text_h)/2-10:text_shaping=1,"

            # Blinking LIVE indicator below logo
            f"drawtext=text='● LIVE':fontfile='{safe_font}':fontsize=16:fontcolor={C_GOLD}:"
            f"box=1:boxcolor={C_BLACK}@0.5:boxborderw=4:"
            f"x=115:y=({TOP_BAR_H}-text_h)/2+15:text_shaping=1:enable='lt(mod(t,1),0.6)',"

            f"drawtext=text='{now}':fontfile='{safe_font}':fontsize=21:fontcolor={C_WHITE}@0.85:"
            f"x=({W}-text_w-18):y=({TOP_BAR_H}-text_h)/2:text_shaping=1,"

            f"drawbox=x=0:y={LOWER_Y}:w={W}:h={LOWER_H}:color={C_NAVY}@0.92:t=fill,"
            f"drawbox=x=0:y={LOWER_Y}:w={W}:h=6:color={C_RED}:t=fill,"
            f"drawbox=x=0:y={LOWER_Y + 3}:w=240:h=50:color={C_RED}:t=fill,"
            f"drawtext=text='{brk}':fontfile='{safe_font}':fontsize=21:fontcolor={C_WHITE}:"
            f"x=15:y={LOWER_Y + 3 + 18}:text_shaping=1,"

            f"drawtext=text='{hl}':fontfile='{safe_font}':fontsize=30:fontcolor={C_WHITE}:"
            f"x=260:y={LOWER_TEXT_Y1}:text_shaping=1,"

            f"drawtext=text='{slg}':fontfile='{safe_font}':fontsize=21:fontcolor={C_GOLD}@0.9:"
            f"x=260:y={LOWER_TEXT_Y2+10}:text_shaping=1,"

            f"drawbox=x=0:y={H - TICKER_H}:w={W}:h={TICKER_H}:color={C_TICKER}:t=fill,"
            f"drawbox=x=0:y={H - TICKER_H}:w=180:h={TICKER_H}:color={C_RED}:t=fill,"
            f"drawtext=text='ताज्या बातम्या':fontfile='{safe_font}':fontsize=21:fontcolor={C_WHITE}:"
            f"x=12:y={TICKER_TEXT_Y}:text_shaping=1,"

            f"drawtext=text='  {tkr}  ●  {tkr}  ':fontfile='{safe_font}':fontsize=21:fontcolor={C_WHITE}:"
            f"x={W}-mod(t*{TICKER_SPEED}\\,{W}+text_w):y={TICKER_TEXT_Y}:text_shaping=1,"

            f"drawbox=x=0:y={H - TICKER_H}:w={W}:h=2:color={C_GOLD}:t=fill"
        )
        return fg

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _get_audio_duration(audio_path: str) -> float:
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

    @staticmethod
    def _esc(text: str) -> str:
        text = text.replace("\\", "\\\\")
        text = text.replace("'",  "\u2019")
        text = text.replace(":",  "\\:")
        text = text.replace("%",  "\\%")
        return text


# ── Standalone test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    vg = VideoGenerator()
    audio   = sys.argv[1] if len(sys.argv) > 1 else "media/audio/test.mp3"
    anchor  = sys.argv[2] if len(sys.argv) > 2 else None
    headline = "महाराष्ट्रातील मोठी बातमी: राज्यपालांनी महत्त्वाचा निर्णय घेतला"
    ticker   = "| मुंबई: पावसाचा इशारा | पुणे: मेट्रो उद्घाटन | सेन्सेक्स उच्चांकी |"
    out = vg.create_news_clip(audio, headline, ticker, "studio_test.mp4", anchor)
    print(f"Output: {out}")

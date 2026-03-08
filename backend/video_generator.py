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
W, H  = 1920, 1080
FPS   = 30
# Windows-friendly font fallback
if os.name == "nt":
    # On Windows, FFmpeg can usually find "Arial" if specified directly
    FONT = "Arial"
else:
    FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

TOP_BAR_H  = 80
TICKER_H   = 52
GOLD       = 4             # gold accent line height
CONTENT_H  = H - TOP_BAR_H - GOLD - TICKER_H   # 1080-80-4-52 = 944
ANCHOR_W   = 640           # anchor zone width (left third)
NEWS_X     = ANCHOR_W      # news graphics start x
NEWS_W     = W - ANCHOR_W  # 1280px

LOWER_H    = 220           # lower-third panel height
LOWER_Y    = H - TICKER_H - LOWER_H  # y where lower-third panel starts

TICKER_SPEED = 180

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
FFMPEG_EXE  = os.getenv("FFMPEG_PATH", "ffmpeg")
FFPROBE_EXE = os.getenv("FFPROBE_PATH", "ffprobe")

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
    ) -> str:
        """
        Renders a professional 1080p30 broadcast news clip.
        anchor_video_path: pre-rendered 640xH anchor video (optional).
        Returns the output file path on success, or '' on failure.
        """
        output_path = os.path.join(self.output_dir, output_filename)

        try:
            duration = self._get_audio_duration(audio_path)
            if duration <= 0:
                duration = 60

            logger.info(
                f"Compositing studio clip | anchor={'YES' if anchor_video_path else 'NO'} "
                f"| duration={duration:.1f}s"
            )

            hl  = self._esc(headline)
            tkr = self._esc(ticker_text)
            ch  = self._esc("स्मार्ट न्यूज मराठी")
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

            if has_anchor:
                logger.info(f"Anchor file detected: {anchor_video_path}")
                cmd = self._build_cmd_with_anchor(
                    audio_path, anchor_video_path, output_path,
                    duration, hl, tkr, ch, brk, slg, now
                )
            else:
                logger.warning(f"No anchor file found at: {anchor_video_path}")
                cmd = self._build_cmd_no_anchor(
                    audio_path, output_path,
                    duration, hl, tkr, ch, brk, slg, now
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
                    logger.error(f"FFmpeg stderr: {result.stderr[-1000:]}")
                return ""

            if os.path.exists(output_path):
                logger.info(f"✅ Studio clip ready: {output_path}")
            else:
                logger.error(f"FFmpeg claimed success but output file missing: {output_path}")
                return ""
            
            return output_path

        except Exception as exc:
            import traceback
            logger.error(f"create_news_clip failed: {exc}")
            logger.error(traceback.format_exc())
            return ""

    # ── Build FFmpeg commands ──────────────────────────────────────────────────

    def _build_cmd_with_anchor(
        self, audio, anchor_vid, output,
        duration, hl, tkr, ch, brk, slg, now
    ):
        """Two-input FFmpeg: canvas + anchor video overlaid on left zone."""

        # The filter graph:
        # [0:v] = black canvas
        # [1:v] = anchor video
        # Step 1: draw all static studio graphics onto canvas → [bg]
        # Step 2: overlay anchor video onto left zone → [vout]
        graphics = self._studio_graphics(
            has_anchor=True, duration=duration,
            hl=hl, tkr=tkr, ch=ch, brk=brk, slg=slg, now=now
        )

        filter_complex = (
            f"[0:v]{graphics}[bg];"
            # Scale anchor to fit zone exactly
            f"[1:v]scale={ANCHOR_W}:{CONTENT_H + GOLD}:force_original_aspect_ratio=decrease,"
            f"pad={ANCHOR_W}:{CONTENT_H + GOLD}:(ow-iw)/2:(oh-ih)/2:color={C_ANCHOR}[av];"
            # Overlay anchor on left zone, starting below top bar
            f"[bg][av]overlay=0:{TOP_BAR_H}[vout]"
        )

        return [
            FFMPEG_EXE, "-y",
            "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={duration}",
            "-stream_loop", "-1", "-i", anchor_vid,
            "-i", audio,
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "2:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
            "-t", str(duration),
            "-movflags", "+faststart",
            output,
        ]

    def _build_cmd_no_anchor(
        self, audio, output,
        duration, hl, tkr, ch, brk, slg, now
    ):
        """Single canvas source — full-width layout, no anchor zone."""

        graphics = self._studio_graphics(
            has_anchor=False, duration=duration,
            hl=hl, tkr=tkr, ch=ch, brk=brk, slg=slg, now=now
        )

        filter_complex = f"[0:v]{graphics}[vout]"

        return [
            FFMPEG_EXE, "-y",
            "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={duration}",
            "-i", audio,
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
            "-shortest",
            "-movflags", "+faststart",
            output,
        ]

    # ── Studio Filtergraph ─────────────────────────────────────────────────────

    def _studio_graphics(
        self, has_anchor: bool, duration: float,
        hl, tkr, ch, brk, slg, now
    ) -> str:
        """
        Returns the drawbox/drawtext chain.
        When has_anchor=True, the left 640px is reserved for the anchor overlay
        and text/graphics are pushed to the right zone.
        """

        # x offsets depend on anchor presence
        TEXT_X = f"{NEWS_X + 20}" if has_anchor else "24"
        TEXT_W = NEWS_W if has_anchor else W

        # ── Pre-calculate coordinates to avoid f-string parsing issues ────────
        CENTER_Y = (TOP_BAR_H - 30) // 2  # Approx center of top bar
        LOWER_TEXT_Y1 = LOWER_Y + 15
        LOWER_TEXT_Y2 = LOWER_Y + 70
        TICKER_TEXT_Y = int(H - TICKER_H + (TICKER_H - 30) / 2)

        fg = (
            # ── Background ─────────────────────────────────────────────
            f"drawbox=x=0:y=0:w={W}:h={H}:color={C_NAVY}:t=fill,"

            # ── Anchor zone background (left side) ──────────────────────
            + (
                f"drawbox=x=0:y={TOP_BAR_H}:w={ANCHOR_W}:h={CONTENT_H + GOLD}:color={C_ANCHOR}:t=fill,"
                f"drawbox=x={ANCHOR_W}:y={TOP_BAR_H}:w=3:h={CONTENT_H}:color={C_GOLD}@0.5:t=fill,"
            if has_anchor else
                f"drawbox=x=0:y={TOP_BAR_H}:w={W}:h={CONTENT_H}:color={C_PANEL}:t=fill,"
            ) +

            # ── Top branding bar ─────────────────────────────────────────
            f"drawbox=x=0:y=0:w={W}:h={TOP_BAR_H}:color={C_RED}:t=fill,"

            # ── Gold accent line ─────────────────────────────────────────
            f"drawbox=x=0:y={TOP_BAR_H}:w={W}:h={GOLD}:color={C_GOLD}:t=fill,"

            # ── Channel name ─────────────────────────────────────────────
            f"drawtext=text='{ch}':fontfile={FONT}:fontsize=34:fontcolor={C_WHITE}:"
            f"x=24:y=({TOP_BAR_H}-text_h)/2,"

            # ── LIVE badge ───────────────────────────────────────────────
            f"drawtext=text='● LIVE':fontfile={FONT}:fontsize=26:fontcolor={C_GOLD}:"
            f"box=1:boxcolor={C_BLACK}@0.45:boxborderw=10:"
            f"x=({W}/2-text_w/2):y=({TOP_BAR_H}-text_h)/2,"

            # ── Clock ────────────────────────────────────────────────────
            f"drawtext=text='{now}':fontfile={FONT}:fontsize=24:fontcolor={C_WHITE}@0.85:"
            f"x=({W}-text_w-24):y=({TOP_BAR_H}-text_h)/2,"

            # ── Lower-third container ────────────────────────────────────
            f"drawbox=x=0:y={LOWER_Y}:w={W}:h={LOWER_H}:color={C_NAVY}@0.92:t=fill,"
            f"drawbox=x=0:y={LOWER_Y}:w={W}:h=5:color={C_RED}:t=fill,"

            # ── BREAKING NEWS label ──────────────────────────────────────
            f"drawbox=x=0:y={LOWER_Y + 5}:w=320:h=75:color={C_RED}:t=fill,"
            f"drawtext=text='{brk}':fontfile={FONT}:fontsize=24:fontcolor={C_WHITE}:"
            f"x=16:y={LOWER_Y + 5 + 25},"

            # ── Headline text ────────────────────────────────────────────
            f"drawtext=text='{hl}':fontfile={FONT}:fontsize=34:fontcolor={C_WHITE}:"
            f"x=340:y={LOWER_TEXT_Y1},"

            # ── Channel slogan ────────────────────────────────────────────
            f"drawtext=text='{slg}':fontfile={FONT}:fontsize=22:fontcolor={C_GOLD}@0.9:"
            f"x=340:y={LOWER_TEXT_Y2},"

            # ── Ticker strip ─────────────────────────────────────────────
            f"drawbox=x=0:y={H - TICKER_H}:w={W}:h={TICKER_H}:color={C_TICKER}:t=fill,"
            f"drawbox=x=0:y={H - TICKER_H}:w=210:h={TICKER_H}:color={C_RED}:t=fill,"
            f"drawtext=text='ताज्या बातम्या':fontfile={FONT}:fontsize=24:fontcolor={C_WHITE}:"
            f"x=14:y={TICKER_TEXT_Y},"

            # ── Scrolling ticker text ─────────────────────────────────────
            f"drawtext=text='  {tkr}  ●  {tkr}  ':fontfile={FONT}:fontsize=24:fontcolor={C_WHITE}:"
            f"x={W}-mod(t*{TICKER_SPEED}\\,{W}+text_w):y={TICKER_TEXT_Y},"

            # ── Bottom gold line ─────────────────────────────────────────
            f"drawbox=x=0:y={H - TICKER_H}:w={W}:h=3:color={C_GOLD}:t=fill"
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

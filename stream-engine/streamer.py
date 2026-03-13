"""
Smart News Marathi — 24x7 Stream Engine
========================================
Continuously streams news clips to the YouTube RTMP endpoint.
- Fetches the latest generated clips from the backend API
- Streams them as a seamless concat playlist
- Falls back to a branded filler screen when no clips exist
"""

import time
with open("iamalive.txt", "w") as f: f.write(f"Alive at {time.time()}\n")
import logging
try:
    import requests
    import os
    import socket
    from playlist_manager import PlaylistManager
    from broadcaster import Broadcaster
except ImportError as e:
    with open("import_error.txt", "w") as f: f.write(f"Import Error: {e}\n")
    print(f"CRITICAL: Missing dependency: {e}")
    import sys
    sys.exit(1)

# Basic console logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Add file handler separately to avoid crashing if file is locked
try:
    fh = logging.FileHandler("stream_engine.log", encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)
    logger.info("File logging initialized successfully.")
except Exception as e:
    print(f"CRITICAL: Failed to initialize file logging: {e}")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
# How many clips to batch-concat per streaming session
PLAYLIST_BATCH = 5
AD_INTERVAL_SEC = 30 * 60  # 30 minutes
LOCAL_ASSETS_DIR = "media/assets"
os.makedirs(LOCAL_ASSETS_DIR, exist_ok=True)
PROMO_PATH = os.path.join(LOCAL_ASSETS_DIR, "promo.mp4")

_lock_socket = None

def sync_promo_video():
    """Downloads the promotion video from backend to local storage for FFmpeg looping."""
    try:
        url = f"{BACKEND_URL}/media/assets/promo.mp4"
        logger.info(f"Syncing Promotion Video from {url}...")
        r = requests.get(url, stream=True, timeout=30)
        if r.status_code == 200:
            with open(PROMO_PATH, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info("✅ Promotion video synced locally.")
        else:
            logger.warning(f"Promotion video not found on backend (Status: {r.status_code})")
    except Exception as e:
        logger.warning(f"Failed to sync promo video: {e}")


def fetch_video_urls() -> list[str]:
    """Fetches the latest video URLs from the backend."""
    try:
        resp = requests.get(f"{BACKEND_URL}/news/videos", timeout=10)
        if resp.ok:
            files = resp.json().get("videos", [])
            valid_urls = []
            # Check which clips actually exist before queuing
            for f in files[:PLAYLIST_BATCH]:
                if f.startswith("../admin/"):
                    # Admin injected file
                    filename = f.split("/")[-1]
                    url = f"{BACKEND_URL}/media/admin/{filename}"
                else:
                    # Standard auto-news clip
                    url = f"{BACKEND_URL}/media/video/{f}"
                
                if requests.head(url, timeout=5).ok:
                    valid_urls.append(url)
            return valid_urls
    except Exception as exc:
        logger.warning(f"Could not reach backend: {exc}")
    return []

def fetch_ad_video() -> str:
    """Fetches the latest ad video from the backend, if available."""
    try:
        # We assume the backend has an endpoint for ads or we filter from list_videos
        resp = requests.get(f"{BACKEND_URL}/news/videos", timeout=10)
        if resp.ok:
            files = resp.json().get("videos", [])
            for f in files:
                if "ad_" in f:
                    filename = f.split("/")[-1]
                    url = f"{BACKEND_URL}/media/admin/{filename}"
                    if requests.head(url, timeout=5).ok:
                        return url
    except Exception as exc:
        logger.warning(f"Could not reach backend for ads: {exc}")
    return ""

def main():
    logger.info("=" * 60)
    logger.info("  वार्ताप्रवाह (VartaPravah) — 24x7 Stream Engine  ")
    logger.info("=" * 60)

    # Initial asset sync
    sync_promo_video()

    b = Broadcaster()
    streamed_urls: set[str] = set()
    last_ad_play_time = time.time()
    last_sync_time = time.time()

    while True:
        try:
            # 1. Check if it's time for an Ad/Promo Break (Every 30 mins)
            now = time.time()
            if now - last_ad_play_time >= AD_INTERVAL_SEC:
                logger.info("🕒 30-Minute Break Triggered: Checking for Ads...")
                ad_url = fetch_ad_video()
                
                if ad_url:
                    logger.info(f"Playing Admin Ad: {ad_url}")
                    b.start_streaming(ad_url)
                else:
                    logger.info("No Ad available. Playing 2-minute Looped Promotion...")
                    if os.path.exists(PROMO_PATH):
                        b.stream_video_loop(PROMO_PATH, 120) # 2 minutes
                    else:
                        logger.warning("Promo video missing at media/assets/promo.mp4. Skipping break.")
                
                last_ad_play_time = time.time()
                continue

            # 2. Normal News Cycle
            videos = fetch_video_urls()

            # Filter to new clips we haven't streamed yet
            new_videos = [v for v in videos if v not in streamed_urls]

            if new_videos:
                logger.info(f"Found {len(new_videos)} valid new clip(s). Starting playlist stream...")
                b.stream_playlist(new_videos)
                for nv in new_videos:
                    streamed_urls.add(nv)

                # Keep the played-set bounded (remember last 20 only)
                if len(streamed_urls) > 20:
                    sorted_urls = sorted(list(streamed_urls))
                    streamed_urls = set(sorted_urls[-20:])
            else:
                if not videos:
                    logger.info("No news available yet — streaming looped promotion as filler...")
                else:
                    logger.info("All clips streamed — streaming looped promotion while waiting...")
                
                # Use filler (which we updated to prefer promo.mp4)
                # This will loop until the process is interrupted by the next cycle check
                b.stream_filler()
                
                # Periodic re-sync of promo video (every 1 hour)
                if time.time() - last_sync_time > 3600:
                    sync_promo_video()
                    last_sync_time = time.time()
                
                time.sleep(2)

        except KeyboardInterrupt:
            logger.info("Stream engine stopped by user.")
            break
        except Exception as exc:
            logger.error(f"Stream engine error: {exc}. Retrying in 10s...")
            time.sleep(10)


if __name__ == "__main__":
    main()

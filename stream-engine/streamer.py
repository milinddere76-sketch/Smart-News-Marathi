"""
Smart News Marathi — 24x7 Stream Engine
========================================
Continuously streams news clips to the YouTube RTMP endpoint.
- Fetches the latest generated clips from the backend API
- Streams them as a seamless concat playlist
- Falls back to a branded filler screen when no clips exist
"""

import time
import logging
import requests
import os
from playlist_manager import PlaylistManager
from broadcaster import Broadcaster

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
# How many clips to batch-concat per streaming session
PLAYLIST_BATCH = 5


def fetch_video_urls() -> list[str]:
    """Fetches the latest video URLs from the backend."""
    try:
        resp = requests.get(f"{BACKEND_URL}/news/videos", timeout=10)
        if resp.ok:
            files = resp.json().get("videos", [])
            return [f"{BACKEND_URL}/media/video/{f}" for f in files[:PLAYLIST_BATCH]]
    except Exception as exc:
        logger.warning(f"Could not reach backend: {exc}")
    return []


def main():
    logger.info("=" * 60)
    logger.info("  स्मार्ट न्यूज मराठी — 24x7 Stream Engine  ")
    logger.info("=" * 60)

    b = Broadcaster()
    streamed_urls: set[str] = set()  # track what we've already played recently

    while True:
        try:
            videos = fetch_video_urls()

            # Filter to new clips we haven't streamed yet
            new_videos = [v for v in videos if v not in streamed_urls]

            if new_videos:
                logger.info(f"Found {len(new_videos)} new clip(s). Starting playlist stream...")
                b.stream_playlist(new_videos)
                streamed_urls.update(new_videos)

                # Keep the played-set bounded (remember last 20 only)
                if len(streamed_urls) > 20:
                    streamed_urls = set(list(streamed_urls)[-20:])
            else:
                if not videos:
                    logger.info("No clips available yet — streaming filler...")
                else:
                    logger.info("All available clips already streamed — streaming filler and waiting for new content...")
                    # Reset so we re-stream them next cycle if still no new content
                    streamed_urls.clear()

                b.stream_filler()
                logger.info("Filler done. Checking for new content in 30s...")
                time.sleep(30)

        except KeyboardInterrupt:
            logger.info("Stream engine stopped by user.")
            break
        except Exception as exc:
            logger.error(f"Stream engine error: {exc}. Retrying in 10s...")
            time.sleep(10)


if __name__ == "__main__":
    main()

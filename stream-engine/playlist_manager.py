import os
import random
import logging
import requests
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlaylistManager:
    def __init__(self, backend_url: str = None, ads_dir: str = "media/ads"):
        self.backend_url = backend_url or os.getenv("BACKEND_URL", "http://localhost:8000")
        self.ads_dir = ads_dir
        os.makedirs(self.ads_dir, exist_ok=True)
        # We don't need news_dir anymore as it's fetched via API

    def get_next_item(self, last_type: str = "news") -> str:
        """
        Determines the next video to play (News or Ad).
        Simple logic: Toggle between news and ads, or random.
        """
        if last_type == "news":
            # Pick an ad
            ads = [f for f in os.listdir(self.ads_dir) if f.endswith(".mp4")]
            if ads:
                return os.path.join(self.ads_dir, random.choice(ads)), "ad"
            else:
                # Fallback to news if no ads
                return self.get_random_news(), "news"
        else:
            # Pick a news clip
            return self.get_random_news(), "news"

    def get_random_news(self) -> str:
        try:
            response = requests.get(f"{self.backend_url}/news/videos")
            if response.status_code == 200:
                videos = response.json().get("videos", [])
                if videos:
                    filename = random.choice(videos)
                    return f"{self.backend_url}/media/video/{filename}"
        except Exception as e:
            logger.error(f"Error fetching news from backend: {e}")

        # Fallback to a placeholder if no news yet or API fails
        return "media/assets/placeholder_loop.mp4"

if __name__ == "__main__":
    pm = PlaylistManager()
    print(pm.get_next_item())

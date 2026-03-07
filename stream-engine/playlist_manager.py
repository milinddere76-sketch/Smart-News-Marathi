import os
import random
import logging
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlaylistManager:
    def __init__(self, news_dir: str = "../backend/media/video", ads_dir: str = "media/ads"):
        self.news_dir = news_dir
        self.ads_dir = ads_dir
        os.makedirs(self.news_dir, exist_ok=True)
        os.makedirs(self.ads_dir, exist_ok=True)

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
        news_files = [f for f in os.listdir(self.news_dir) if f.endswith(".mp4")]
        if not news_files:
            # Fallback to a placeholder if no news yet
            return "media/assets/placeholder_loop.mp4"
        return os.path.join(self.news_dir, random.choice(news_files))

if __name__ == "__main__":
    pm = PlaylistManager()
    print(pm.get_next_item())

import time
import logging
from playlist_manager import PlaylistManager
from broadcaster import Broadcaster
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("=== स्मार्ट न्यूज मराठी Stream Engine Starting ===")
    
    pm = PlaylistManager()
    b = Broadcaster()
    
    last_type = "ad" # Start with news
    
    while True:
        try:
            video_path, next_type = pm.get_next_item(last_type)
            
            if not os.path.exists(video_path):
                logger.warning(f"Video file not found: {video_path}. Waiting for content...")
                time.sleep(10)
                continue
            
            logger.info(f"Playing next segment: {next_type} ({video_path})")
            b.start_streaming(video_path)
            
            last_type = next_type
            
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

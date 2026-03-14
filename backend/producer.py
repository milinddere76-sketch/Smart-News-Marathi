import os
import time
import asyncio
import logging
import uuid
import json
from playlist_manager import PlaylistManager  # type: ignore
from broadcaster import Broadcaster  # type: ignore
from datetime import datetime
from scraper import NewsScraper  # type: ignore
from script_writer import NewsScriptWriter  # type: ignore
from voice_generator import VoiceGenerator  # type: ignore
from video_generator import VideoGenerator  # type: ignore
from anchor_generator import AnchorGenerator  # type: ignore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("producer.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NewsProducer:
    def __init__(self):
        self.scraper = NewsScraper()
        self.writer = NewsScriptWriter()
        self.video_gen = VideoGenerator()
        self.anchor_gen = AnchorGenerator()
        
        self.output_dir = "media/video"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Scheduling configuration
        self.slots = {
            "Morning Bulletin": (6, 10),
            "Afternoon Digest": (12, 16),
            "Prime Time Marathi": (19, 22),
            "Nightly Recap": (22, 24),
            "Late Night Update": (0, 6)
        }

    def get_current_slot(self):
        hour = datetime.now().hour
        for name, (start, end) in self.slots.items():
            if start <= hour < end:
                return name
        return "Regular News"

    async def produce_30_minute_loop(self):
        """
        Orchestrates a full 30-minute news cycle.
        """
        slot_name = self.get_current_slot()
        logger.info(f"--- Starting Production Loop for {slot_name} ---")
        
        try:
            # 1. Fetch News
            news_items = self.scraper.fetch_latest_news()[:7]
            if not news_items:
                logger.warning("No news items found. Waiting...")
                return

            # Current session ID (Formatted for requested news_YYYY_MM_DD_HH_MM style)
            session_id = datetime.now().strftime("%Y_%m_%d_%H_%M")
            logger.info(f"Session ID (Timestamp): {session_id}")

            # 2. INTRO
            logger.info("Producing Intro segment...")
            intro_script = await asyncio.to_thread(self.writer.generate_intro, slot_name)
            await self._generate_segment(intro_script, f"{slot_name} Intro", "Branding", is_male=True, prefix="01_intro", session_id=session_id, news_items=news_items)

            # 3. HEADLINES (Summary of all items)
            logger.info("Producing Headlines segment...")
            headlines_script = await asyncio.to_thread(self.writer.generate_headlines, news_items)
            await self._generate_segment(headlines_script, "प्रमुख बातम्या (Highlights)", "Breaking News", is_male=False, prefix="02_headlines", session_id=session_id, news_items=news_items)

            # 4. DETAILED NEWS SEGMENTS
            is_male = True
            for i, item in enumerate(news_items):
                title = item.get("title", "Breaking News")
                category = item.get("category", "General")
                logger.info(f"Generating Segment {i+1}: {str(title)[:50]}...")  # type: ignore
                
                script = await asyncio.to_thread(self.writer.generate_marathi_script, title)
                if "Error" in script: continue
                
                idx_str = f"{i+3:02d}" # 03, 04, ...
                await self._generate_segment(script, title, category, is_male, prefix=f"{idx_str}_news", session_id=session_id, news_items=news_items)
                is_male = not is_male
                await asyncio.sleep(2)

            # 5. PROMO / AD BREAK
            logger.info("Generating Channel Promotion Clip...")
            promo_filename = f"news_{session_id}_98_promo_{str(uuid.uuid4().hex)[:8]}.mp4"  # type: ignore
            await asyncio.to_thread(self.video_gen.create_promo_clip, promo_filename)

            # 6. OUTRO
            logger.info("Producing Outro segment...")
            outro_script = await asyncio.to_thread(self.writer.generate_outro)
            await self._generate_segment(outro_script, "धन्यवाद (Thank You)", "Branding", is_male=True, prefix="99_outro", session_id=session_id, news_items=news_items)

            logger.info(f"--- Production Loop for {slot_name} COMPLETED ---")
            
        except Exception as e:
            logger.error(f"Error in production loop: {e}")
            import traceback
            logger.error(traceback.format_exc())

    async def _generate_segment(self, script, title, category, is_male, prefix="segment", session_id="", news_items=[]):
        """Helper to generate a single news segment video."""
        try:
            # Voice
            voice_gen = VoiceGenerator(is_male=is_male)
            audio_filename = f"audio_{str(uuid.uuid4().hex)[:8]}.mp3"  # type: ignore
            audio_path = await voice_gen.generate_speech(script, audio_filename)
            
            # Anchor
            anchor_filename = f"anchor_{str(uuid.uuid4().hex)[:8]}.mp4"  # type: ignore
            anchor_path_out = os.path.join("media/anchor", anchor_filename)
            anchor_path = await asyncio.to_thread(
                self.anchor_gen.generate_anchor_clip, os.path.abspath(audio_path), anchor_path_out, is_male
            )
            
            # Final Clip
            ticker_content = " | ".join([item.get("title", "") for item in news_items])
            video_filename = f"news_{session_id}_{prefix}_{str(uuid.uuid4().hex)[:8]}.mp4"  # type: ignore
            final_path = await asyncio.to_thread(
                self.video_gen.create_news_clip,
                os.path.abspath(audio_path), title, ticker_content,
                video_filename, anchor_path, category
            )
            return final_path
        except Exception as e:
            logger.error(f"Failed to generate {prefix} segment: {e}")
            return None

    async def start_production_service(self):
        """Main service loop to run continuous production."""
        logger.info("VartaPravah Producer Service Started")
        while True:
            await self.produce_30_minute_loop()
            logger.info("Waiting 15 minutes before next production cycle...")
            await asyncio.sleep(900) # 15 min wait

if __name__ == "__main__":
    producer = NewsProducer()
    asyncio.run(producer.produce_30_minute_loop())

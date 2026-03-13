import os
import sys
import asyncio
import logging
import uuid
from scraper import NewsScraper
from script_writer import NewsScriptWriter
from voice_generator import VoiceGenerator
from video_generator import VideoGenerator
from anchor_generator import AnchorGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_single_segment():
    # 1. Setup
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    scraper = NewsScraper()
    writer = NewsScriptWriter()
    video_gen = VideoGenerator()
    anchor_gen = AnchorGenerator()
    
    # 2. News Title (Marathi)
    # Literal: "Maharashtra weather update: Heavy rain warning for next 48 hours"
    title = "महाराष्ट्र हवामान अपडेट: पुढील ४८ तास मुसळधार पावसाचा इशारा"
    category = "Hawaaman"
    
    logger.info(f"--- STARTING FULL SEGMENT GENERATION ---")
    logger.info(f"Title: {title}")
    
    try:
        # 3. Generate Marathi Script
        logger.info("Step 1: Generating Marathi script...")
        script = await asyncio.to_thread(writer.generate_marathi_script, title)
        logger.info(f"Script generated: {script[:100]}...")
        
        # 4. Voice Selection (Male for this test)
        is_male = True
        logger.info(f"Step 2: Initializing voice generator (Male: {is_male})...")
        voice_gen = VoiceGenerator(is_male=is_male)
        
        # 5. Output Filenames
        audio_filename = f"voice_{uuid.uuid4().hex}.mp3"
        video_filename = f"final_news_{uuid.uuid4().hex}.mp4"
        
        # 6. Generate Voice Audio
        logger.info("Step 3: Generating voice audio...")
        audio_path = await voice_gen.generate_speech(script, audio_filename)
        
        if not audio_path or not os.path.exists(audio_path):
            logger.error("Audio generation failed!")
            return

        # 7. Generate Anchor Video (Talking Head)
        logger.info("Step 4: Generating AI Anchor video (SadTalker)...")
        logger.info("NOTE: This uses the 'Fast/Stable Mode' we just verified!")
        
        anchor_video_filename = f"anchor_{uuid.uuid4().hex}.mp4"
        anchor_video_target = os.path.join("media/anchor", anchor_video_filename)
        
        anchor_video_path = await asyncio.to_thread(
            anchor_gen.generate_anchor_clip, 
            audio_path, 
            anchor_video_target,
            is_male=is_male
        )
        
        if not anchor_video_path or not os.path.exists(anchor_video_path):
            logger.error("Anchor video generation failed!")
            return

        # 8. Assemble Final Video (Overlays, Music, News Ticker)
        logger.info("Step 5: Assembling final news segment with overlays...")
        final_video_path = await asyncio.to_thread(
            video_gen.create_news_clip,
            audio_path=audio_path,
            headline=title,
            ticker_text=script,
            output_filename=video_filename,
            anchor_video_path=anchor_video_path,
            category=category
        )
        
        if not final_video_path or not os.path.exists(final_video_path):
            logger.error("Final video assembly failed!")
            return

        logger.info("--- [SUCCESS] FULL SEGMENT GENERATED! ---")
        logger.info(f"Final Video Location: {final_video_path}")
        print(f"\n✅ SUCCESS! Your Marathi news video is ready at:\n{final_video_path}")

    except Exception as e:
        logger.exception(f"An error occurred during generation: {e}")

if __name__ == "__main__":
    asyncio.run(generate_single_segment())

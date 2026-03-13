import asyncio
import sys
import os
import logging
sys.path.insert(0, r"d:\Apps\Smart News Marathi\backend")
os.chdir(r"d:\Apps\Smart News Marathi\backend")

logging.basicConfig(level=logging.INFO)

from scraper import NewsScraper
from script_writer import NewsScriptWriter
from voice_generator import VoiceGenerator
from video_generator import VideoGenerator

async def test_generation():
    print("\n--- 1. Testing Scraper ---")
    scraper = NewsScraper()
    news = scraper.fetch_latest_news()
    if not news:
        print("FAIL: Scraper returned nothing.")
        return
    title = news[0].get("title", "")
    print(f"Scraped title: {title}")

    print("\n--- 2. Testing AI Script Writer ---")
    writer = NewsScriptWriter()
    script = writer.generate_marathi_script(title)
    print(f"Generated Script[:100]: {script[:100]}...")

    print("\n--- 3. Testing Voice Generator ---")
    voice_gen = VoiceGenerator()
    audio = await voice_gen.generate_speech(script, "test_voice.mp3")
    print(f"Generated Audio Path: {audio}")

    print("\n--- 4. Testing Video Gen ---")
    print("Skipping full render, initializing class only")
    vg = VideoGenerator()
    print("Success. All models loaded and APIs responded.")

if __name__ == "__main__":
    asyncio.run(test_generation())

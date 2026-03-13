import asyncio
from scraper import NewsScraper
from script_writer import NewsScriptWriter
from voice_generator import VoiceGenerator
from video_generator import VideoGenerator
from anchor_generator import AnchorGenerator

async def test_all():
    scraper = NewsScraper()
    writer = NewsScriptWriter()
    voice_gen = VoiceGenerator()
    video_gen = VideoGenerator()
    anchor_gen = AnchorGenerator()
    
    # 1. Scrape
    print("1. Scraping...")
    news = scraper.fetch_latest_news()
    if not news:
        print("No news")
        return
    title = news[0]['title']
    print(f"Top: {title}")
    
    # 2. Script
    print("2. Scripting...")
    script = writer.generate_marathi_script(title)
    print(f"Script: {script[:50]}...")
    
    # 3. Voice
    print("3. Voice...")
    audio = await voice_gen.generate_speech(script, "test_voice.mp3")
    print(f"Audio: {audio}")
    
    # 4. Anchor
    print("4. Anchor...")
    anchor = anchor_gen.generate_anchor_clip(audio, "media/anchor/test_anchor.mp4", False)
    print(f"Anchor: {anchor}")
    
    # 5. Video
    print("5. Video...")
    vid = video_gen.create_news_clip(audio, title, "Test Ticker", "test_final.mp4", anchor, "Breaking News")
    print(f"Final Video: {vid}")

if __name__ == "__main__":
    asyncio.run(test_all())

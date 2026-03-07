from voice_generator import VoiceGenerator
from video_generator import VideoGenerator
from typing import List
import uuid

app = FastAPI(title="Smart News Marathi API")
scraper = NewsScraper()
writer = NewsScriptWriter()
voice_gen = VoiceGenerator()
video_gen = VideoGenerator()

@app.get("/")
async def root():
    return {"message": "Smart News Marathi API is running"}

@app.get("/news/top")
async def get_top_news(limit: int = 5):
    """
    Endpoint to fetch top N news items.
    """
    news = scraper.fetch_latest_news()
    return {"news": news[:limit]}

@app.post("/news/generate-script")
async def generate_script(title: str):
    """
    Endpoint to generate a Marathi news script for a given title.
    """
    script = writer.generate_marathi_script(title)
    return {"script": script}

@app.post("/news/generate-voice")
async def generate_voice(script: str):
    """
    Endpoint to generate a Marathi voiceover for a given script.
    """
    filename = f"news_{uuid.uuid4().hex}.mp3"
    audio_path = await voice_gen.generate_speech(script, filename)
    return {"audio_url": audio_path, "filename": filename}

@app.post("/news/generate-video")
async def generate_video(audio_path: str, headline: str, ticker: str):
    """
    Endpoint to generate a final news video clip.
    """
    filename = f"final_{uuid.uuid4().hex}.mp4"
    video_path = video_gen.create_news_clip(audio_path, headline, ticker, filename)
    return {"video_url": video_path, "filename": filename}

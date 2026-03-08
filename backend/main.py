from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from scraper import NewsScraper
from script_writer import NewsScriptWriter
from voice_generator import VoiceGenerator
from video_generator import VideoGenerator
from anchor_generator import AnchorGenerator
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Smart News Marathi API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for production simplicity, or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure media directory exists
os.makedirs("media/video", exist_ok=True)
os.makedirs("media/audio", exist_ok=True)

# Mount static files
app.mount("/media", StaticFiles(directory="media"), name="media")

@app.get("/latest-video")
async def get_latest_video():
    """Returns the filename of the most recently created news clip."""
    video_dir = "media/video"
    if not os.path.exists(video_dir):
        return {"filename": None}
    
    files = [f for f in os.listdir(video_dir) if f.endswith(".mp4") and f.startswith("final_")]
    if not files:
        return {"filename": None}
    
    # Sort by creation time
    files.sort(key=lambda x: os.path.getctime(os.path.join(video_dir, x)), reverse=True)
    return {"filename": files[0]}

scraper    = NewsScraper()
writer     = NewsScriptWriter()
voice_gen  = VoiceGenerator()
video_gen  = VideoGenerator()
anchor_gen = AnchorGenerator()

async def auto_generate_news_cycle():
    """
    Background loop to automatically fetch news and generate videos.
    """
    while True:
        try:
            logger.info("Starting auto news generation cycle...")
            # 1. Fetch latest news
            news_items = scraper.fetch_latest_news()[:3] # process top 3
            
            for item in news_items:
                title = item.get("title", "")
                if not title: continue
                
                logger.info(f"Processing: {title}")
                
                # 2. Generate script (Run in thread because it's blocking)
                script = await asyncio.to_thread(writer.generate_marathi_script, title)
                
                if "Error" in script:
                    logger.error(f"Script generation failed: {script}")
                    continue

                # 3. Generate voice
                voice_filename = f"news_{uuid.uuid4().hex}.mp3"
                audio_path = await voice_gen.generate_speech(script, voice_filename)
                
                if not audio_path:
                    logger.error("Voice generation failed.")
                    continue

                # 4. Generate anchor clip (AI talking head or FFmpeg silhouette)
                anchor_filename = f"anchor_{uuid.uuid4().hex}.mp4"
                anchor_path_out = os.path.abspath(os.path.join("media/anchor", anchor_filename))
                os.makedirs("media/anchor", exist_ok=True)
                
                logger.info("Generating AI anchor clip...")
                anchor_path = await asyncio.to_thread(
                    anchor_gen.generate_anchor_clip, os.path.abspath(audio_path), anchor_path_out
                )
                
                if anchor_path and os.path.exists(anchor_path):
                    logger.info(f"✅ Anchor clip ready: {os.path.basename(anchor_path)}")
                else:
                    logger.warning("⚠️ Anchor generation failed or file missing — falling back to no-anchor layout.")
                    anchor_path = None

                # 5. Generate studio video
                video_filename = f"final_{uuid.uuid4().hex}.mp4"
                final_video_path = await asyncio.to_thread(
                    video_gen.create_news_clip,
                    os.path.abspath(audio_path), title, "Smart News Marathi",
                    video_filename, anchor_path
                )

                if final_video_path and os.path.exists(final_video_path):
                    logger.info(f"✅ Video generated successfully: {video_filename}")
                else:
                    logger.error(f"❌ Video generation failed for: {video_filename}")

                await asyncio.sleep(20)  # longer break to avoid API rate limits
                
            logger.info("Cycle complete. Waiting 15 minutes for next update.")
            await asyncio.sleep(900) # Wait 15 minutes
            
        except Exception as e:
            logger.error(f"Error in auto_generate_news_cycle: {e}")
            await asyncio.sleep(60) # Wait a minute before retrying

@app.on_event("startup")
async def startup_event():
    # Start the background news generator
    asyncio.create_task(auto_generate_news_cycle())

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
    return {"video_url": f"/media/video/{filename}", "filename": filename}

@app.get("/news/videos")
async def list_videos():
    """
    Endpoint to list all generated video files.
    """
    video_dir = "media/video"
    if not os.path.exists(video_dir):
        return {"videos": []}
    files = [f for f in os.listdir(video_dir) if f.endswith(".mp4")]
    return {"videos": sorted(files, reverse=True)}

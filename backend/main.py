from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, Depends, HTTPException, status  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # type: ignore
from scraper import NewsScraper  # type: ignore
from script_writer import NewsScriptWriter  # type: ignore
from voice_generator import VoiceGenerator  # type: ignore
from video_generator import VideoGenerator  # type: ignore
from anchor_generator import AnchorGenerator  # type: ignore
import jwt # type: ignore
from datetime import datetime, timedelta
import uuid
import os
import time
import asyncio
import logging
import json
import shutil

# Configure logging
LOG_FILE = "app.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ],
    force=True
)
logger = logging.getLogger(__name__)

app = FastAPI(title="VartaPravah API")

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
os.makedirs("media/admin", exist_ok=True) 
os.makedirs("media/ads", exist_ok=True)
os.makedirs("media/assets", exist_ok=True)

# Admin Queue file
ADMIN_QUEUE_FILE = "admin_queue.json"
if not os.path.exists(ADMIN_QUEUE_FILE):
    with open(ADMIN_QUEUE_FILE, "w") as f:
        json.dump([], f)

# JWT Setup
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
ALGORITHM = "HS256"
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "smartnews123")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def verify_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != ADMIN_USER:
            raise HTTPException(status_code=401, detail="Invalid admin credentials")
        return username
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# Mount static files
app.mount("/media", StaticFiles(directory="media"), name="media")
# app.mount("/admin-ui", StaticFiles(directory="../frontend"), name="admin-ui")

from fastapi.responses import HTMLResponse  # type: ignore
# @app.get("/admin", response_class=HTMLResponse)
# async def get_admin_dashboard():
#     with open("../frontend/index.html", "r", encoding="utf-8") as f:
#         return f.read()

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
# Voice is now instantiated per-clip to allow gender toggling
# video_gen is still static
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
            news_items = scraper.fetch_latest_news()[:10] # process more per block
            logger.info(f"Fetched {len(news_items)} news items.")
            
            # Start alternating generator flag
            is_male_next = False
            news_count: int = 0
            
            for item in news_items:
                # Every 5 news items, inject a promotional clip
                if news_count > 0 and news_count % 5 == 0:  # type: ignore
                    logger.info("Injecting Promotional Clip...")
                    promo_filename = f"final_promo_{uuid.uuid4().hex}.mp4"
                    await asyncio.to_thread(video_gen.create_promo_clip, promo_filename)
                    await asyncio.sleep(5)
                    
                title = item.get("title", "")
                category = item.get("category", "Breaking News")
                if not title: continue
                
                logger.info(f"Processing: {title}")
                
                # 2. Generate script (Run in thread because it's blocking)
                logger.info(f"Calling Gemini Script Writer for: {title[:50]}...")
                script = await asyncio.to_thread(writer.generate_marathi_script, title)
                logger.info(f"Script generated: {script[:30]}...")
                
                if "Error" in script:
                    logger.error(f"Script generation failed: {script}")
                    continue

                # 3. Generate voice (Toggle gender)
                voice_gen = VoiceGenerator(is_male=is_male_next)
                voice_filename = f"news_{uuid.uuid4().hex}.mp3"
                logger.info(f"Generating TTS Speech (Male: {is_male_next})...")
                audio_path = await voice_gen.generate_speech(script, voice_filename)
                logger.info(f"Voice TTS Audio created at {audio_path}")
                
                if not audio_path:
                    logger.error("Voice generation failed.")
                    continue

                # 4. Generate anchor clip (AI talking head or FFmpeg silhouette)
                anchor_filename = f"anchor_{uuid.uuid4().hex}.mp4"
                anchor_path_out = os.path.abspath(os.path.join("media/anchor", anchor_filename))
                os.makedirs("media/anchor", exist_ok=True)
                
                logger.info(f"Generating AI anchor clip (Male: {is_male_next})...")
                anchor_path = await asyncio.to_thread(
                    anchor_gen.generate_anchor_clip, os.path.abspath(audio_path), anchor_path_out, is_male_next
                )
                
                if anchor_path and os.path.exists(anchor_path):
                    logger.info(f"DONE: Anchor clip ready: {os.path.basename(anchor_path)}")
                else:
                    logger.warning("WARNING: Anchor failed — using FFmpeg silhouette fallback...")
                    # Force FFmpeg silhouette — always works, no AI models needed
                    anchor_path = await asyncio.to_thread(
                        anchor_gen._run_ffmpeg_silhouette, os.path.abspath(audio_path), anchor_path_out, ""
                    )
                    if not (anchor_path and os.path.exists(anchor_path)):
                        logger.error("ERROR: FFmpeg silhouette also failed. Skipping item.")
                        continue
                    logger.info(f"DONE: FFmpeg silhouette anchor ready")

                # 5. Generate studio video
                video_filename = f"final_{uuid.uuid4().hex}.mp4"
                logger.info("Generating Final News Report Video...")
                final_video_path = await asyncio.to_thread(
                    video_gen.create_news_clip,
                    os.path.abspath(audio_path), title, "VartaPravah",
                    video_filename, anchor_path, category
                )
                logger.info(f"Final clip output: {final_video_path}")

                if final_video_path and os.path.exists(final_video_path):
                    logger.info(f"DONE: Video generated successfully: {video_filename}")
                else:
                    logger.error(f"ERROR: Video generation failed for: {video_filename}")

                # Toggle gender and increment counter for next news item
                is_male_next = not is_male_next
                news_count += 1

                await asyncio.sleep(20)  # longer break to avoid API rate limits
                
            logger.info("Cycle complete. Waiting 5 minutes for next update.")
            await asyncio.sleep(300) # Wait 5 minutes
            
        except Exception as e:
            logger.error(f"ERROR: FATAL CYCLE EXCEPTION: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await asyncio.sleep(60) # Wait a minute before retrying

async def cleanup_old_files():
    """
    Background loop to delete media files older than 6 hours.
    Runs every hour.
    """
    CLEANUP_HOURS = 6
    max_age_seconds = CLEANUP_HOURS * 3600
    media_dirs = ["media/video", "media/anchor", "media/audio"]

    while True:
        try:
            logger.info(f"Starting media cleanup (Files > {CLEANUP_HOURS} hours)...")
            print(f"MAIN_DEBUG: Starting media cleanup (Files > {CLEANUP_HOURS} hours)...", flush=True)
            now = time.time()
            deleted_count: int = 0
            
            for mdir in media_dirs:
                if not os.path.exists(mdir):
                    continue
                
                for f in os.listdir(mdir):
                    file_path = os.path.join(mdir, f)
                    if not os.path.isfile(file_path):
                        continue
                        
                    file_age = now - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        try:
                            # Keep placeholder loop safe if it exists
                            if f == "placeholder_loop.mp4":
                                continue
                            os.remove(file_path)
                            deleted_count += 1  # type: ignore
                        except Exception as e:
                            logger.error(f"Failed to delete {file_path}: {e}")
            
            if deleted_count > 0:
                logger.info(f"DONE: Cleanup complete: Removed {deleted_count} old files.")
                print(f"MAIN_DEBUG: DONE: Cleanup complete: Removed {deleted_count} old files.", flush=True)
            else:
                logger.info("Cleanup complete: No old files found.")
                print("MAIN_DEBUG: Cleanup complete: No old files found.", flush=True)

            # Wait 1 hour before next cleanup
            print(f"MAIN_DEBUG: Pausing before next cleanup cycle...", flush=True)
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"MAIN_DEBUG: ERROR: FATAL CLEANUP EXCEPTION: {e}", flush=True)
            import traceback
            traceback.print_exc()
            logger.error(f"Error in cleanup_old_files: {e}")
            await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    # Start the background news generator
    asyncio.create_task(auto_generate_news_cycle())
    # Start the background cleanup task
    asyncio.create_task(cleanup_old_files())
    logger.info("Startup complete - Auto news generation and Cleanup started.")


@app.get("/")
async def root():
    return {"message": "VartaPravah API is running"}

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
    voice_gen = VoiceGenerator()
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
    Endpoint to list all generated video files and prioritize any admin queued files.
    """
    admin_videos = []
    # 1. Pop from admin queue first!
    if os.path.exists(ADMIN_QUEUE_FILE):
        try:
            with open(ADMIN_QUEUE_FILE, "r") as f:
                queue = json.load(f)
            
            if queue:
                # Get the first item
                item = queue.pop(0)
                # Write back the remaining queue
                with open(ADMIN_QUEUE_FILE, "w") as f:
                    json.dump(queue, f)
                
                # Check if file exists in the admin dir
                admin_path = os.path.join("media/admin", item["filename"])
                if os.path.exists(admin_path):
                    # We return a special path marker so the streamer knows where it is
                    admin_videos.append(f"../admin/{item['filename']}")
                    logger.info(f"Injecting Admin Priority Video into Queue: {item['filename']}")
        except Exception as e:
            logger.error(f"Error reading admin queue: {e}")

    # 2. Get standard auto-news
    video_dir = "media/video"
    if not os.path.exists(video_dir):
        return {"videos": admin_videos}
    files = [f for f in os.listdir(video_dir) if f.endswith(".mp4") and not f.endswith("_temp.mp4")]
    # Sort by creation time so the newest clips play first
    files.sort(key=lambda x: os.path.getctime(os.path.join(video_dir, x)), reverse=True)
    
    # Return admin videos FIRST, then recent standard news
    return {"videos": admin_videos + files}

# ── ADMIN API ROUTES ────────────────────────────────────────────────────────

@app.post("/admin/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == ADMIN_USER and form_data.password == ADMIN_PASS:
        access_token = create_access_token(data={"sub": form_data.username}, expires_delta=timedelta(hours=24))
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")

@app.post("/admin/upload-media")
async def upload_custom_media(
    file: UploadFile = File(...), 
    type: str = Form(...), 
    title: str = Form(...),
    username: str = Depends(verify_admin)
):
    """Admin uploads Ad/Debate/Promo. Saved to media/admin and immediately pushed to front of queue."""
    if not file.filename.endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Only MP4 files allowed")
        
    if type == "promo":
        # Special case for channel promotion video
        file_path = os.path.join("media/assets", "promo.mp4")
        logger.info(f"Updating Channel Promotion video: {file_path}")
    elif type == "ad":
        u_id = uuid.uuid4().hex[:8]
        safe_name = f"ad_{u_id}.mp4"
        file_path = os.path.join("media/admin", safe_name)
    else:
        u_id = uuid.uuid4().hex[:8]
        safe_name = f"{type}_{u_id}.mp4"
        file_path = os.path.join("media/admin", safe_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    if type != "promo":
        # Add to JSON queue for priority playback in news cycle
        try:
            queue = []
            if os.path.exists(ADMIN_QUEUE_FILE):
                with open(ADMIN_QUEUE_FILE, "r") as f:
                    queue = json.load(f)
            
            queue.append({
                "filename": os.path.basename(file_path),
                "type": type,
                "title": title,
                "added_at": time.time()
            })
            
            with open(ADMIN_QUEUE_FILE, "w") as f:
                json.dump(queue, f)
                
            logger.info(f"Admin uploaded {type}: {os.path.basename(file_path)}")
        except Exception as e:
            logger.error(f"Upload queue failure: {e}")
            raise HTTPException(status_code=500, detail="Failed to queue media")

    return {"success": True, "path": file_path}

@app.get("/admin/queue")
async def get_admin_queue(username: str = Depends(verify_admin)):
    try:
        if os.path.exists(ADMIN_QUEUE_FILE):
            with open(ADMIN_QUEUE_FILE, "r") as f:
                return {"queue": json.load(f)}
    except Exception:
        pass
    return {"queue": []}

@app.get("/force_log")
async def force_log():
    try:
        logger.info("TEST LOG ENTRY - SUCCESS")
        return {"status": "Wrote to log"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/logs")
async def get_logs():
    """
    Endpoint to read the last 100 lines of the application log.
    """
    try:
        if not os.path.exists(LOG_FILE):
            return {"error": f"Log file not found at {os.path.abspath(LOG_FILE)}"}
            
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return {"logs": "".join(lines[-100:])}  # type: ignore
    except Exception as e:
        return {"error": str(e)}

@app.get("/check_assets")
async def check_assets():
    """Diagnostic endpoint to check for required files."""
    from typing import Any
    results: dict[str, Any] = {}
    assets_dir = "static_assets" if os.path.exists("static_assets") else "media/assets"
    
    paths = [
        f"{assets_dir}/anchor_male.jpg",
        f"{assets_dir}/anchor_female.jpg",
        f"{assets_dir}/news_font.ttf",
        f"{assets_dir}/bg_breaking.jpg",
        "app.log"
    ]
    for p in paths:
        results[p] = os.path.exists(p)
    
    # List all files for deep dive
    if os.path.exists(assets_dir):
        results[f"{assets_dir}_list"] = os.listdir(assets_dir)
    
    return results

if __name__ == "__main__":
    import uvicorn  # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)

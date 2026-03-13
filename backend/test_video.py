from video_generator import VideoGenerator
import os
print("Testing Video Generator...")
v = VideoGenerator()
if not os.path.exists("test_voice.mp3"):
    with open("test_voice.mp3", "wb") as f:
        f.write(b"dummy")
if not os.path.exists("test_anchor.mp4"):
    with open("test_anchor.mp4", "wb") as f:
        f.write(b"dummy")
        
path = v.create_news_clip("test_voice.mp3", "Test Title", "Ticker", "test_out.mp4", "test_anchor.mp4")
print(f"Path: {path}")

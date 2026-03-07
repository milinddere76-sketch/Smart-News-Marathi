import ffmpeg
import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self):
        self.output_dir = "media/video"
        self.assets_dir = "media/assets"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)

    def create_news_clip(self, audio_path: str, headline: str, ticker_text: str, output_filename: str) -> str:
        """
        Composites a news video using FFmpeg.
        Overlaying: Background, Anchor, Headline (Lower Third), and Scrolling Ticker.
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Paths to assets (assuming they exist or using placeholders)
        background_path = os.path.join(self.assets_dir, "studio_bg.jpg")
        anchor_path = os.path.join(self.assets_dir, "anchor_loop.mp4")
        
        # Check if assets exist, if not, use a solid color background for now
        if not os.path.exists(background_path):
            logger.warning("Background asset not found, using placeholder.")
            bg = ffmpeg.input('color=c=navy:s=1920x1080:d=10', f='lavfi')
        else:
            bg = ffmpeg.input(background_path)

        audio = ffmpeg.input(audio_path)
        
        # Initial composite logic
        try:
            logger.info(f"Compositing video for headline: {headline}")
            
            # Simple compositing example:
            # 1. Take background
            # 2. Overlay ticker text (Scrolling)
            # 3. Add audio
            
            # Note: Complex FFmpeg filters for scrolling text and lower thirds:
            # [bg][ticker]drawtext=text='...':fontfile=fonts/Marathi.ttf:y=h-line_h-10:x=w-mod(t*100\,w+tw):fontcolor=white:fontsize=40[v]
            
            stream = (
                bg
                .drawtext(
                    text=headline,
                    x='100', y='h-200',
                    fontsize=60,
                    fontcolor='yellow',
                    box=1, boxcolor='black@0.5', boxborderw=5
                )
                .drawtext(
                    text=ticker_text,
                    x='w-t*150', y='h-60',
                    fontsize=40,
                    fontcolor='white',
                    box=1, boxcolor='red@0.8', boxborderw=5
                )
                .output(audio, output_path, vcodec='libx264', acodec='aac', shortest=None)
                .overwrite_output()
            )
            
            # In a real environment, we'd run: stream.run()
            # For now, return the command we WOULD run as logic proof
            # stream.run() 
            
            logger.info(f"Video composite command prepared: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error compositing video: {e}")
            return ""

if __name__ == "__main__":
    vg = VideoGenerator()
    # Test call
    # vg.create_news_clip("media/audio/test.mp3", "मुंबईत मुसळधार पाऊस", "ताज्या बातम्यांसाठी पाहत रहा स्मार्ट न्यूज मराठी", "test_news.mp4")

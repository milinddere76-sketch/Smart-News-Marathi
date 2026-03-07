import subprocess
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Broadcaster:
    def __init__(self):
        self.stream_key = os.getenv("YOUTUBE_STREAM_KEY")
        self.rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{self.stream_key}"

    def start_streaming(self, video_path: str):
        """
        Broadsigns a single video file to the RTMP URL using FFmpeg.
        This is a blocking call until the video finishes.
        """
        if not self.stream_key:
            logger.error("YOUTUBE_STREAM_KEY not set. Cannot stream.")
            return

        command = [
            'ffmpeg',
            '-re', # Read input at native frame rate
            '-i', video_path,
            '-vcodec', 'libx264',
            '-preset', 'veryfast',
            '-maxrate', '3000k',
            '-bufsize', '6000k',
            '-pix_fmt', 'yuv420p',
            '-g', '50', # Keyframe interval
            '-acodec', 'aac',
            '-b:a', '128k',
            '-ar', '44100',
            '-f', 'flv',
            self.rtmp_url
        ]

        try:
            logger.info(f"Starting stream for: {video_path}")
            # Use subprocess to run FFmpeg
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            
            for line in process.stdout:
                # Optionally log progress
                if "frame=" in line.lower():
                    continue 
                # logger.debug(line.strip())
            
            process.wait()
            logger.info("Stream segment completed.")
            
        except Exception as e:
            logger.error(f"Broadcaster error: {e}")

if __name__ == "__main__":
    # Test broadcaster (needs a real stream key in .env)
    b = Broadcaster()
    # b.start_streaming("media/test.mp4")

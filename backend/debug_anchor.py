import asyncio
import os
import logging
from anchor_generator import AnchorGenerator

logging.basicConfig(level=logging.INFO)

async def debug_anchor():
    gen = AnchorGenerator()
    # Create a dummy audio file if it doesn't exist
    audio_path = "media/audio/test_debug.mp3"
    os.makedirs("media/audio", exist_ok=True)
    if not os.path.exists(audio_path):
        # Generate 5 sec of silence
        import subprocess
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "5", audio_path])
    
    out_path = "media/anchor/debug_silhouette.mp4"
    result = gen.generate_anchor_clip(audio_path, out_path)
    print(f"Result: {result}")
    if result and os.path.exists(result):
        print("Success!")
    else:
        print("Failed!")

if __name__ == "__main__":
    asyncio.run(debug_anchor())

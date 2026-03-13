import sys
import os
import asyncio

# Ensure paths correctly point to the backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.chdir('backend')

from voice_generator import VoiceGenerator
from anchor_generator import AnchorGenerator
from video_generator import VideoGenerator

async def main():
    print("Running end-to-end test...")
    vg = VoiceGenerator(is_male=False)
    audio_path = await vg.generate_speech("नमस्कार, स्मार्ट न्यूज मराठीमध्ये आपले स्वागत आहे. आजच्या ठळक बातम्या.", "test_voice.mp3")
    print(f"Generated voice: {audio_path}")

    ag = AnchorGenerator()
    anchor_out = os.path.abspath(os.path.join("media/anchor", "test_anchor_vid.mp4"))
    
    # Run anchor generation
    print("Generating anchor... (This should trigger SadTalker)")
    res_anchor = ag.generate_anchor_clip(os.path.abspath(audio_path), anchor_out, is_male=False)
    print(f"Generated anchor: {res_anchor}")

    vgen = VideoGenerator()
    print("Generating final 480p composite video...")
    res_vid = vgen.create_news_clip(os.path.abspath(audio_path), "टेस्ट न्यूज", "TEST TICKER | TEST", "test_final.mp4", res_anchor)
    print(f"Generated video: {res_vid}")
    
    if os.path.exists("media/video/test_final.mp4"):
        print("SUCCESS! File exists.")
        
if __name__ == "__main__":
    asyncio.run(main())

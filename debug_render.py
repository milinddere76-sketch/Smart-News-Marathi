import os
import sys
import logging

# Set up logging to stdout
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add backend to path so we can import modules
sys.path.append(os.path.abspath("backend"))

try:
    from backend.video_generator import VideoGenerator
    from backend.anchor_generator import AnchorGenerator
    
    # Force FFmpeg paths if not in env
    os.environ["FFMPEG_PATH"] = r"D:\ffmpeg\bin\ffmpeg.exe"
    os.environ["FFPROBE_PATH"] = r"D:\ffmpeg\bin\ffprobe.exe"
    
    vg = VideoGenerator()
    ag = AnchorGenerator()
    
    # Pick a random audio file
    audio_dir = "backend/media/audio"
    audios = [f for f in os.listdir(audio_dir) if f.endswith(".mp3")]
    if not audios:
        print("No audio files found in backend/media/audio")
        sys.exit(1)
        
    test_audio = os.path.join(audio_dir, audios[0])
    test_anchor = "backend/media/anchor/debug_anchor.mp4"
    test_final = "backend/media/video/debug_final.mp4"
    
    print(f"--- TESTING ANCHOR GENERATION ---")
    anchor_res = ag.generate_anchor_clip(test_audio, test_anchor)
    print(f"Anchor result: {anchor_res}")
    
    if anchor_res and os.path.exists(anchor_res):
        print(f"Anchor file size: {os.path.getsize(anchor_res)} bytes")
        
        print(f"\n--- TESTING FINAL COMPOSITION ---")
        final_res = vg.create_news_clip(
            test_audio, 
            "चाचणी हेडलाईन: स्मार्ट न्यूज मराठी मध्ये आपले स्वागत आहे", 
            "| मुंबई: ताज्या बातम्या | पुणे: अपडेट्स |",
            "debug_final.mp4",
            anchor_res
        )
        print(f"Final result: {final_res}")
        if final_res and os.path.exists(final_res):
            print(f"Final file size: {os.path.getsize(final_res)} bytes")
    else:
        print("Anchor generation failed, skipping final composition test.")

except Exception as e:
    import traceback
    print(f"An error occurred: {e}")
    traceback.print_exc()

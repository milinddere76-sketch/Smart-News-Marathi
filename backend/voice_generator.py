import asyncio
import edge_tts
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Marathi Voices available in edge-tts:
# mr-IN-AarohiNeural (Female)
# mr-IN-ManoharNeural (Male)

class VoiceGenerator:
    def __init__(self, voice: str = "mr-IN-AarohiNeural"):
        self.voice = voice
        self.output_dir = "media/audio"
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_speech(self, text: str, filename: str) -> str:
        """
        Converts text to speech in Marathi and saves as an mp3 file.
        """
        if not text:
            return ""

        output_path = os.path.join(self.output_dir, filename)
        
        try:
            logger.info(f"Generating voice for: {text[:50]}...")
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_path)
            logger.info(f"Audio saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating voice: {e}")
            return ""

if __name__ == "__main__":
    # Test voice generator
    async def test():
        vg = VoiceGenerator()
        await vg.generate_speech("नमस्कार, स्मार्ट न्यूज मराठी मध्ये आपले स्वागत आहे.", "test_intro.mp3")
    
    asyncio.run(test())

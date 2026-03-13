import asyncio
import edge_tts
import os
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Marathi Voices available in edge-tts:
# mr-IN-AarohiNeural (Female)
# mr-IN-ManoharNeural (Male)

class VoiceGenerator:
    def __init__(self, is_male: bool = False):
        self.voice = "mr-IN-ManoharNeural" if is_male else "mr-IN-AarohiNeural"
        self.output_dir = "media/audio"
        os.makedirs(self.output_dir, exist_ok=True)

    def _clean_text_for_tts(self, text: str) -> str:
        """
        Strips ALL XML/SSML tags and technical artifacts from text before
        sending to edge-tts. This prevents tags from being read aloud.
        """
        # All competitor channel names to scrub out
        competitor_channels = [
            "एबीपी माझा", "ABP Majha", "ABP माझा", "एबीपी",
            "लोकमत", "Lokmat",
            "झी 24 तास", "Zee 24 Taas", "झी न्यूज", "Zee News", "झी",
            "TV9 मराठी", "TV9 Marathi", "टीव्ही 9", "TV9",
            "सकाळ टीव्ही", "Sakal TV",
            "महाराष्ट्र टाइम्स", "Maharashtra Times",
            "नवभारत", "Navbharat Times",
            "India Today मराठी", "India Today Marathi",
            "आज तक", "Aaj Tak",
            "NDTV मराठी", "NDTV",
            "Republic Bharat", "Republic TV",
            "CNN News18", "News18 Lokmat", "News18",
            "Star Pravah", "स्टार प्रवाह",
            "Colors Marathi",
            "Rasodi", "रसोडी", "Manohar", "महरान", "Aarohi", "आरोही",
            "Misteryn", "Manohar", "ManoharNeural", "AarohiNeural"
        ]
        for channel in competitor_channels:
            text = re.sub(re.escape(channel), "", text, flags=re.IGNORECASE)

        # Strip all XML/SSML tags (e.g. <speak>, <break/>, <prosody>, etc.)
        text = re.sub(r'<[^>]+/?>', '', text)

        # Remove XML declarations and namespaces that might appear as text
        text = re.sub(r'xmlns\s*=\s*["\'][^"\']*["\']', '', text)
        text = re.sub(r'xml:\w+\s*=\s*["\'][^"\']*["\']', '', text)
        text = re.sub(r'version\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
        text = re.sub(r'organization\s+synthesis\s+xml', '', text, flags=re.IGNORECASE)
        text = re.sub(r'bose\s+speak\s+version', '', text, flags=re.IGNORECASE)

        # Remove URLs (http/https)
        text = re.sub(r'https?://\S+', '', text)

        # Remove SSML/Technical parameters (rate, pitch, volume, htz, ms, etc.)
        technical_junk = [
             r'\b(rate|pitch|volume|break|time|lang|language)\s*[=:+\-]?\s*[\d.%A-Za-z]+\b',
             r'\b\d+\s*(htzs|hz|kbps|ms)\b',
             r'\b(synthesis|synthesis_xml|lan|misteryn)\b'
        ]
        for pattern in technical_junk:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Remove bracket and parenthesis stage directions
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(.*?\)', '', text)

        # Remove @ handles and # hashtags
        text = re.sub(r'[@#]\S+', '', text)

        # Clean up leftover punctuation artifacts and extra whitespace
        text = re.sub(r'[<>{}]', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)

        return text.strip()

    async def generate_speech(self, text: str, filename: str) -> str:
        """
        Converts text to speech in Marathi and saves as an mp3 file.
        Uses plain text (NOT SSML) so no XML artifacts are spoken aloud.
        """
        if not text:
            return ""

        # Clean the text FIRST — strip all XML/SSML tags and technical garbage
        clean_text = self._clean_text_for_tts(text)

        if not clean_text:
            logger.warning("Text was empty after cleaning. Skipping TTS.")
            return ""

        output_path = os.path.join(self.output_dir, filename)

        try:
            logger.info(f"Generating voice for: {str(clean_text)[:60]}...")
            # Use plain text — edge-tts Communicate() does NOT support manual SSML.
            # Passing SSML causes all the tags (<speak>, <break>, rate=, volume=) to be read aloud.
            communicate = edge_tts.Communicate(clean_text, self.voice)
            await communicate.save(output_path)
            logger.info(f"Audio saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating voice: {e}")
            return ""

if __name__ == "__main__":
    async def test():
        vg = VoiceGenerator()
        await vg.generate_speech("नमस्कार... वार्ताप्रवाहमध्ये आपले स्वागत आहे.", "test_intro.mp3")

    asyncio.run(test())

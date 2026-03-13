import os
import google.generativeai as genai  # type: ignore[import-untyped]
from dotenv import load_dotenv  # type: ignore[import-untyped]
import logging
import time
import random

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    logger.warning("GEMINI_API_KEY not found in environment variables.")

MARATHI_NEWS_PROMPT = """
You are a professional Marathi news anchor and scriptwriter. 
Your task is to take the following news headline/brief and rewrite it into a formal, engaging, and professional broadcast script in Marathi.

News to process:
{raw_news}

Guidelines:
1. Use professional Marathi language (Sakal/Lokmat style).
2. The tone should be serious and informative.
3. Start with a hook.
4. Keep the script between 100-150 words.
5. Focus on clarity and flow for a news reader.
6. Only output the Marathi script, no English or Hindi.

Output format:
मथळा: [News Title]
बातमी: [Your rewritten Marathi news script]
"""

class NewsScriptWriter:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash') if api_key else None

    def generate_marathi_script(self, raw_news_title: str, raw_news_content: str = "") -> str:
        """
        Generates a Marathi news script with exponential backoff and fallback.
        """
        if not self.model:
            return "Error: Gemini API not configured."

        prompt = f"""
        तुम्ही एक अत्यंत व्यावसायिक आणि अनुभवी न्यूज अँकर आणि स्क्रिप्टरायटर आहात जे "वार्ताप्रवाह" (VARTAPRAVAH) या राष्ट्रीय वृत्तवाहिनीसाठी काम करता.

        **तुमचे काम:**
        दिलेल्या बातमीच्या हेडलाईनवरून एक **सविस्तर**, **माहितीपूर्ण** आणि **व्यावसायिक** मराठी बातमी लिहा.

        **लांबी (अत्यंत महत्त्वाचे - बंधनकारक):**
        - स्क्रिप्ट **२०० ते २८० शब्दांची** असणे अनिवार्य आहे.
        - वाचनाचा वेळ ४० ते ६० सेकंद असला पाहिजे.
        - बातमीत कमीत कमी **३ ते ४ सविस्तर मुद्दे** असणे आवश्यक आहे.

        **स्क्रिप्टची अनिवार्य रचना:**
        १. **सुरुवात (Intro):** "नमस्कार... वार्ताप्रवाहमध्ये आपले स्वागत आहे..." या वाक्यानेच सुरुवात करा.
        २. **मुख्य बातमी (Body - ३-४ मुद्दे):**
           - मुद्दा १: बातमी काय घडली, कुठे, कधी?
           - मुद्दा २: कारण आणि पार्श्वभूमी काय?
           - मुद्दा ३: सरकार/प्रशासन/तज्ज्ञ काय म्हणतात?
           - मुद्दा ४: पुढे काय अपेक्षित आहे?
        ३. **समारोप (Outro):** "...अधिक माहिती आणि ताज्या घडामोडींसाठी... पाहत राहा... वार्ताप्रवाह... आणि सबस्क्राईब करायला विसरू नका."

        **न्यूज अँकर पेसिंग:**
        - प्रभावी ठिकाणी पॉज द्या: तीन डॉट (...) वापरा.
        - "महत्त्वाची बातमी...", "सूत्रांकडून मिळालेल्या माहितीनुसार..." असे व्यावसायिक वाक्यप्रयोग वापरा.

        **कठोर बंदी (या गोष्टी अजिबात वापरू नका):**
        - रसोडी, रेसिपी, खाद्यपदार्थ, स्वयंपाक, मेजवानी, चव, जेवण, फॅशन, जीवनशैली या विषयांशी संबंधित काहीही लिहू नका.
        - बातमी जर या विषयावर असेल तर ती **वगळा** आणि "माहिती अनुपलब्ध" असे सांगा.
        - इतर चॅनेलची नावे (लोकमत, एबीपी माझा, झी न्यूज इ.) वापरू नका.
        - इंग्रजी शब्द, @ हँडल्स, ब्रॅकेट्स वापरू नका.
        - फक्त शुद्ध मराठी बातमी द्या.

        **बातमी हेडलाईन:**
        {raw_news_title}

        **अतिरिक्त माहिती (असल्यास):**
        {raw_news_content if raw_news_content else "वरील हेडलाईनवरून सविस्तर बातमी तयार करा."}
        """

        if not self.model:
            logger.error("Gemini model is not initialized (API key missing). Returning fallback.")
            return self._sanitize_script(f"नमस्कार... वार्ताप्रवाहमध्ये आपले स्वागत आहे... {raw_news_title}. ...अधिक माहितीसाठी पाहत राहा... वार्ताप्रवाह.")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Generating Marathi news script (Attempt {attempt+1}/{max_retries})...")
                response = self.model.generate_content(prompt)  # type: ignore[union-attr]
                if response and response.text:
                    return self._sanitize_script(response.text.strip())
            except Exception as e:
                # Check for rate limit (429)
                if "429" in str(e):
                    wait_time = (2 ** attempt) + random.random()
                    logger.warning(f"Rate limit hit. Retrying in {wait_time:.2f}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                # Handle other errors immediately without retry
                if "Illegal header value" in str(e) or "invalid metadata" in str(e).lower():
                    logger.error("CRITICAL: Invalid GEMINI_API_KEY. Please check for spaces or newlines in your Fly.io secrets.")
                else:
                    logger.error(f"Error generating script: {e}")
                break # Exit loop on non-rate-limit errors

        # Hard-coded Marathi fallback if API fails completely
        logger.warning("Using hard-coded Marathi news template fallback.")
        fallback = f"""नमस्कार... वार्ताप्रवाहमध्ये आपले स्वागत आहे...\n\n{raw_news_title}. या महत्त्वाच्या बातमीनुसार, संबंधित प्रशासनाने तातडीने पावले उचलली आहेत. सूत्रांकडून मिळालेल्या माहितीनुसार पुढील तपास सुरू असून लवकरच अधिक माहिती समोर येण्याची शक्यता आहे. या घटनेचा परिणाम राज्यभर जाणवत असून सरकार परिस्थितीवर बारकाईने लक्ष ठेवून आहे.\n\n...अधिक माहिती आणि ताज्या घडामोडींसाठी... पाहत राहा... वार्ताप्रवाह... आणि सबस्क्राईब करायला विसरू नका."""
        return fallback.strip()

    def _sanitize_script(self, text: str) -> str:
        """
        Post-processing safety net: removes competitor channel names,
        social handles, and bracket annotations from AI-generated scripts.
        Runs every time regardless of what the AI outputs.
        """
        import re

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

        # Remove XML namespaces / attributes read as plain text
        text = re.sub(r'xmlns\s*=\s*["\'][^"\']*["\']', '', text)
        text = re.sub(r'xml:\w+\s*=\s*["\'][^"\']*["\']', '', text)
        text = re.sub(r'version\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
        text = re.sub(r'organization\s+synthesis\s+xml', '', text, flags=re.IGNORECASE)
        text = re.sub(r'bose\s+speak\s+version', '', text, flags=re.IGNORECASE)

        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)

        # Remove SSML/Technical parameters (rate, pitch, volume, htz, ms, etc.)
        technical_junk = [
            r'\b(rate|pitch|volume|break|time|lang|language)\s*[=:+\-]?\s*[\d.%A-Za-z]+\b',
            r'\b\d+\s*(htzs|hz|kbps|ms)\b',
            r'\b(synthesis|synthesis_xml|lan|misteryn)\b'
        ]
        for pattern in technical_junk:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Remove @social handles
        text = re.sub(r'@\S+', '', text)

        # Remove bracket/parenthesis stage directions [Pause], (anchor smiles) etc.
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(.*?\)', '', text)

        # Remove hashtags and stray < > symbols
        text = re.sub(r'#\S+', '', text)
        text = re.sub(r'[<>{}]', '', text)

        # Clean up extra whitespace/blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

if __name__ == "__main__":
    import sys
    # Force UTF-8 encoding for Windows console output
    try:
        sys.stdout.reconfigure(encoding='utf-8')  # type: ignore[union-attr]
    except AttributeError:
        pass
    # Test script writer
    writer = NewsScriptWriter()
    test_title = "Mumbai Rain Update: Heavy rainfall expected in next 24 hours"
    script = writer.generate_marathi_script(test_title)
    print(script)

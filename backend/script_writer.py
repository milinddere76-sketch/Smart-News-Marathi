import os
import google.generativeai as genai
from dotenv import load_dotenv
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
You are a professional Marathi news anchor and scriptwriter for 'स्मार्ट न्यूज मराठी'. 
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
        तुम्ही एक अत्यंत व्यावसायिक मराठी न्यूज अँकर आणि स्क्रिप्ट रायटर आहात. 
        तुमची भाषा शुद्ध, औपचारिक आणि प्रभावी असावी (सकाळ/लोकमत शैली). 
        
        दिलेल्या हेडलाईनवरून ३०-४० सेकंदांची एक न्यूज स्क्रिप्ट लिहा.
        स्क्रिप्टमध्ये खालील ३ भाग असणे अनिवार्य आहे:
        १. सुरुवात (Hook/Greeting): उदा. "नमस्कार, आपण पाहत आहात स्मार्ट न्यूज मराठी. आजची सर्वात मोठी बातमी..."
        २. मुख्य बातमी (Body): बातमीचे तपशील, 'दरम्यान', 'परिणामी', 'असे असले तरी' यांसारखे शब्द वापरून लिहा.
        ३. समारोप (Outro): उदा. "पाहात राहा, स्मार्ट न्यूज मराठी. सत्य, निर्भय, निष्पक्ष. धन्यवाद."

        केवळ मराठी भाषेत स्क्रिप्ट द्या. कोणतीही इतर माहिती नको.
        
        HEADLINE: {raw_news_title}
        CONTENT: {raw_news_content}
        
        व्यावसायिक न्यूज स्क्रिप्ट:
        """

        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Generating Marathi news script (Attempt {attempt+1}/{max_retries})...")
                response = self.model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
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
        return f"""
नमस्कार, आपण पाहत आहात स्मार्ट न्यूज मराठी.

आजची मोठी बातमी: {raw_news_title}

या विषयावर अधिक माहिती मिळवत आहोत. महाराष्ट्रातील आणि देशातील सर्व महत्त्वाच्या घडामोडींसाठी पाहत राहा, स्मार्ट न्यूज मराठी. सत्य, निर्भय, निष्पक्ष. धन्यवाद.
        """.strip()

if __name__ == "__main__":
    # Test script writer
    writer = NewsScriptWriter()
    test_title = "Mumbai Rain Update: Heavy rainfall expected in next 24 hours"
    script = writer.generate_marathi_script(test_title)
    print(script)

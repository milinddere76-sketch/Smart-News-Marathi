import os
import google.generativeai as genai # type: ignore
from dotenv import load_dotenv
import logging
import time
import random

load_dotenv()
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class NewsScriptWriter:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.marathi_prompt_base = (
            "You are a professional Marathi news writer for 'VartaPravah'. "
            "Write a concise, engaging, and professional news script in Marathi (script only, no English) "
            "based on the following news title. Use a formal broadcast tone. "
        )

    def _safe_generate(self, prompt: str, max_retries: int = 5) -> str:
        attempt = 1
        last_error = ""
        
        while attempt <= max_retries:
            try:
                logger.info(f"Generating content (Attempt {attempt}/{max_retries})...")
                response = self.model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
                else:
                    logger.warning(f"Empty response from Gemini on attempt {attempt}")
            except Exception as e:
                last_error = str(e)
                if "429" in last_error or "quota" in last_error.lower() or "rate limit" in last_error.lower():
                    # Wait and retry on rate limits
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Rate limit hit. Retrying in {wait_time:.2f}s... (Attempt {attempt}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Gemini Error on attempt {attempt}: {e}")
                    # For non-rate-limit errors, we still retry but maybe with smaller wait
                    time.sleep(1)
            
            attempt += 1
            
        return f"Error: Maximum retries exceeded. Last error: {last_error}"

    def generate_marathi_script(self, title: str) -> str:
        """Generates a standard news script for a single item."""
        prompt = self.marathi_prompt_base + f"\nTitle: {title}\nScript:"
        return self._safe_generate(prompt)

    def generate_intro(self, slot_name: str) -> str:
        """Generates a professional intro for a news slot."""
        prompt = (
            f"Write a 15-second professional Marathi news introduction for the '{slot_name}' bulletin on VartaPravah channel. "
            "Welcome the viewers and set a serious, authoritative tone. No English."
        )
        return self._safe_generate(prompt)

    def generate_headlines(self, items: list) -> str:
        """Generates a quick summary of multiple headlines."""
        titles_str = "\n".join([f"- {item.get('title')}" for item in items])
        prompt = (
            "Write a concise Marathi summary of the following top headlines for a quick 30-second 'Headlines' segment. "
            f"Keep it fast-paced and professional.\n\n{titles_str}\nNo English."
        )
        return self._safe_generate(prompt)

    def generate_outro(self) -> str:
        """Generates a professional outro."""
        prompt = (
            "Write a 10-second professional Marathi news outro for VartaPravah. "
            "Thank the viewers for watching, ask them to stay tuned, and conclude formally. No English."
        )
        return self._safe_generate(prompt)

if __name__ == "__main__":
    writer = NewsScriptWriter()
    print(writer.generate_marathi_script("महाराष्ट्रात पावसाचा जोर वाढणार"))

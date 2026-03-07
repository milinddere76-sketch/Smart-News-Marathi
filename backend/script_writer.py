import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
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
        self.model = genai.GenerativeModel('gemini-1.5-flash') if api_key else None

    def generate_marathi_script(self, raw_news_title: str, raw_news_content: str = "") -> str:
        """
        Generates a professional Marathi news script using Gemini API.
        """
        if not self.model:
            return "Error: Gemini API not configured."

        combined_input = f"Title: {raw_news_title}\nContent: {raw_news_content}"
        prompt = MARATHI_NEWS_PROMPT.format(raw_news=combined_input)

        try:
            logger.info("Generating Marathi news script...")
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
            return "Error: Empty response from AI."
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            return f"Error: {str(e)}"

if __name__ == "__main__":
    # Test script writer
    writer = NewsScriptWriter()
    test_title = "Mumbai Rain Update: Heavy rainfall expected in next 24 hours"
    script = writer.generate_marathi_script(test_title)
    print(script)

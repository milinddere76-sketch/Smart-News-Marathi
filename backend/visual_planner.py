import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import json

load_dotenv()
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class VisualPlanner:
    def __init__(self):
        # Using Gemini 1.5 Flash - avoid '-latest' suffix to prevent 404s
        raw_model = os.getenv("GEMINI_VISUAL_MODEL", "gemini-1.5-flash")
        self.model_name = raw_model.replace("-latest", "")
        self.model = genai.GenerativeModel(self.model_name)
        
        self.system_instructions = (
            "You are a professional News Visual Director. Your task is to analyze Marathi news scripts "
            "and plan the visual scenes for a 1920x1080 professional news broadcast. "
            "For each news story, provide:\n"
            "1. A background image prompt (for AI image generation).\n"
            "2. A short headline to be displayed as text overlay.\n"
            "3. Suggested scene transition (e.g., 'fade', 'slide').\n"
            "Output must be in JSON format."
        )

    def plan_visuals(self, bulletin: dict) -> list:
        """
        Takes a bulletin structure and returns a list of visual plans for each story.
        """
        visual_plans = []
        
        for story in bulletin.get("stories", []):
            prompt = (
                f"Analyze this news story and provide visual metadata in JSON format:\n"
                f"Title: {story['title']}\n"
                f"Script: {story['script']}\n\n"
                "JSON structure:\n"
                "{\n"
                "  \"image_prompt\": \"Detailed prompt for a news background image related to this story\",\n"
                "  \"overlay_headline\": \"Concise headline text for the screen (Marathi)\",\n"
                "  \"transition\": \"fade\"\n"
                "}"
            )
            
            try:
                response = self.model.generate_content(
                    f"{self.system_instructions}\n\n{prompt}",
                    generation_config={"response_mime_type": "application/json"}
                )
                plan = json.loads(response.text)
                visual_plans.append(plan)
            except Exception as e:
                logger.error(f"Gemini Visual Planning Error: {e}")
                # Fallback plan
                visual_plans.append({
                    "image_prompt": f"Professional news background regarding {story['title']}",
                    "overlay_headline": story['title'],
                    "transition": "fade"
                })
        
        return visual_plans

if __name__ == "__main__":
    planner = VisualPlanner()
    test_bulletin = {
        "stories": [
            {"title": "महाराष्ट्रात पावसाचा इशारा", "script": "पुढील २४ तासात मुंबई आणि साताऱ्यात मुसळधार पाऊस पडेल."}
        ]
    }
    print(planner.plan_visuals(test_bulletin))

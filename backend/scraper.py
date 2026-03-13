import feedparser
import requests
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google News RSS for Marathi News
# HL = Marathi (mr), GL = India (IN)
# Categorized Google News RSS Feeds for Marathi (HL=mr, GL=IN)
CATEGORIES = {
    "Breaking News": "https://news.google.com/rss?hl=mr&gl=IN&ceid=IN:mr",
    "India": "https://news.google.com/rss/headlines/section/topic/NATION.mr_in?hl=mr&gl=IN&ceid=IN:mr",
    "World": "https://news.google.com/rss/headlines/section/topic/WORLD.mr_in?hl=mr&gl=IN&ceid=IN:mr",
    "Maharashtra": "https://news.google.com/rss/headlines/section/geo/Maharashtra?hl=mr&gl=IN&ceid=IN:mr",
    "Business": "https://news.google.com/rss/headlines/section/topic/BUSINESS.mr_in?hl=mr&gl=IN&ceid=IN:mr",
    "Technology": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY.mr_in?hl=mr&gl=IN&ceid=IN:mr",
    "Entertainment": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT.mr_in?hl=mr&gl=IN&ceid=IN:mr",
    "Sports": "https://news.google.com/rss/headlines/section/topic/SPORTS.mr_in?hl=mr&gl=IN&ceid=IN:mr"
}

class NewsScraper:
    def __init__(self):
        pass

    def fetch_latest_news(self) -> List[Dict]:
        """
        Fetches the latest news from categorized RSS feeds.
        Returns a list of dictionaries containing news title, link, date, and category.
        """
        news_items = []
        try:
            for category, url in CATEGORIES.items():
                logger.info(f"Fetching {category} news from {url}")
                feed = feedparser.parse(url)
                
                # Take top 5 and filter for better diversity
                count = 0
                for entry in feed.entries:
                    if count >= 3: break
                    
                    raw_title = entry.title
                    # Strip source names (e.g., "News Title - Source Name")
                    title = raw_title
                    for sep in [" - ", " | ", " : ", " – "]: # Added en-dash
                        if sep in title:
                            parts = title.split(sep)
                            # Only split if the part after separator looks like a source (short or known)
                            if len(parts) > 1:
                                title = parts[0].strip()
                    
                    # More aggressive source stripping for Marathi news
                    sources_to_strip = [
                        "Saam TV", "साम टीव्ही", "Lokmat", "लोकमत", "ABP Majha", "एबीपी माझा", 
                        "TV9 Marathi", "टीव्ही९ मराठी", "Maharashtra Times", "महाराष्ट्र टाइम्स",
                        "News18 Lokmat", "न्यूज१८ लोकमत", "Zeenews", "झी न्यूज", "Sakal", "सकाळ",
                        "Pudhari", "पुढारी", "Loksatta", "लोकसत्ता", "Marathi News", "मराठी बातम्या",
                        "Latest News", "ताज्या बातम्या", "Breaking News", "ब्रेकिंग न्यूज"
                    ]
                    for src in sources_to_strip:
                        if title.endswith(src):
                            title = title[:-(len(src))].strip()
                        if title.endswith(f"({src})"):
                            title = title[:-(len(src)+2)].strip()
                    
                    # Clean up trailing separators again after source stripping
                    for sep in [" -", " |", " :", " –"]:
                        if title.endswith(sep):
                            title = title[:-len(sep)].strip()
                    
                    # Filter out non-news content (food, recipes, lifestyle, entertainment fluff)
                    unwanted_keywords = [
                        # English food/lifestyle
                        "recipe", "cooking", "rasodi", "rasoi", "kitchen", "food", "snack",
                        "lifestyle", "fashion", "beauty", "makeup", "diet", "health tip",
                        "home remedy", "weight loss", "yoga", "entertainment gossip",
                        # Marathi food/lifestyle
                        "रेसिपी", "रसोडी", "मेजवानी", "स्वयंपाक", "चव", "जेवण", "खाद्य",
                        "आहार टिप", "सौंदर्य", "फॅशन", "डाएट", "घरगुती उपाय",
                    ]
                    if any(kw.lower() in title.lower() for kw in unwanted_keywords):
                        continue
                        
                    news_items.append({
                        "title": title,
                        "link": entry.link,
                        "category": category,
                        "published": getattr(entry, "published", "Unknown"),
                        "source": entry.source.get("title", "Unknown") if hasattr(entry, "source") else "Unknown"
                    })
                    count += 1
            
            # Shuffle or return as is; they will be grouped by category initially
            logger.info(f"Successfully fetched {len(news_items)} total categorized news items.")
            return news_items
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []

if __name__ == "__main__":
    scraper = NewsScraper()
    news = scraper.fetch_latest_news()
    for idx, item in enumerate(news[:5]):
        print(f"{idx+1}. {item['title']} ({item['source']})")

import feedparser
import requests
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google News RSS for Marathi News
# HL = Marathi (mr), GL = India (IN)
MARATHI_NEWS_RSS = "https://news.google.com/rss/search?q=when:24h&hl=mr&gl=IN&ceid=IN:mr"

class NewsScraper:
    def __init__(self, rss_url: str = MARATHI_NEWS_RSS):
        self.rss_url = rss_url

    def fetch_latest_news(self) -> List[Dict]:
        """
        Fetches the latest news from the RSS feed.
        Returns a list of dictionaries containing news title, link, and publication date.
        """
        try:
            logger.info(f"Fetching news from {self.rss_url}")
            feed = feedparser.parse(self.rss_url)
            
            news_items = []
            for entry in feed.entries:
                news_items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.published,
                    "source": entry.source.get("title", "Unknown") if hasattr(entry, "source") else "Unknown"
                })
            
            logger.info(f"Successfully fetched {len(news_items)} news items.")
            return news_items
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []

if __name__ == "__main__":
    scraper = NewsScraper()
    news = scraper.fetch_latest_news()
    for idx, item in enumerate(news[:5]):
        print(f"{idx+1}. {item['title']} ({item['source']})")

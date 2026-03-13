from scraper import NewsScraper
print("Testing Scraper...")
s = NewsScraper()
news = s.fetch_latest_news()
print(f"News found: {len(news)}")
if news:
    print(news[0]['title'])

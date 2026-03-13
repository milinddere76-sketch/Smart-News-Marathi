import requests
import json

def trigger_manual():
    print("Fetching top news...")
    url = "https://snm-be-priyansh-dere.fly.dev/news/top?limit=1"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch news: {response.text}")
        return
        
    news = response.json().get("news", [])
    if not news:
        print("No news found")
        return
        
    title = news[0]["title"]
    print(f"Triggering script generation for: {title}")
    
    # Normally handled by background task, but we can test components
    script_url = f"https://snm-be-priyansh-dere.fly.dev/news/generate-script?title={requests.utils.quote(title)}"
    script_response = requests.post(script_url)
    print(f"Script Result: {script_response.text[:200]}...")

if __name__ == "__main__":
    trigger_manual()

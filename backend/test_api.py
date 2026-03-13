import requests
import time

URL = "https://snm-be-priyansh-dere.fly.dev"

def test_generation():
    print("Testing News API...")

    # 1. Fetch Top News
    print("1. Fetching Top News...")
    news_res = requests.get(f"{URL}/news/top")
    if not news_res.ok:
        print(news_res.text)
        return
    news = news_res.json().get('news', [])
    if not news:
        print("No news found.")
        return
        
    title = news[0]['title']
    print(f"Top News: {title}")

    # 2. Generate Script
    print("2. Generating Script...")
    script_res = requests.post(f"{URL}/news/generate-script", params={"title": title})
    if not script_res.ok:
        print(script_res.text)
        return
    script = script_res.json().get('script', '')
    print(f"Script: {script[:50]}...")

    # 3. Generate Voice
    print("3. Generating Voice...")
    voice_res = requests.post(f"{URL}/news/generate-voice", params={"script": script})
    if not voice_res.ok:
        print(voice_res.text)
        return
    audio_path = voice_res.json().get('audio_url', '')
    print(f"Voice Audio: {audio_path}")

    # 4. Generate Video
    print("4. Generating Video...")
    vid_res = requests.post(
        f"{URL}/news/generate-video", 
        params={
            "audio_path": audio_path, 
            "headline": title[:50], 
            "ticker": "Testing Live Stream from API"
        }
    )
    if not vid_res.ok:
        print(f"FAILED: {vid_res.status_code} - {vid_res.text}")
        return
    
    print(f"Result: {vid_res.json()}")

if __name__ == "__main__":
    test_generation()

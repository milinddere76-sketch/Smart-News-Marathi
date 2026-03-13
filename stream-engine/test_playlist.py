import os
import requests
from broadcaster import Broadcaster

def main():
    b = Broadcaster()
    try:
        resp = requests.get("http://localhost:8000/news/videos")
        videos = [f"http://localhost:8000/media/video/{v}" for v in resp.json()["videos"][:2]]
        print(f"Testing playlist stream for: {videos}")
        b.stream_playlist(videos)
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    main()

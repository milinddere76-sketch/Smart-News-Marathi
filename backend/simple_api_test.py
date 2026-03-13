import requests

def test_api():
    try:
        print("Testing API...")
        r = requests.get("https://snm-be-priyansh-dere.fly.dev/news/top", timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Text: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()

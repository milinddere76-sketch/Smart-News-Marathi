import requests
try:
    r = requests.get("https://www.google.com", timeout=5)
    print(f"Internet OK: {r.status_code}")
except Exception as e:
    print(f"Internet FAILED: {e}")

#Send test readings. Made using Chatgpt.
import requests, random, os
url = "http://127.0.0.1:8000/api/readings"
api_key = os.getenv("API_INGEST_KEY", "dev-123")  # load from env or fallback

payload = {
    "sensor": "temperature",
    "value": round(random.uniform(18.0, 25.0), 2)
}

headers = {"X-API-Key": api_key}

r = requests.post(url, json=payload, headers=headers, timeout=5)
print("Status:", r.status_code, "Response:", r.json())


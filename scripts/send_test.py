import requests, random
url = "http://127.0.0.1:8000/api/readings"
payload = {
    "sensor": "temperature",
    "value": round(random.uniform(18.0, 25.0), 2)
}
r = requests.post(url, json=payload, timeout=5)
print("Status:", r.status_code, "Response:", r.json())

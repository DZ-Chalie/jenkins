import requests
import json

# 백엔드에 직접 연결
url = "http://localhost:8000/search/similar"
payload = {"name": "막걸리", "exclude_id": None}

print(f" Testing: {url}")
print(f"Payload: {json.dumps(payload, ensure_ascii=False)}\n")

try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Got {len(data)} drinks\n")
        for drink in data[:3]:
            print(f"  - {drink}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Exception: {e}")

import requests

url = "http://localhost:8000/search/region"
params = {
    "province": "경기도",
    "season": "봄",
    "size": 5
}

try:
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"Found {len(data)} items.")
        if data:
            print(f"First item: {data[0]['name']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ Exception: {e}")

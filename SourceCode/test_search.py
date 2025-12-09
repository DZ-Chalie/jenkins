import requests
import json

url = "http://localhost:8000/search/search"
payload = {"query": "복순도가"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("Search Result:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Verify rich data fields exist
        if "image_url" in data and "pairing_food" in data:
            print("\nSUCCESS: Rich data fields found!")
        else:
            print("\nWARNING: Rich data fields missing.")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Exception: {e}")

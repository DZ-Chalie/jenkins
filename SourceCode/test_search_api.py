import requests
import json

BASE_URL = "http://localhost:8000"

def test_search(query):
    print(f"\nTesting Search for '{query}'...")
    try:
        res = requests.post(f"{BASE_URL}/search", json={"query": query})
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"Name Match: {data.get('name')}")
            print(f"Image URL: {data.get('image_url')}")
            if data.get('candidates'):
                print("Candidates:", len(data['candidates']))
                print(data['candidates'][:2])
        else:
            print("Error:", res.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_search("복순도가")

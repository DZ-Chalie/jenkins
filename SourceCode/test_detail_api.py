import requests
import json

BASE_URL = "http://localhost:8000"

def test_detail(drink_id):
    print(f"\nTesting Detail for ID {drink_id}...")
    try:
        res = requests.get(f"{BASE_URL}/search/detail/{drink_id}")
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"Name: {data.get('name')}")
            print(f"Image URL: {data.get('image_url')}")
        else:
            print("Error:", res.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_detail(123) # Use a likely ID, or search first to get one.
    # Let's search for '복순도가' to get an ID first.
    s_res = requests.post(f"{BASE_URL}/search", json={"query": "복순도가"})
    if s_res.status_code == 200:
        candidates = s_res.json().get('candidates', [])
        if candidates:
            first_id = candidates[0]['id']
            test_detail(first_id)

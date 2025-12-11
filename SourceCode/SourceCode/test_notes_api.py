import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_note():
    print("Testing Create Note...")
    payload = {
        "user_id": "test_user_123",
        "author_name": "TestUser",
        "liquor_id": 999,
        "liquor_name": "Test Liquor",
        "rating": 4.5,
        "flavor_profile": {
            "sweet": 3,
            "sour": 3,
            "body": 3,
            "scent": 3,
            "throat": 3
        },
        "content": "Test content",
        "tags": ["test"],
        "is_public": True,
        "images": ["https://example.com/image.jpg"]
    }
    
    try:
        res = requests.post(f"{BASE_URL}/notes", json=payload)
        print(f"Create Status: {res.status_code}")
        print(res.text)
        if res.status_code == 200:
            return res.json()["_id"]
    except Exception as e:
        print(f"Request failed: {e}")
    return None

if __name__ == "__main__":
    test_create_note()

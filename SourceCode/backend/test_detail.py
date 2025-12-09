import requests
import time

def test_detail_endpoint():
    # 1. Get a valid drink_id from ES (via search endpoint)
    # We can use the region search to get a list and pick one ID
    print("🔍 Fetching a valid drink_id...")
    try:
        # Assuming the server is running on localhost:8000 inside the container
        # We use the region search we just built
        response = requests.get("http://localhost:8000/search/region?province=경기도&size=1")
        if response.status_code != 200:
            print(f"❌ Failed to fetch region drinks: {response.text}")
            return

        data = response.json()
        if not data:
            print("❌ No drinks found in Gyeonggi-do to test with.")
            return

        test_id = data[0]['id']
        print(f"✅ Found drink_id: {test_id}")

        # 2. Test the detail endpoint
        print(f"🚀 Testing /detail/{test_id}...")
        detail_response = requests.get(f"http://localhost:8000/search/detail/{test_id}")
        
        if detail_response.status_code == 200:
            detail = detail_response.json()
            print("✅ Detail Endpoint Success!")
            print(f"   Name: {detail.get('name')}")
            print(f"   Type: {detail.get('type')}")
            print(f"   Foods: {detail.get('foods')}")
        else:
            print(f"❌ Detail Endpoint Failed: {detail_response.status_code}")
            print(detail_response.text)

    except Exception as e:
        print(f"❌ Test Error: {e}")

if __name__ == "__main__":
    # Wait a bit for server reload if needed
    time.sleep(2) 
    test_detail_endpoint()

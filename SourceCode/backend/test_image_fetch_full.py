import requests

url = "https://thesool.com/common/imageView.do?targetId=PR00001312&targetNm=PRODUCT"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://thesool.com/",
    "Connection": "keep-alive"
}

def test_fetch():
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        # 1. Visit main page to get cookies (if any)
        print("Visiting main page...")
        session.get("https://thesool.com/")
        
        # 2. Fetch image
        print("Fetching image...")
        response = session.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {len(response.content)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fetch()

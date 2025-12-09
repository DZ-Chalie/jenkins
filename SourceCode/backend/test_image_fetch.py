import requests

url = "https://thesool.com/common/imageView.do?targetId=PR00001312&targetNm=PRODUCT"

def test_fetch(headers=None, description="No Headers"):
    try:
        response = requests.head(url, headers=headers, timeout=5)
        print(f"[{description}] Status Code: {response.status_code}")
    except Exception as e:
        print(f"[{description}] Error: {e}")

if __name__ == "__main__":
    test_fetch(description="No Headers")
    test_fetch(headers={"Referer": "https://thesool.com/"}, description="Referer: thesool.com")
    test_fetch(headers={"Referer": "http://localhost:3000/"}, description="Referer: localhost")
    test_fetch(headers={"User-Agent": "Mozilla/5.0"}, description="User-Agent only")

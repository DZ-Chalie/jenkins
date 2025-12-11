import requests
import json

# 유사 전통주 검색 API 테스트
url = "http://localhost:8000/api/python/search/similar"
payload = {
    "name": "막걸리",
    "exclude_id": None
}

print("=" * 60)
print("🔍 유사 전통주 검색 API 테스트")
print("=" * 60)
print(f"\nURL: {url}")
print(f"요청: {json.dumps(payload, ensure_ascii=False)}\n")

try:
    response = requests.post(url, json=payload, timeout=10)
    
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ 성공! {len(data)}개의 유사 전통주 발견\n")
        
        for idx, drink in enumerate(data, 1):
            print(f"{idx}. {drink['name']}")
            print(f"   ID: {drink['id']}")
            print(f"   점수: {drink['score']:.2f}")
            print(f"   이미지: {drink['image_url'][:50] if drink.get('image_url') else 'N/A'}...\n")
    else:
        print(f"\n❌ 실패: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ 연결 실패: 백엔드가 실행 중인지 확인하세요")
except Exception as e:
    print(f"❌ 에러: {e}")

print("=" * 60)

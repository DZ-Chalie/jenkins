import requests
import json

# Elasticsearch 설정
ES_HOST = "http://192.168.0.182:9200"
INDEX_NAME = "liquor_integrated"

print("=" * 80)
print("🔍 Elasticsearch 양조장 데이터 확인")
print("=" * 80)

# 1. 양조장 필드가 있는 문서 개수 확인
try:
    response = requests.get(
        f"{ES_HOST}/{INDEX_NAME}/_count",
        json={
            "query": {
                "exists": {
                    "field": "brewery"
                }
            }
        }
    )
    
    if response.status_code == 200:
        count = response.json()["count"]
        print(f"\n✅ 양조장(brewery) 필드가 있는 문서: {count}개")
    else:
        print(f"❌ 개수 조회 실패: {response.status_code}")
except Exception as e:
    print(f"❌ 오류: {e}")

# 2. 양조장 데이터 샘플 조회
try:
    response = requests.get(
        f"{ES_HOST}/{INDEX_NAME}/_search",
        json={
            "size": 3,
            "query": {
                "exists": {
                    "field": "brewery.name"
                }
            },
            "_source": ["name", "brewery"]
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        hits = data["hits"]["hits"]
        
        print(f"\n📋 양조장 데이터 샘플 ({len(hits)}개):")
        print("-" * 80)
        
        for i, hit in enumerate(hits, 1):
            source = hit["_source"]
            print(f"\n{i}. 술 이름: {source.get('name', 'N/A')}")
            
            brewery = source.get("brewery", {})
            if brewery:
                print(f"   양조장 이름: {brewery.get('name', 'N/A')}")
                print(f"   주소: {brewery.get('address', 'N/A')}")
                print(f"   연락처: {brewery.get('contact', 'N/A')}")
                print(f"   홈페이지: {brewery.get('homepage', 'N/A')}")
            else:
                print("   ⚠️ 양조장 정보 없음")
    else:
        print(f"❌ 샘플 조회 실패: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ 오류: {e}")

# 3. 인덱스 매핑 확인
try:
    response = requests.get(f"{ES_HOST}/{INDEX_NAME}/_mapping")
    
    if response.status_code == 200:
        mapping = response.json()
        properties = mapping[INDEX_NAME]["mappings"]["properties"]
        
        print(f"\n🗺️ 'brewery' 필드 매핑:")
        print("-" * 80)
        
        if "brewery" in properties:
            brewery_mapping = properties["brewery"]
            print(json.dumps(brewery_mapping, indent=2, ensure_ascii=False))
        else:
            print("⚠️ brewery 필드가 매핑에 없습니다!")
    else:
        print(f"❌ 매핑 조회 실패: {response.status_code}")
except Exception as e:
    print(f"❌ 오류: {e}")

print("\n" + "=" * 80)

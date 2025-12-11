import requests
import json

# Elasticsearch 설정
ES_HOST = "http://192.168.0.182:9200"
INDEX_NAME = "liquor_integrated"

print("=" * 80)
print("🔍 Elasticsearch 문서 전체 구조 확인")
print("=" * 80)

try:
    # 문서 1개 조회
    response = requests.get(
        f"{ES_HOST}/{INDEX_NAME}/_search",
        json={"size": 1}
    )
    
    if response.status_code == 200:
        data = response.json()
        total = data["hits"]["total"]["value"]
        print(f"\n📊 전체 문서 개수: {total}개")
        
        if data["hits"]["hits"]:
            doc = data["hits"]["hits"][0]["_source"]
            print(f"\n📄 첫 번째 문서의 필드 목록:")
            print("-" * 80)
            for key in sorted(doc.keys()):
                value = doc[key]
                if isinstance(value, str):
                    preview = value[:50] + "..." if len(str(value)) > 50 else value
                elif isinstance(value, dict):
                    preview = f"{{객체: {len(value)} 필드}}"
                elif isinstance(value, list):
                    preview = f"[배열: {len(value)} 항목]"
                else:
                    preview = str(value)
                print(f"  ✓ {key}: {preview}")
            
            print(f"\n📋 전체 문서 내용:")
            print("-" * 80)
            print(json.dumps(doc, indent=2, ensure_ascii=False))
        else:
            print("⚠️ 문서가 없습니다!")
    else:
        print(f"❌ 조회 실패: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ 오류: {e}")

print("\n" + "=" * 80)

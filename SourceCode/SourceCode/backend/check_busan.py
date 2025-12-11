import sys
import os

sys.path.append(os.path.join(os.getcwd(), "backend"))
from app.utils.es_client import get_es_client

def check_busan_data():
    es = get_es_client()
    if not es:
        print("❌ ES unavailable")
        return

    # 1. Search for "청탁" (Cheongtak)
    print("🔍 Searching for '청탁'...")
    query = {
        "query": {
            "match": {
                "drink_name": "청탁"
            }
        }
    }
    res = es.search(index="drink_info", body=query)
    for hit in res['hits']['hits']:
        src = hit['_source']
        print(f"✅ Found Liquor: {src.get('drink_name')}")
        print(f"  - Province: {src.get('province')}")
        print(f"  - City: {src.get('city')}")
        print(f"  - Address: {src.get('drink_city')}")

    # 2. Check counts for Province="부산광역시" vs Province="경상남도"
    print("\n📊 Checking Province Counts:")
    for prov in ["부산광역시", "경상남도"]:
        q = {"query": {"term": {"province.keyword": prov}}}
        count = es.count(index="drink_info", body=q)['count']
        print(f"  - {prov}: {count} items")

if __name__ == "__main__":
    check_busan_data()

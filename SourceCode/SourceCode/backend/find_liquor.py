import sys
import os

sys.path.append(os.path.join(os.getcwd(), "backend"))
from app.utils.es_client import get_es_client

def find_yangji_baekju():
    es = get_es_client()
    if not es:
        print("❌ ES unavailable")
        return

    # Try searching for the name directly
    query = {
        "query": {
            "match": {
                "drink_name": {
                    "query": "양지 백주",
                    "fuzziness": "AUTO"
                }
            }
        }
    }
    
    print("🔍 Searching for '양지 백주'...")
    res = es.search(index="drink_info", body=query)
    hits = res['hits']['hits']
    
    if not hits:
        print("❌ '양지 백주' not found in ES.")
    else:
        for hit in hits:
            src = hit['_source']
            print(f"✅ Found: {src.get('drink_name')}")
            print(f"  - Province: {src.get('province')}")
            print(f"  - City: {src.get('city')}")
            print(f"  - Address: {src.get('drink_city')}") # Original address field

if __name__ == "__main__":
    find_yangji_baekju()

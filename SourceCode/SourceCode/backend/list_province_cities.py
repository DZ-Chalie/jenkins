import sys
import os

sys.path.append(os.path.join(os.getcwd(), "backend"))
from app.utils.es_client import get_es_client

def list_cities():
    es = get_es_client()
    if not es: return

    target_provinces = ["경상남도", "경상북도", "경기도", "충청남도", "전라남도"]
    
    for prov in target_provinces:
        print(f"\nProbing {prov}...")
        query = {
            "size": 0,
            "query": {"term": {"province.keyword": prov}},
            "aggs": {
                "cities": {
                    "terms": {"field": "city.keyword", "size": 100}
                }
            }
        }
        res = es.search(index="drink_info", body=query)
        buckets = res['aggregations']['cities']['buckets']
        for b in buckets:
            print(f"  - {b['key']} ({b['doc_count']})")

if __name__ == "__main__":
    list_cities()

import sys
import os
import json

# Add /app to sys.path to allow imports from app
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.utils.es_client import get_es_client

def check_gangwon_data():
    es = get_es_client()
    if not es:
        print("❌ Elasticsearch client not available")
        return

    query = {
        "query": {
            "match": {
                "province": "강원도"
            }
        },
        "size": 50
    }

    print(f"🔍 Searching for items in '강원도'...")
    try:
        response = es.search(index="drink_info", body=query)
        hits = response['hits']['hits']
        
        print(f"✅ Found {len(hits)} items.")
        
        cities = {}
        for hit in hits:
            source = hit['_source']
            name = source.get('drink_name')
            city = source.get('city')
            
            # Count city occurrences
            if city:
                cities[city] = cities.get(city, 0) + 1
            else:
                cities['None'] = cities.get('None', 0) + 1
                
            print(f"- {name}: City='{city}'")

        print("\n📊 City Distribution in Gangwon-do:")
        for c, count in cities.items():
            print(f"  - {c}: {count}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_gangwon_data()

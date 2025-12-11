import os
import json
from app.utils.es_client import get_es_client
from dotenv import load_dotenv

load_dotenv("backend.env")

es = get_es_client()

# Check specific drink '서울의 밤'
print("\n=== 6. Inspect 'Seoul Night' Document ===")
resp = es.search(index="liquor_integrated", body={
    "query": {
        "match": {
            "name": "서울의 밤"
        }
    },
    "size": 1
})

if resp['hits']['hits']:
    src = resp['hits']['hits'][0]['_source']
    print(f"ID: {src.get('drink_id')}")
    print(f"Name: {src.get('name')}")
    print(f"Encyclopedia Type: {type(src.get('encyclopedia'))}")
    print(f"Encyclopedia: {json.dumps(src.get('encyclopedia'), ensure_ascii=False)[:500]}...") # Truncate for readability
    print(f"Cocktails: {json.dumps(src.get('cocktails'), ensure_ascii=False)}")
    print(f"Selling Shops: {json.dumps(src.get('selling_shops'), ensure_ascii=False)}")
else:
    print("❌ '서울의 밤' NOT found in ES")

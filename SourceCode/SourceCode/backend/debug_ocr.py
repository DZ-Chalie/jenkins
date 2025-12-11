from app.utils.es_client import get_es_client
import json

es = get_es_client()

target_name = "서울의 밤"
noisy_query = "ion ...... 12:00 SOU NIGHT 서울의 밤 MUUI DISTIED HUAN SPIRITS 11 AIC/IOS https"

print(f"--- 1. Data Verification for '{target_name}' ---")
# Direct term query to find the doc
resp = es.search(index="liquor_integrated", body={
    "query": {"match": {"name": target_name}}
})

if resp['hits']['hits']:
    source = resp['hits']['hits'][0]['_source']
    print(f"Found ID: {source.get('drink_id')}")
    print(f"Name: {source.get('name')}")
    
    # Check Encyclopedia
    desc = source.get('description', '')
    print(f"\n[Encyclopedia Check]")
    print(f"Length: {len(desc)}")
    print(f"Preview: {desc[:50]}..." if desc else "EMPTY")
    
    # Check Cocktails
    cocktails = source.get('cocktails', [])
    print(f"\n[Cocktails Check]")
    print(f"Count: {len(cocktails)}")
    print(f"Data: {json.dumps(cocktails, ensure_ascii=False)}")
else:
    print("❌ Drink not found in ES!")

print(f"\n--- 2. Search Reproduction (Operator: AND) ---")
# Mimic current search logic
query_and = {
    "query": {
        "bool": {
            "should": [
                {"match": {"name": {"query": noisy_query, "operator": "and"}}}
            ]
        }
    }
}
resp_and = es.search(index="liquor_integrated", body=query_and)
print(f"Hits with AND: {len(resp_and['hits']['hits'])}")

print(f"\n--- 3. Search Fix Test (Operator: OR) ---")
query_or = {
    "query": {
        "bool": {
            "should": [
                {"match": {"name": {"query": noisy_query, "operator": "or", "minimum_should_match": "2<75%"}}} # Require some match
            ]
        }
    }
}
resp_or = es.search(index="liquor_integrated", body=query_or)
print(f"Hits with OR: {len(resp_or['hits']['hits'])}")
if resp_or['hits']['hits']:
    print(f"Top Hit: {resp_or['hits']['hits'][0]['_source']['name']}")

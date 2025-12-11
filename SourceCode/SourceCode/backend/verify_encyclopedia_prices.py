import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Load env
env_path = os.path.join(os.path.dirname(__file__), "backend.env")
load_dotenv(env_path)

ES_HOST = os.getenv("ELASTICSEARCH_HOST", "192.168.0.182")
ES_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")
ES_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "pass123")
ES_URL = f"http://{ES_HOST}:{ES_PORT}"

# Connect to ES
es = Elasticsearch(ES_URL, basic_auth=(ES_USERNAME, ES_PASSWORD))

# Query 1: Count by price source
print("=" * 60)
print("📊 Price Source Distribution")
print("=" * 60)

agg_query = {
    "size": 0,
    "aggs": {
        "by_source": {
            "terms": {
                "field": "price_source",
                "missing": "no_price"
            }
        }
    }
}

result = es.search(index="liquor_integrated", body=agg_query)
for bucket in result['aggregations']['by_source']['buckets']:
    print(f"  {bucket['key']}: {bucket['doc_count']} products")

print()

# Query 2: Sample encyclopedia-priced products
print("=" * 60)
print("📚 Sample Encyclopedia-Priced Products")
print("=" * 60)

sample_query = {
    "query": {"term": {"price_is_reference": True}},
    "size": 5,
    "_source": ["name", "lowest_price", "price_source", "price_is_reference"]
}

result = es.search(index="liquor_integrated", body=sample_query)
for hit in result['hits']['hits']:
    src = hit['_source']
    print(f"  • {src['name']}: ₩{src.get('lowest_price', 0):,} (참고가)")

print()

# Query 3: Total count
total = es.count(index="liquor_integrated")
print(f"✅ Total drinks indexed: {total['count']}")

# Query 4: Seasonal data check
season_query = {
    "query": {"exists": {"field": "season"}},
    "size": 0
}
season_result = es.search(index="liquor_integrated", body=season_query)
print(f"✅ Drinks with seasonal data: {season_result['hits']['total']['value']}")

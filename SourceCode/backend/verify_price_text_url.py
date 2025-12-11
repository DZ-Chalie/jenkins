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

print("=" * 80)
print("📚 Encyclopedia-Priced Products with Price Text and URL")
print("=" * 80)

# Query: Sample encyclopedia-priced products with new fields
sample_query = {
    "query": {"term": {"price_is_reference": True}},
    "size": 10,
    "_source": ["name", "lowest_price", "encyclopedia_price_text", "encyclopedia_url"]
}

result = es.search(index="liquor_integrated", body=sample_query)

for i, hit in enumerate(result['hits']['hits'], 1):
    src = hit['_source']
    print(f"\n{i}. {src['name']}")
    print(f"   Parsed Price: ₩{src.get('lowest_price', 0):,}")
    print(f"   Original Text: {src.get('encyclopedia_price_text', 'N/A')}")
    url = src.get('encyclopedia_url', 'N/A')
    if url != 'N/A':
        print(f"   URL: {url[:60]}...")
    else:
        print(f"   URL: {url}")

print("\n" + "=" * 80)
print(f"✅ Total encyclopedia-priced products: {result['hits']['total']['value']}")

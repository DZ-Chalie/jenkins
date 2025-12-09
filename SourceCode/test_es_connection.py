import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Load environment variables from backend.env
load_dotenv('backend/backend.env')

ES_URL = os.getenv("ELASTICSEARCH_URL")
ES_USERNAME = os.getenv("ELASTICSEARCH_USERNAME")
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")

print(f"Testing connection to: {ES_URL}")
print(f"Username: {ES_USERNAME}")

try:
    if ES_PASSWORD:
        es = Elasticsearch(ES_URL, basic_auth=(ES_USERNAME, ES_PASSWORD))
    else:
        es = Elasticsearch(ES_URL)

    if es.ping():
        print("\n✅ SUCCESS: Connected to Elasticsearch!")
        info = es.info()
        print(f"Cluster Name: {info['cluster_name']}")
        print(f"Version: {info['version']['number']}")
    else:
        print("\n❌ FAILED: Could not ping Elasticsearch.")

except Exception as e:
    print(f"\n❌ ERROR: Connection failed with exception:")
    print(e)

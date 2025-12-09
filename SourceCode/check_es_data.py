import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import json

# Load environment variables from backend.env
load_dotenv('backend/backend.env')

ES_URL = os.getenv("ELASTICSEARCH_URL")
ES_USERNAME = os.getenv("ELASTICSEARCH_USERNAME")
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")

print(f"Testing connection to: {ES_URL}")

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
        
        print("\n[Indices]")
        indices = es.cat.indices(v=True)
        print(indices)

        # Check for 'liquors' index
        if es.indices.exists(index="liquors"):
            print("\n[Data in 'liquors' index]")
            count = es.count(index="liquors")['count']
            print(f"Total Documents: {count}")
            
            if count > 0:
                print("\n[Sample Document]")
                res = es.search(index="liquors", size=1)
                print(json.dumps(res['hits']['hits'][0]['_source'], indent=2, ensure_ascii=False))
        else:
            print("\n⚠️ 'liquors' index NOT found.")

    else:
        print("\n❌ FAILED: Could not ping Elasticsearch.")

except Exception as e:
    print(f"\n❌ ERROR: Connection failed with exception:")
    print(e)

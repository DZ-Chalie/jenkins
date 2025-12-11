import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import json

ES_URL = "http://192.168.0.36:9200"
ES_USERNAME = "elastic"
ES_PASSWORD = "pass123"

print(f"Connecting to: {ES_URL}")

try:
    es = Elasticsearch(ES_URL, basic_auth=(ES_USERNAME, ES_PASSWORD))

    if es.ping():
        print("✅ Connected to Elasticsearch")
        
        # 1. List all indices
        print("\n[Indices]")
        indices = es.cat.indices(v=True)
        print(indices)

        # 2. Check 'liquors' index
        index_name = "liquors"
        if es.indices.exists(index=index_name):
            print(f"\n[Index '{index_name}' exists]")
            
            # Get mapping (structure)
            mapping = es.indices.get_mapping(index=index_name)
            # print("\n[Mapping Structure]")
            # print(json.dumps(mapping, indent=2, ensure_ascii=False))

            # Get 1 sample document
            res = es.search(index=index_name, size=1)
            hits = res['hits']['hits']
            if hits:
                print(f"\n[Sample Document from '{index_name}']")
                source = hits[0]['_source']
                print(json.dumps(source, indent=2, ensure_ascii=False))
                
                # Verification for OCR
                print("\n[OCR Matching Verification]")
                if 'name' in source:
                    print(f"✅ 'name' field found: {source['name']}")
                    print("   -> This field is used for fuzzy matching with OCR results.")
                else:
                    print("❌ 'name' field NOT found. OCR matching might fail.")
            else:
                print(f"\n⚠️ Index '{index_name}' is empty.")
        else:
            print(f"\n❌ Index '{index_name}' does NOT exist.")
            print("   -> Monstache might not have synced data yet, or MongoDB is empty.")

    else:
        print("❌ Could not ping Elasticsearch")

except Exception as e:
    print(f"Error: {e}")

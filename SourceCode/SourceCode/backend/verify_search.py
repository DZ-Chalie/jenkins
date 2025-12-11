from elasticsearch import Elasticsearch
import os

def verify_search():
    try:
        ES_HOST = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
        ES_PORT = os.getenv("ELASTICSEARCH_PORT", 9200)
        ES_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
        ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "pass123")
        ES_URL = f"http://{ES_HOST}:{ES_PORT}"

        es = Elasticsearch(ES_URL, basic_auth=(ES_USERNAME, ES_PASSWORD))
        query_text = "서울의 밤"
        print(f"🔍 Searching for: {query_text} at {ES_URL}")
        
        res = es.search(index='drink_info', body={
            'query': {
                'match': {
                    'drink_name': query_text
                }
            }
        })
        
        hits = res['hits']['total']['value']
        print(f"✅ Found {hits} hits")
        
        if hits > 0:
            for hit in res['hits']['hits']:
                print(f" - {hit['_source']['drink_name']}")
        else:
            print("❌ No results found.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_search()

from elasticsearch import Elasticsearch
import os

ES_HOST = os.getenv("ELASTICSEARCH_HOST", "192.168.0.36")
ES_PORT = os.getenv("ELASTICSEARCH_PORT", 9200)
ES_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "pass123")
ES_URL = f"http://{ES_HOST}:{ES_PORT}"

es = Elasticsearch(ES_URL, basic_auth=(ES_USERNAME, ES_PASSWORD))

def check_data():
    query = {
        "query": {
            "match": {
                "drink_name": "지란지교"
            }
        }
    }
    res = es.search(index="drink_info", body=query, size=10)
    print(f"Total hits: {res['hits']['total']['value']}")
    for hit in res['hits']['hits']:
        print(f"- {hit['_source']['drink_name']} (Score: {hit['_score']})")

if __name__ == "__main__":
    check_data()

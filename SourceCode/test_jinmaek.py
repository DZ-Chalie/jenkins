import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv('backend/backend.env')

ES_HOST = os.getenv('ELASTICSEARCH_HOST')
ES_PORT = os.getenv('ELASTICSEARCH_PORT')
ES_USERNAME = os.getenv('ELASTICSEARCH_USERNAME')
ES_PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD')

es = Elasticsearch(
    f"http://{ES_HOST}:{ES_PORT}",
    basic_auth=(ES_USERNAME, ES_PASSWORD)
)

# Search for 진맥소주
result = es.search(
    index='liquor_integrated',
    body={
        'query': {'match': {'name': '진맥소주 오크40%'}},
        'size': 1,
        '_source': ['drink_id', 'name', 'price_is_reference', 'encyclopedia_price_text', 'encyclopedia_url', 'selling_shops']
    }
)

if result['hits']['hits']:
    hit = result['hits']['hits'][0]
    source = hit['_source']
    print(f"=== 진맥소주 오크40% Data ===")
    print(f"ID: {source.get('drink_id')}")
    print(f"Name: {source.get('name')}")
    print(f"price_is_reference: {source.get('price_is_reference')}")
    print(f"encyclopedia_price_text: {source.get('encyclopedia_price_text')}")
    print(f"encyclopedia_url: {source.get('encyclopedia_url')}")
    print(f"selling_shops count: {len(source.get('selling_shops', []))}")
else:
    print("Not found")

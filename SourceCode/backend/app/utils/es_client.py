from elasticsearch import Elasticsearch
import os

ES_HOST = os.getenv("ELASTICSEARCH_HOST", "192.168.0.36")
ES_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")
ES_URL = f"http://{ES_HOST}:{ES_PORT}"

ES_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "pass123")

import time

def get_es_client(max_retries=5, retry_delay=2):
    retries = 0
    while retries < max_retries:
        try:
            # Use basic_auth if password is provided
            if ES_PASSWORD:
                es = Elasticsearch(ES_URL, basic_auth=(ES_USERNAME, ES_PASSWORD))
            else:
                es = Elasticsearch(ES_URL)
                
            if es.ping():
                print("Connected to Elasticsearch")
                return es
            else:
                print(f"Elasticsearch ping failed. Retrying ({retries+1}/{max_retries})...")
                try:
                    print(es.info())
                except Exception as e:
                    print(f"Debug Info: {e}")
        except Exception as e:
            print(f"Error connecting to Elasticsearch: {e}. Retrying ({retries+1}/{max_retries})...")
        
        retries += 1
        time.sleep(retry_delay)
    
    print("Could not connect to Elasticsearch after multiple attempts.")
    return None

def create_index_if_not_exists(es, index_name="liquors"):
    if not es.indices.exists(index=index_name):
        es.indices.create(
            index=index_name,
            body={
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "nori_analyzer": {
                                "tokenizer": "nori_tokenizer"
                            },
                            "hangul_to_latin": {
                                "tokenizer": "standard",
                                "filter": ["icu_transform_hangul_latin", "lowercase"]
                            }
                        },
                        "filter": {
                            "icu_transform_hangul_latin": {
                                "type": "icu_transform",
                                "id": "Hangul-Latin; NFD; [:Nonspacing Mark:] Remove; NFC" 
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "name": {
                            "type": "text", 
                            "analyzer": "nori_analyzer",
                            "fields": {
                                "romanized": {
                                    "type": "text",
                                    "analyzer": "hangul_to_latin"
                                }
                            }
                        }, 
                        "description": {"type": "text", "analyzer": "nori_analyzer"},
                        "intro": {"type": "text", "analyzer": "nori_analyzer"},
                        "tags": {"type": "keyword"},
                        "image_url": {"type": "keyword"},
                        "url": {"type": "keyword"},
                        "pairing_food": {"type": "text", "analyzer": "nori_analyzer"},
                        "detail": {
                            "properties": {
                                "기타": {"type": "text"},
                                "수상내역": {"type": "text"},
                                "알콜도수": {"type": "keyword"},
                                "용량": {"type": "keyword"},
                                "원재료": {"type": "text"},
                                "종류": {"type": "keyword"}
                            }
                        },
                        "brewery": {
                            "properties": {
                                "name": {"type": "text", "analyzer": "nori_analyzer"},
                                "address": {"type": "text"},
                                "contact": {"type": "keyword"},
                                "homepage": {"type": "keyword"}
                            }
                        }
                    }
                }
            }
        )
        print(f"Index '{index_name}' created with ICU analyzer.")

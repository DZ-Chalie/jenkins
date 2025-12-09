from app.utils.es_client import get_es_client
import json

def debug_search():
    es = get_es_client()
    index_name = "drink_info"
    text = "지란 지고"
    
    print(f"🔍 Analyzing Query: '{text}'")
    
    # 1. Analyze Query Tokens (Nori)
    analyze_nori = es.indices.analyze(index=index_name, body={
        "analyzer": "nori_analyzer",
        "text": text
    })
    print("\n[Nori Analyzer Tokens]")
    for token in analyze_nori['tokens']:
        print(f" - {token['token']}")

    # 2. Analyze Query Tokens (Ngram)
    analyze_ngram = es.indices.analyze(index=index_name, body={
        "analyzer": "ngram_analyzer",
        "text": text
    })
    print("\n[Ngram Analyzer Tokens]")
    for token in analyze_ngram['tokens']:
        print(f" - {token['token']}")

    # 2.5 Analyze Target Documents
    print("\n🔍 Analyzing '지란지교' Tokens...")
    analyze_doc1 = es.indices.analyze(index=index_name, body={"analyzer": "nori_analyzer", "text": "지란지교"})
    print(" [Nori] ", [t['token'] for t in analyze_doc1['tokens']])
    analyze_doc1_ngram = es.indices.analyze(index=index_name, body={"analyzer": "ngram_analyzer", "text": "지란지교"})
    print(" [Ngram] ", [t['token'] for t in analyze_doc1_ngram['tokens']])

    print("\n🔍 Analyzing '가와지탁주' Tokens...")
    analyze_doc2 = es.indices.analyze(index=index_name, body={"analyzer": "nori_analyzer", "text": "가와지탁주"})
    print(" [Nori] ", [t['token'] for t in analyze_doc2['tokens']])
    analyze_doc2_ngram = es.indices.analyze(index=index_name, body={"analyzer": "ngram_analyzer", "text": "가와지탁주"})
    print(" [Ngram] ", [t['token'] for t in analyze_doc2_ngram['tokens']])

    # 3. Check if '지란지교' exists
    print("\n🔍 Checking '지란지교' in Index...")
    doc_search = es.search(index=index_name, body={
        "query": {
            "match": {
                "drink_name": "지란지교"
            }
        }
    })
    if doc_search['hits']['hits']:
        print(f"✅ Found '지란지교': {doc_search['hits']['hits'][0]['_source']['drink_name']}")
    else:
        print("❌ '지란지교' NOT FOUND in index!")

    # 4. Run Explain Query
    print("\n🔍 Running Explain Query...")
    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "drink_name": {
                                "query": text,
                                "fuzziness": "AUTO",
                                "boost": 2.0,
                                "minimum_should_match": "70%" 
                            }
                        }
                    },
                    {
                        "match": {
                            "drink_name.ngram": {
                                "query": text,
                                "fuzziness": "AUTO"
                            }
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "size": 3
    }
    
    response = es.search(index=index_name, body=query)
    print("\n[Search Results]")
    for hit in response['hits']['hits']:
        print(f" - {hit['_source']['drink_name']} (Score: {hit['_score']})")

if __name__ == "__main__":
    debug_search()

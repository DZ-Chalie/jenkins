from app.utils.es_client import get_es_client

es = get_es_client()
if es:
    res = es.search(index="liquor_integrated", body={
        "query": {"exists": {"field": "season"}},
        "size": 5,
        "_source": ["name", "season"]
    })
    print("Sample docs with season:", res['hits']['hits'])
else:
    print("ES connection failed")

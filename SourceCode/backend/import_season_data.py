import csv
import os
from elasticsearch import Elasticsearch, helpers

# Connect to Elasticsearch
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "192.168.0.36")
ES_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")
ES_URL = f"http://{ES_HOST}:{ES_PORT}"
ES_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "pass123")

print(f"Connecting to ES at {ES_URL}...")
if ES_PASSWORD:
    es = Elasticsearch(ES_URL, basic_auth=(ES_USERNAME, ES_PASSWORD))
else:
    es = Elasticsearch(ES_URL)

CSV_PATH = "app/data/season.csv.csv" # Adjust path relative to where we run it, or absolute
# In Docker, it might be /app/data/... but we will run this from host or via docker exec.
# Let's try running from host first if ES port is exposed, or docker exec.
# Assuming docker exec context: path is /app/data/season.csv.csv (if mapped)

def import_season_data():
    if not os.path.exists(CSV_PATH):
        # Try absolute path just in case we run from different cwd
        print(f"File not found at {CSV_PATH}, checking alternate...")
        # Fallback or error
        return

    print(f"Reading {CSV_PATH}...")
    
    encodings = ['utf-8-sig', 'cp949', 'euc-kr', 'utf-8']
    rows = []
    
    for enc in encodings:
        try:
            print(f"Trying encoding: {enc}...")
            with open(CSV_PATH, 'r', encoding=enc) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            print(f"Successfully read with {enc}. Row count: {len(rows)}")
            break
        except UnicodeDecodeError:
            print(f"Failed with {enc}")
            continue
        except Exception as e:
            print(f"Error with {enc}: {e}")
            break
            
    if not rows:
        print("Failed to read CSV with any encoding.")
        return

    actions = []  # Initialize here
    
    # Check indices
    print("Indices:", es.indices.get_alias(index="*").keys())

    for row in rows:
        # We have 'name' and 'entry_name'. Let's try matching 'name' first, then 'entry_name'
        # Actually, 'entry_name' in CSV (e.g. "소백산 생 막걸리") looks more like the spacing in ES ("소백산 생 막걸리")
        # 'name' in CSV (e.g. "소백산생막걸리") is compacted.
        # But 'name' field in ES is analyzed text, so both should match.
        
        candidates = [row.get('entry_name'), row.get('name')]
        candidates = [c for c in candidates if c]
        
        season = row.get('season')
        if not season:
            continue
        season = season.strip()
        
        matched_id = None
        matched_index = None
        
        for search_name in candidates:
            # Try liquors first
            try:
                res = es.search(index="liquors", body={
                    "query": {
                        "match": {
                            "name": search_name
                        }
                    }
                })
                if res['hits']['total']['value'] > 0:
                    matched_id = res['hits']['hits'][0]['_id']
                    matched_index = res['hits']['hits'][0]['_index']
                    break
            except Exception:
                pass
            
            # If not found, try drink_info
            try:
                # drink_info uses 'drink_name' usually, let's try both fields
                res = es.search(index="drink_info", body={
                    "query": {
                        "match": {
                            "drink_name": search_name
                        }
                    }
                })
                if res['hits']['total']['value'] > 0:
                    matched_id = res['hits']['hits'][0]['_id']
                    matched_index = res['hits']['hits'][0]['_index']
                    break
            except Exception:
                pass
        
        if matched_id:
            # print(f"Found {candidates[0]} in {matched_index}")
            actions.append({
                "_op_type": "update",
                "_index": matched_index,
                "_id": matched_id,
                "doc": {
                    "season": season
                }
            })
        else:
             pass 
             # print(f"⚠️ Not found in ES: {candidates[0]}")

    if actions:
        print(f"Updating {len(actions)} documents...")
        success, failed = helpers.bulk(es, actions, stats_only=True)
        print(f"Success: {success}, Failed: {failed}")
    else:
        print("No actions to perform.")

if __name__ == "__main__":
    # We might need to adjust path if running inside docker
    # If running inside docker container source-backend-1:
    CSV_PATH = "/app/data/season.csv.csv"
    import_season_data()

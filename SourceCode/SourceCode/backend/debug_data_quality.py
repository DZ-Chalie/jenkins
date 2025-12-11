import os
import pymysql
import json
from app.utils.es_client import get_es_client
from dotenv import load_dotenv

load_dotenv("backend.env")

es = get_es_client()

print("\n=== 1. Inspect MariaDB Shop Table Schema ===")
try:
    conn = pymysql.connect(
        host=os.getenv("MARIADB_HOST"),
        port=int(os.getenv("MARIADB_PORT", 3306)),
        user=os.getenv("MARIADB_USER"),
        password=os.getenv("MARIADB_PASSWORD"),
        database=os.getenv("MARIADB_DB"),
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    cursor.execute("DESCRIBE menu_shop")
    print(cursor.fetchall())
    
    print("\n--- Sample Shop Data ---")
    cursor.execute("SELECT * FROM menu_shop LIMIT 3")
    print(cursor.fetchall())
    
    print("\n--- Sample Cocktail Data (for images) ---")
    cursor.execute("SELECT cocktail_title, cocktail_image_url FROM cocktail_info WHERE cocktail_image_url IS NOT NULL AND cocktail_image_url != '' LIMIT 3")
    print(cursor.fetchall())
    
    conn.close()
except Exception as e:
    print(f"DB Error: {e}")

print("\n=== 2. Inspect Elasticsearch 'Liquor' Document ===")
# Search for a drink that likely has data (e.g. one with cocktails or encyclopedia)
resp = es.search(index="liquor_integrated", body={
    "query": {
        "bool": {
            "should": [
                {"exists": {"field": "encyclopedia"}},
                {"exists": {"field": "selling_shops"}}
            ]
        }
    },
    "size": 1
})

if resp['hits']['hits']:
    src = resp['hits']['hits'][0]['_source']
    print(f"Name: {src.get('name')}")
    print(f"Encyclopedia field type: {type(src.get('encyclopedia'))}")
    print(f"Encyclopedia content: {json.dumps(src.get('encyclopedia'), ensure_ascii=False)[:300]}...")
    print(f"Selling Shops: {json.dumps(src.get('selling_shops'), ensure_ascii=False)}")
    print(f"Cocktails: {json.dumps(src.get('cocktails'), ensure_ascii=False)}")
else:
    print("❌ No documents found with encyclopedia or shops")

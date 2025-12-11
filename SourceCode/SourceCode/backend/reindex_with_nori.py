import os
import pymysql
from elasticsearch import Elasticsearch, helpers
import sys
from pymongo import MongoClient
import urllib.parse

# Environment Variables
MARIADB_HOST = os.getenv("MARIADB_HOST", "192.168.0.36")
MARIADB_PORT = int(os.getenv("MARIADB_PORT", 3306))
MARIADB_USER = os.getenv("MARIADB_USER", "root")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD", "pass123#")
MARIADB_DB = os.getenv("MARIADB_DB", "drink")

ES_HOST = os.getenv("ELASTICSEARCH_HOST", "192.168.0.36")
ES_PORT = os.getenv("ELASTICSEARCH_PORT", 9200)
ES_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "pass123")

ES_URL = f"http://{ES_HOST}:{ES_PORT}"

# MongoDB Config
MONGODB_HOST = os.getenv("MONGODB_HOST", "192.168.0.36")
MONGODB_PORT = os.getenv("MONGODB_PORT", "27017")
MONGODB_USER = os.getenv("MONGODB_USER", "root")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "pass123#")
MONGODB_AUTH_DB = "admin"

def get_mariadb_conn():
    try:
        conn = pymysql.connect(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
            database=MARIADB_DB,
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4'
        )
        print("✅ MariaDB Connection Successful")
        return conn
    except Exception as e:
        print(f"❌ MariaDB Connection Failed: {e}")
        sys.exit(1)

def get_es_client():
    try:
        es = Elasticsearch(ES_URL, basic_auth=(ES_USERNAME, ES_PASSWORD))
        if es.ping():
            print("✅ Elasticsearch Connection Successful")
            return es
        else:
            print("❌ Elasticsearch Ping Failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Elasticsearch Connection Failed: {e}")
        sys.exit(1)

def get_mongo_price_map():
    try:
        encoded_password = urllib.parse.quote_plus(MONGODB_PASSWORD)
        mongo_url = f"mongodb://{MONGODB_USER}:{encoded_password}@{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_AUTH_DB}"
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=2000)
        
        # Check 'liquor' DB and 'products' collection
        db = client["liquor"]
        collection = db["products"]
        
        price_map = {}
        # Fetch only necessary fields: liquor_id and price
        cursor = collection.find({}, {"liquor_id": 1, "price": 1, "_id": 0})
        
        for doc in cursor:
            l_id = doc.get("liquor_id")
            price = doc.get("price")
            
            if l_id and price:
                # If multiple prices exist for same ID, take the lowest
                if l_id in price_map:
                    price_map[l_id] = min(price_map[l_id], price)
                else:
                    price_map[l_id] = price
                    
        print(f"✅ Loaded {len(price_map)} price records from MongoDB")
        return price_map
    except Exception as e:
        print(f"⚠️ MongoDB Connection/Fetch Failed: {e}")
        return {}



def reindex():
    conn = get_mariadb_conn()
    es = get_es_client()
    price_map = get_mongo_price_map()
    
    index_name = "drink_info"

    # 1. Define Index Settings with Nori Analyzer
    settings = {
        "settings": {
            "analysis": {
                "tokenizer": {
                    "nori_user_dict": {
                        "type": "nori_tokenizer",
                        "decompound_mode": "mixed"
                    },
                    "ngram_tokenizer": {
                        "type": "ngram",
                        "min_gram": 2,
                        "max_gram": 3,
                        "token_chars": ["letter", "digit"]
                    }
                },
                "analyzer": {
                    "nori_analyzer": {
                        "type": "custom",
                        "tokenizer": "nori_user_dict",
                        "filter": [
                            "nori_readingform",
                            "icu_transform", 
                            "lowercase"
                        ]
                    },
                    "ngram_analyzer": {
                        "type": "custom",
                        "tokenizer": "ngram_tokenizer",
                        "filter": ["lowercase"]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "drink_name": { 
                    "type": "text", 
                    "analyzer": "nori_analyzer",
                    "fields": {
                        "keyword": { "type": "keyword" },
                        "ngram": { 
                            "type": "text", 
                            "analyzer": "ngram_analyzer" 
                        }
                    }
                },
                "drink_origin": { 
                    "type": "text", 
                    "analyzer": "nori_analyzer" 
                },
                "drink_volume": { "type": "keyword" },
                "drink_url": { "type": "keyword" },
                "type_id": { "type": "long" },
                "province": { "type": "keyword" }, # New field for region filtering
                "city": { "type": "keyword" }, # New field for city filtering
                "lowest_price": { "type": "long" } # New field for sorting
            }
        }
    }

    # 2. Delete Existing Index
    if es.indices.exists(index=index_name):
        print(f"🗑️ Deleting existing index: {index_name}")
        es.indices.delete(index=index_name)
    
    # 3. Create New Index
    print(f"mj Creating new index: {index_name} with Nori analyzer")
    es.indices.create(index=index_name, body=settings)

    # 4. Load Encyclopedia Data
    import json
    encyclopedia_data = {}
    try:
        with open("data/전통주 지식백과.json", "r", encoding="utf-8") as f:
            encyclopedia_list = json.load(f)
            for item in encyclopedia_list:
                encyclopedia_data[item['name']] = item.get('naver', {}).get('sections', [])
        print(f"📚 Loaded {len(encyclopedia_data)} encyclopedia entries.")
    except Exception as e:
        print(f"⚠️ Failed to load encyclopedia data: {e}")

    # 5. Fetch Data from MariaDB
    print("📥 Fetching data from MariaDB...")
    documents = []
    with conn.cursor() as cursor:
        # Fetch all drinks with region info
        print("📥 Fetching drinks with region info...")
        sql_drinks = """
            SELECT d.*, r.province, r.city 
            FROM drink_info d
            LEFT JOIN drink_region dr ON d.drink_id = dr.drink_id
            LEFT JOIN region r ON dr.region_id = r.id
        """
        cursor.execute(sql_drinks)
        drinks = cursor.fetchall()
        
        # Fetch all cocktails linked to drinks
        print("🍹 Fetching cocktail recipes...")
        sql_cocktails = """
            SELECT c.*, b.drink_id 
            FROM cocktail_info c
            JOIN cocktail_base_bridge b ON c.cocktail_id = b.cocktail_id
        """
        cursor.execute(sql_cocktails)
        cocktails = cursor.fetchall()

        # Fetch all selling shops linked to drinks
        print("🏪 Fetching selling shops...")
        sql_shops = """
            SELECT s.shop_id, s.name, s.address, s.contact, s.url, sd.drink_id, sd.price
            FROM menu_shop s
            JOIN shop_drinks_bridge sd ON s.shop_id = sd.shop_id
        """
        cursor.execute(sql_shops)
        shops = cursor.fetchall()

        # Fetch pairing foods
        print("🍽️ Fetching pairing foods...")
        sql_foods = """
            SELECT f.name as food_name, b.drink_id
            FROM pairing_food f
            JOIN drink_pairing_food_bridge b ON f.id = b.food_id
        """
        cursor.execute(sql_foods)
        foods = cursor.fetchall()
        
        # Group foods by drink_id
        food_map = {}
        for f in foods:
            d_id = f['drink_id']
            if d_id not in food_map:
                food_map[d_id] = []
            food_map[d_id].append(f['food_name'])

        
        # Group cocktails by drink_id
        cocktail_map = {}
        for c in cocktails:
            d_id = c['drink_id']
            if d_id not in cocktail_map:
                cocktail_map[d_id] = []
            
            c_copy = c.copy()
            del c_copy['drink_id']
            cocktail_map[d_id].append(c_copy)

        # Group shops by drink_id
        shop_map = {}
        for s in shops:
            d_id = s['drink_id']
            if d_id not in shop_map:
                shop_map[d_id] = []
            
            s_copy = s.copy()
            del s_copy['drink_id']
            shop_map[d_id].append(s_copy)
        
        for row in drinks:
            # Add cocktails to the drink document
            row['cocktails'] = cocktail_map.get(row['drink_id'], [])
            
            # Add selling shops to the drink document
            row['selling_shops'] = shop_map.get(row['drink_id'], [])

            # Add pairing foods
            row['pairing_foods'] = food_map.get(row['drink_id'], [])

            # Add Encyclopedia Data
            if row['drink_name'] in encyclopedia_data:
                row['encyclopedia'] = encyclopedia_data[row['drink_name']]
            
            # --- NEW: Add Lowest Price from MongoDB ---
            d_id = row['drink_id']
            row['lowest_price'] = price_map.get(d_id, 0) # Default to 0 if no price found
            
            # --- NEW: Add Province Mapping ---
            # Now fetched directly from SQL JOIN as 'province'
            if not row.get('province'):
                row['province'] = "기타"
            
            if not row.get('city'):
                row['city'] = "기타"

            # Convert any non-serializable types if necessary
            doc = {
                "_index": index_name,
                "_source": row
            }
            documents.append(doc)
    
    print(f"📊 Found {len(documents)} records.")

    # 5. Bulk Index to Elasticsearch
    if documents:
        print("📤 Bulk indexing to Elasticsearch...")
        success, failed = helpers.bulk(es, documents, stats_only=True)
        print(f"✅ Successfully indexed: {success}")
        print(f"❌ Failed: {failed}")
    else:
        print("⚠️ No data to index.")

    conn.close()

if __name__ == "__main__":
    reindex()

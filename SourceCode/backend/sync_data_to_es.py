import os
import pymysql
from pymongo import MongoClient
from app.utils.es_client import get_es_client
from dotenv import load_dotenv

# Load env vars
load_dotenv("backend.env")

def get_mariadb_conn():
    try:
        conn = pymysql.connect(
            host=os.getenv("MARIADB_HOST", "192.168.0.36"),
            port=int(os.getenv("MARIADB_PORT", 3306)),
            user=os.getenv("MARIADB_USER", "root"),
            password=os.getenv("MARIADB_PASSWORD", "pass123#"),
            database=os.getenv("MARIADB_DB", "drink"),
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4'
        )
        return conn
    except Exception as e:
        print(f"❌ MariaDB Connection Error: {e}")
        return None

def connect_mongo():
    try:
        mongo_host = os.getenv("MONGODB_HOST", "192.168.0.36")
        mongo_port = os.getenv("MONGODB_PORT", "27017")
        mongo_user = os.getenv("MONGODB_USER", "root")
        mongo_pass = os.getenv("MONGODB_PASSWORD", "pass123#")
        
        if mongo_user and mongo_pass:
            mongo_url = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}"
        else:
            mongo_url = f"mongodb://{mongo_host}:{mongo_port}"
            
        client = MongoClient(mongo_url)
        return client["liquor"]["products"]
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {e}")
        return None

def sync_data():
    print("🚀 Starting Data Sync to Elasticsearch...")
    
    # 1. Connect to DBs
    mariadb = get_mariadb_conn()
    mongo_col = connect_mongo()
    es = get_es_client()
    
    if not mariadb or mongo_col is None or not es:
        print("❌ Database connection failed.")
        return

    # 2. Get all drinks from MariaDB with Region Info
    try:
        with mariadb.cursor() as cursor:
            print("📦 Fetching drinks from MariaDB...")
            sql = """
                SELECT d.drink_id, d.drink_name, d.drink_city, r.province, r.city
                FROM drink_info d
                LEFT JOIN drink_region dr ON d.drink_id = dr.drink_id
                LEFT JOIN region r ON dr.region_id = r.id
            """
            cursor.execute(sql)
            drinks = cursor.fetchall()
            print(f"✅ Found {len(drinks)} drinks in MariaDB.")
    except Exception as e:
        print(f"❌ MariaDB Query Error: {e}")
        return
    finally:
        mariadb.close()

    # Re-open connection for loop queries (or use the same one if kept open, but safer to reopen or keep open)
    # Let's keep a connection open for the loop
    mariadb = get_mariadb_conn()

    # 3. Update Elasticsearch
    updated_count = 0
    
    for drink in drinks:
        drink_id = drink['drink_id']
        drink_name = drink['drink_name']
        province = drink['province']
        city = drink['city']
        
        # Fallback for city/province if not in region table
        if not city and drink['drink_city']:
            city = drink['drink_city']
            # Simple heuristic for province if missing (can be improved)
            if not province:
                province = city.split(' ')[0] if ' ' in city else city

        # Get Lowest Price from MongoDB
        lowest_price = 0
        try:
            pipeline = [
                {"$match": {"liquor_id": drink_id}},
                {"$sort": {"price": 1}},
                {"$limit": 1}
            ]
            price_doc = list(mongo_col.aggregate(pipeline))
            if price_doc:
                lowest_price = price_doc[0].get('price', 0)
            else:
                # Fallback by name
                pipeline_name = [
                    {"$match": {"drink_name": drink_name}},
                    {"$sort": {"price": 1}},
                    {"$limit": 1}
                ]
                price_doc_name = list(mongo_col.aggregate(pipeline_name))
                if price_doc_name:
                    lowest_price = price_doc_name[0].get('price', 0)
        except Exception as e:
            print(f"⚠️ MongoDB Error for {drink_name}: {e}")

        # Get Selling Shops from MariaDB
        selling_shops = []
        try:
            with mariadb.cursor() as cursor:
                shop_sql = """
                    SELECT s.shop_id, s.name, s.address, s.contact, s.url, b.price
                    FROM shop_drinks_bridge b
                    JOIN menu_shop s ON b.shop_id = s.shop_id
                    WHERE b.drink_id = %s
                """
                cursor.execute(shop_sql, (drink_id,))
                shops = cursor.fetchall()
                for shop in shops:
                    selling_shops.append({
                        "shop_id": shop['shop_id'],
                        "name": shop['name'],
                        "address": shop['address'],
                        "contact": shop['contact'],
                        "url": shop['url'],
                        "price": shop['price']
                    })
        except Exception as e:
            print(f"⚠️ Shop Fetch Error for {drink_name}: {e}")

        # Update ES Document
        update_body = {
            "doc": {
                "province": province,
                "city": city,
                "lowest_price": lowest_price,
                "selling_shops": selling_shops,
                "drink_id": drink_id
            },
            "doc_as_upsert": True
        }
        
        try:
            # Try updating by drink_name as ID first (common pattern)
            search_res = es.search(index="drink_info", body={
                "query": {"match": {"drink_name.keyword": drink_name}}
            })
            
            if search_res['hits']['hits']:
                doc_id = search_res['hits']['hits'][0]['_id']
                es.update(index="drink_info", id=doc_id, body=update_body)
                updated_count += 1
                if updated_count % 10 == 0:
                    print(f"Updated {updated_count}...", end='\r')
            else:
                # print(f"⚠️ ES Doc not found for: {drink_name}")
                pass
                
        except Exception as e:
            print(f"❌ ES Update Error for {drink_name}: {e}")

    mariadb.close()
    print(f"\n✅ Successfully updated {updated_count} documents in Elasticsearch.")

if __name__ == "__main__":
    sync_data()

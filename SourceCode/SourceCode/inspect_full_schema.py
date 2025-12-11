import pymysql
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv("backend/backend.env")

print("=== 1. MariaDB Tables ===")
try:
    conn = pymysql.connect(
        host=os.getenv('MARIADB_HOST'),
        port=int(os.getenv('MARIADB_PORT', 3306)),
        user=os.getenv('MARIADB_USER'),
        password=os.getenv('MARIADB_PASSWORD'),
        database=os.getenv('MARIADB_DB'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = [list(t.values())[0] for t in cursor.fetchall()]
    print(tables)
    
    # Inspect likely interesting tables
    targets = ['drink_info', 'award', 'cocktail', 'drink_award_bridge', 'drink_cocktail_bridge']
    for t in tables:
        for target in targets:
            if target in t:
                print(f"\n--- {t} Schema ---")
                cursor.execute(f"DESCRIBE {t}")
                print([col['Field'] for col in cursor.fetchall()])
    conn.close()
except Exception as e:
    print(f"MariaDB Error: {e}")

print("\n=== 2. MongoDB Products Sample ===")
try:
    mongo_host = os.getenv("MONGODB_HOST", "192.168.0.36")
    mongo_port = os.getenv("MONGODB_PORT", "27017")
    mongo_user = os.getenv("MONGODB_USER", "root")
    mongo_pass = os.getenv("MONGODB_PASSWORD", "pass123#")
    
    url = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}"
    client = MongoClient(url)
    db = client["liquor"]
    col = db["products"]
    
    doc = col.find_one()
    if doc:
        # print keys
        print(doc.keys())
        print(f"Sample Price: {doc.get('price')}, Lprice: {doc.get('lprice')}")
    else:
        print("No documents found.")
except Exception as e:
    print(f"MongoDB Error: {e}")

print("\n=== 3. Data Directory ===")
try:
    print(os.listdir("../data"))
except Exception as e:
    print(e)

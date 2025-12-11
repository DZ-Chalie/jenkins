from pymongo import MongoClient
import urllib.parse

# User provided info:
# IP: 192.168.0.36
# Port: 27017
# User: root
# Pass: pass123#
# Auth DB: admin

# URL encode the password because it contains special characters (#)
username = "root"
password = urllib.parse.quote_plus("pass123#")
ip = "192.168.0.36"
port = 27017

# Construct connection string
mongo_url = f"mongodb://{username}:{password}@{ip}:{port}/admin"

print(f"Connecting to MongoDB at {ip}...")

try:
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    
    # Check connection
    client.admin.command('ping')
    print("✅ Connected to MongoDB successfully!")
    
    # List databases
    dbs = client.list_database_names()
    print(f"\n[Databases]: {dbs}")
    
    # Check specific database (assuming 'liquors' or 'test' or similar)
    # Let's look for a likely candidate
    target_db = None
    for db in dbs:
        if db not in ['admin', 'config', 'local']:
            target_db = db
            break
            
    if target_db:
        print(f"\nChecking database: '{target_db}'")
        db = client[target_db]
        collections = db.list_collection_names()
        print(f"[Collections]: {collections}")
        
        for col_name in collections:
            count = db[col_name].count_documents({})
            print(f" - Collection '{col_name}': {count} documents")
            
            if count > 0:
                print(f"   [Sample from '{col_name}']")
                print(db[col_name].find_one())
    else:
        print("\n⚠️ No user databases found (only system DBs).")

except Exception as e:
    print(f"\n❌ Connection failed: {e}")

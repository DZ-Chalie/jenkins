import os
import json
import csv
import pandas as pd
from pymongo import MongoClient
from app.utils.es_client import get_es_client, create_index_if_not_exists
from dotenv import load_dotenv

# Load env vars
load_dotenv("../backend.env")

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "traditional_liquor"
COLLECTION_NAME = "liquors"

def connect_mongo():
    try:
        client = MongoClient(MONGO_URL)
        return client[DB_NAME][COLLECTION_NAME]
    except Exception as e:
        print(f"MongoDB Connection Error: {e}")
        return None

def import_data(file_path):
    # 1. Load Data
    data = []
    if file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif file_path.endswith(".csv") or file_path.endswith(".xlsx"):
        df = pd.read_csv(file_path) if file_path.endswith(".csv") else pd.read_excel(file_path)
        data = df.to_dict(orient="records")
    else:
        print("Unsupported file format. Please use .json, .csv, or .xlsx")
        return

    print(f"Loaded {len(data)} records from {file_path}")

    # 2. Connect to DBs
    mongo_col = connect_mongo()
    es = get_es_client()
    
    if mongo_col is None or not es:
        print("Database connection failed.")
        return

    create_index_if_not_exists(es)

    # 3. Insert Data
    success_count = 0
    for item in data:
        try:
            # Ensure 'name' exists
            if "name" not in item:
                continue

            # Parse dot-notation keys into nested dicts
            parsed_item = {}
            for key, value in item.items():
                if pd.isna(value): # Skip NaN values
                    continue
                    
                parts = key.split('.')
                current = parsed_item
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value

            # MongoDB Upsert
            mongo_col.update_one(
                {"name": parsed_item["name"]}, 
                {"$set": parsed_item}, 
                upsert=True
            )

            # Construct ES Document
            es_doc = {
                "name": parsed_item.get("name"),
                "description": parsed_item.get("description", "") or parsed_item.get("intro", ""),
                "intro": parsed_item.get("intro", ""),
                "tags": parsed_item.get("tags", []) or parsed_item.get("keywords", []),
                "image_url": parsed_item.get("image_url", ""),
                "url": parsed_item.get("url", ""),
                "pairing_food": parsed_item.get("pairing_food", ""),
                "detail": parsed_item.get("detail", {}),
                "brewery": parsed_item.get("brewery", {})
            }
            
            es.index(index="drink_info", id=parsed_item["name"], document=es_doc)
            
            success_count += 1
        except Exception as e:
            print(f"Error importing {item.get('name')}: {e}")

    print(f"Successfully imported {success_count} items into MongoDB and Elasticsearch.")

if __name__ == "__main__":
    # Look for files in backend/data
    data_dir = os.path.join(os.path.dirname(__file__), "../../data")
    files = [f for f in os.listdir(data_dir) if f.endswith(('.json', '.csv', '.xlsx'))]
    
    if not files:
        print(f"No data files found in {data_dir}. Please put your file there.")
    else:
        print(f"Found files: {files}")
        target_file = os.path.join(data_dir, files[0]) # Pick the first one
        print(f"Processing {target_file}...")
        import_data(target_file)

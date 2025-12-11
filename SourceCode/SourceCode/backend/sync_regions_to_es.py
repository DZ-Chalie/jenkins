"""
Sync region data from MariaDB to Elasticsearch
This script adds region information to each drink in ES
"""
import pymysql
from app.utils.es_client import get_es_client
import os
from dotenv import load_dotenv

load_dotenv("backend.env")

# Connect to MariaDB
conn = pymysql.connect(
    host=os.getenv('MARIADB_HOST'),
    port=int(os.getenv('MARIADB_PORT', 3306)),
    user=os.getenv('MARIADB_USER'),
    password=os.getenv('MARIADB_PASSWORD'),
    database=os.getenv('MARIADB_DB'),
    charset='utf8mb4'
)

cursor = conn.cursor(pymysql.cursors.DictCursor)
es = get_es_client()

print("Fetching drink-region mappings from MariaDB...")

# Get all drink-region mappings with full region info
# Find the correct table name first
cursor.execute("SHOW TABLES;")
tables = [t[list(t.keys())[0]] for t in cursor.fetchall()]
print(f"Available tables: {tables}")

# Query to get drink-region mappings
query = """
    SELECT 
        di.drink_id,
        di.drink_name,
        r.province,
        r.city,
        dr.city_address
    FROM drink_region dr
    JOIN region r ON dr.region_id = r.id
    JOIN drink_info di ON dr.drink_id = di.drink_id
"""

cursor.execute(query)
mappings = cursor.fetchall()

print(f"Found {len(mappings)} drink-region mappings")

# Group by drink_name (ES uses drink_name as ID)
from collections import defaultdict
drink_regions = defaultdict(list)

for m in mappings:
    drink_regions[m['drink_name']].append({
        'province': m['province'],
        'city': m['city'] or m['city_address']
    })

print(f"Mapped regions for {len(drink_regions)} drinks")

# Update ES
updated_count = 0
for drink_name, regions in drink_regions.items():
    try:
        # Update ES document with region info
        es.update(
            index="liquors",
            id=drink_name,
            body={
                "doc": {
                    "regions": regions,
                    "provinces": list(set(r['province'] for r in regions)),
                    "cities": list(set(r['city'] for r in regions))
                },
                "doc_as_upsert": False
            }
        )
        updated_count += 1
        if updated_count % 10 == 0:
            print(f"Updated {updated_count} drinks...")
    except Exception as e:
        print(f"Error updating {drink_name}: {e}")

print(f"\n✓ Successfully updated {updated_count} drinks with region data!")

cursor.close()
conn.close()

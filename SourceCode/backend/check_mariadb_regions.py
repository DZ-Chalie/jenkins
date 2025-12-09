import pymysql
import json

# Connect to MariaDB
conn = pymysql.connect(
    host='192.168.0.36',
    user='root',
    password='pass123#',
    database='drink',
    charset='utf8mb4'
)

cursor = conn.cursor(pymysql.cursors.DictCursor)

print("=== Region Table ===")
cursor.execute("SELECT * FROM region LIMIT 10;")
regions = cursor.fetchall()
for r in regions:
    print(r)

print("\n=== Drink-Region Mapping ===")
cursor.execute("SELECT * FROM drink_region LIMIT 10;")
drink_regions = cursor.fetchall()
for dr in drink_regions:
    print(dr)

print("\n=== Full Region-Drink Mapping ===")
cursor.execute("""
    SELECT d.name as drink_name, r.region_name, r.region_code
    FROM drink_region dr
    JOIN region r ON dr.region_id = r.region_id
    JOIN drink d ON dr.drink_id = d.drink_id
    LIMIT 20;
""")
mappings = cursor.fetchall()
for m in mappings:
    print(m)

cursor.close()
conn.close()

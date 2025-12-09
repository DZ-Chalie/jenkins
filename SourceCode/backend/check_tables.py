import pymysql
import os
from dotenv import load_dotenv

load_dotenv("backend.env")

conn = pymysql.connect(
    host=os.getenv('MARIADB_HOST'),
    port=int(os.getenv('MARIADB_PORT', 3306)),
    user=os.getenv('MARIADB_USER'),
    password=os.getenv('MARIADB_PASSWORD'),
    database=os.getenv('MARIADB_DB'),
    charset='utf8mb4'
)

cursor = conn.cursor(pymysql.cursors.DictCursor)

# Show all tables
cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()
print("=== All Tables ===")
for t in tables:
    print(list(t.values())[0])

# Find drink table and show its structure
for t in tables:
    table_name = list(t.values())[0]
    if 'drink' in table_name.lower() and 'region' not in table_name.lower():
        print(f"\n=== Structure of {table_name} ===")
        cursor.execute(f"DESCRIBE {table_name};")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col['Field']}: {col['Type']}")
        
        print(f"\n=== Sample data from {table_name} (first 3 rows) ===")
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
        rows = cursor.fetchall()
        for row in rows:
            print(row)

cursor.close()
conn.close()

import os
import pymysql
import sys

# Load env vars manually if not loaded (Docker should have them)
# But we print them to be sure
print("--- Environment Variables ---")
print(f"MARIADB_HOST: {os.getenv('MARIADB_HOST')}")
print(f"MARIADB_PORT: {os.getenv('MARIADB_PORT')}")
print(f"MARIADB_USER: {os.getenv('MARIADB_USER')}")
print(f"MARIADB_DB: {os.getenv('MARIADB_DB')}")
print("-----------------------------")

try:
    conn = pymysql.connect(
        host=os.getenv("MARIADB_HOST"),
        port=int(os.getenv("MARIADB_PORT", 3306)),
        user=os.getenv("MARIADB_USER"),
        password=os.getenv("MARIADB_PASSWORD"),
import os
import pymysql
import sys

# Load env vars manually if not loaded (Docker should have them)
# But we print them to be sure
print("--- Environment Variables ---")
print(f"MARIADB_HOST: {os.getenv('MARIADB_HOST')}")
print(f"MARIADB_PORT: {os.getenv('MARIADB_PORT')}")
print(f"MARIADB_USER: {os.getenv('MARIADB_USER')}")
print(f"MARIADB_DB: {os.getenv('MARIADB_DB')}")
print("-----------------------------")

try:
    conn = pymysql.connect(
        host=os.getenv("MARIADB_HOST"),
        port=int(os.getenv("MARIADB_PORT", 3306)),
        user=os.getenv("MARIADB_USER"),
        password=os.getenv("MARIADB_PASSWORD"),
        database="drink", # Explicitly check 'drink' database
        charset='utf8mb4'
    )
    print("✅ Connection Successful to 'drink' database!")
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT drink_name FROM drink_info WHERE drink_name LIKE '%서울%'")
        rows = cursor.fetchall()
        print(f"Found {len(rows)} drinks matching '서울':")
        for row in rows:
            print(f" - {row['drink_name']}")
            
    conn.close()
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    sys.exit(1)

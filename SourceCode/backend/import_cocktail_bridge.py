import os
import csv
import pymysql
import sys

# DB Connection
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MARIADB_HOST", "192.168.0.36"),
        port=int(os.getenv("MARIADB_PORT", 3306)),
        user=os.getenv("MARIADB_USER", "root"),
        password=os.getenv("MARIADB_PASSWORD", "pass123#"),
        database=os.getenv("MARIADB_DB", "drink"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def import_bridge():
    file_path = '/app/data/cocktail_base_bridge.csv'
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print("✅ Connecting to MariaDB...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Truncate Table
        print("🗑️ Truncating table 'cocktail_base_bridge'...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE cocktail_base_bridge")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # 2. Read CSV and Insert
        print(f"📖 Reading {file_path}...")
        
        data_to_insert = []
        # Try utf-8 first, then cp949
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data_to_insert.append((int(row['cocktail_id']), int(row['drink_id'])))
        except UnicodeDecodeError:
            print("⚠️ UTF-8 decode failed, trying cp949...")
            with open(file_path, 'r', encoding='cp949') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data_to_insert.append((int(row['cocktail_id']), int(row['drink_id'])))

        print(f"📦 Inserting {len(data_to_insert)} rows into cocktail_base_bridge...")
        
        sql = "INSERT INTO cocktail_base_bridge (cocktail_id, drink_id) VALUES (%s, %s)"
        
        cursor.executemany(sql, data_to_insert)
        conn.commit()
        print(f"✅ Successfully imported {len(data_to_insert)} records.")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import_bridge()

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

def import_data():
    file_path = '/app/data/drink_info.csv'
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print("✅ Connecting to MariaDB...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Truncate Table (Disable FK checks first)
        print("🗑️ Truncating table 'drink_info'...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE drink_info")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # 2. Read CSV and Insert
        print(f"📖 Reading {file_path}...")
        # Try cp949 encoding for Korean Windows CSVs
        with open(file_path, 'r', encoding='cp949') as f:
            reader = csv.reader(f)
            # Check if first row is header
            header = next(reader)
            # Simple heuristic: if first col is 'id' or 'drink_id', it's header
            if header[0].lower() in ['id', 'drink_id', 'no']:
                print(f"ℹ️ Header detected: {header}")
            else:
                print("ℹ️ No header detected, resetting file pointer.")
                f.seek(0)
                reader = csv.reader(f)

            count = 0
            for row in reader:
                # Mapping based on CSV header matching DB schema:
                # 0: drink_id, 1: drink_name, 2: drink_url, 3: drink_image_url, 4: drink_intro, 
                # 5: drink_abv, 6: drink_volume, 7: drink_origin, 8: drink_awards, 9: drink_etc, 
                # 10: brewery_id, 11: type_id, 12: drink_city
                
                sql = """
                INSERT INTO drink_info 
                (drink_id, drink_name, drink_url, drink_image_url, drink_intro, drink_abv, drink_volume, drink_origin, drink_awards, drink_etc, brewery_id, type_id, drink_city) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Clean up ABV (remove %)
                abv = row[5].replace('%', '').strip() if row[5] else None
                
                # Handle empty strings as None for integer fields
                brewery_id = row[10] if row[10] and row[10].isdigit() else None
                type_id = row[11] if row[11] and row[11].isdigit() else None

                cursor.execute(sql, (
                    row[0], row[1], row[2], row[3], row[4], abv, row[6], row[7], row[8], row[9], brewery_id, type_id, row[12]
                ))
                count += 1
                
                
        conn.commit()
        print(f"✅ Successfully imported {count} drink records.")

        # 3. Import Pairing Foods
        print("🍽️ Importing pairing foods...")
        cursor.execute("DROP TABLE IF EXISTS drink_pairing_food_bridge")
        cursor.execute("DROP TABLE IF EXISTS pairing_food")
        
        cursor.execute("""
            CREATE TABLE pairing_food (
                id INT PRIMARY KEY,
                name VARCHAR(255)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE drink_pairing_food_bridge (
                drink_id INT,
                food_id INT,
                PRIMARY KEY (drink_id, food_id)
            )
        """)
        
        # Import pairing_food.csv
        with open('/app/data/pairing_food.csv', 'r', encoding='cp949') as f: 
            reader = csv.reader(f)
            next(reader) # Skip header
            for row in reader:
                cursor.execute("INSERT INTO pairing_food (id, name) VALUES (%s, %s)", (row[0], row[1]))
                
        # Import drink_pairing_food_bridge.csv
        with open('/app/data/drink_pairing_food_bridge.csv', 'r', encoding='cp949') as f:
            reader = csv.reader(f)
            next(reader) # Skip header
            for row in reader:
                cursor.execute("INSERT IGNORE INTO drink_pairing_food_bridge (drink_id, food_id) VALUES (%s, %s)", (row[0], row[1]))
                
        conn.commit()
        print("✅ Successfully imported pairing foods.")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import_data()

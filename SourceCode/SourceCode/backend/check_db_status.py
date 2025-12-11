import os
import pymysql
from dotenv import load_dotenv

load_dotenv('backend/backend.env')

def check_schema_and_data():
    conn = pymysql.connect(
        host=os.getenv('MARIADB_HOST'),
        port=int(os.getenv('MARIADB_PORT')),
        user=os.getenv('MARIADB_USER'),
        password=os.getenv('MARIADB_PASSWORD'),
        db=os.getenv('MARIADB_DB'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with conn.cursor() as cursor:
            # 1. List all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("Tables in DB:", [list(t.values())[0] for t in tables])

            # 2. Check schema of shop_drinks_bridge
            cursor.execute("DESCRIBE shop_drinks_bridge")
            print("\nSchema of shop_drinks_bridge:")
            for col in cursor.fetchall():
                print(col)

            # 3. Check schema of shops (or menu_shop if exists)
            # We'll check 'shops' first as that's what we've been using
            if any('shops' in list(t.values())[0] for t in tables):
                cursor.execute("DESCRIBE shops")
                print("\nSchema of shops:")
                for col in cursor.fetchall():
                    print(col)
            
            # 4. Check for null prices
            cursor.execute("SELECT count(*) as total, count(price) as non_null_price FROM shop_drinks_bridge")
            counts = cursor.fetchone()
            print(f"\nPrice Stats: Total Rows: {counts['total']}, Non-Null Prices: {counts['non_null_price']}")
            
            cursor.execute("SELECT * FROM shop_drinks_bridge WHERE price IS NOT NULL LIMIT 5")
            print("\nSample Non-Null Price Rows:")
            for row in cursor.fetchall():
                print(row)

            cursor.execute("SELECT * FROM shop_drinks_bridge WHERE price IS NULL LIMIT 5")
            print("\nSample Null Price Rows:")
            for row in cursor.fetchall():
                print(row)

    finally:
        conn.close()

if __name__ == "__main__":
    check_schema_and_data()

import os
import pymysql
from dotenv import load_dotenv

load_dotenv('backend/backend.env')

def check_indices_and_duplicates():
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
            # 1. Check Indices
            cursor.execute("SHOW INDEX FROM shop_drinks_bridge")
            print("Indices on shop_drinks_bridge:")
            for idx in cursor.fetchall():
                print(idx)

            # 2. Check for duplicates
            cursor.execute("""
                SELECT shop_id, drink_id, count(*) as cnt 
                FROM shop_drinks_bridge 
                GROUP BY shop_id, drink_id 
                HAVING cnt > 1 
                LIMIT 5
            """)
            duplicates = cursor.fetchall()
            print(f"\nDuplicate Pairs (shop_id, drink_id): {len(duplicates)} found (showing max 5)")
            for row in duplicates:
                print(row)

            # 3. Check for 'menu_shop' table
            cursor.execute("SHOW TABLES LIKE 'menu_shop'")
            print(f"\nTable 'menu_shop' exists: {len(cursor.fetchall()) > 0}")

    finally:
        conn.close()

if __name__ == "__main__":
    check_indices_and_duplicates()

import os
import pymysql
from dotenv import load_dotenv

load_dotenv('backend/backend.env')

def compare_shops():
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
            # Check shops
            cursor.execute("SELECT shop_id, name FROM shops LIMIT 5")
            print("Shops table:")
            for row in cursor.fetchall():
                print(row)
                
            # Check menu_shop
            cursor.execute("SELECT shop_id, name FROM menu_shop LIMIT 5")
            print("\nMenu_shop table:")
            for row in cursor.fetchall():
                print(row)
                
    finally:
        conn.close()

if __name__ == "__main__":
    compare_shops()

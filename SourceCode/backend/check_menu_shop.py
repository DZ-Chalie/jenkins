import os
import pymysql
from dotenv import load_dotenv

load_dotenv('backend/backend.env')

def check_menu_shop():
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
            # 1. Check Schema
            cursor.execute("DESCRIBE menu_shop")
            print("Schema of menu_shop:")
            for col in cursor.fetchall():
                print(col)

            # 2. Check Content
            cursor.execute("SELECT * FROM menu_shop LIMIT 5")
            print("\nSample rows from menu_shop:")
            for row in cursor.fetchall():
                print(row)
                
            # 3. Check count
            cursor.execute("SELECT count(*) as cnt FROM menu_shop")
            print(f"\nTotal rows in menu_shop: {cursor.fetchone()['cnt']}")

    finally:
        conn.close()

if __name__ == "__main__":
    check_menu_shop()

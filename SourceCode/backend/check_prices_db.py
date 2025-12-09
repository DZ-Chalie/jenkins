import os
import pymysql
from dotenv import load_dotenv

load_dotenv('backend/backend.env')

def check_prices():
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
            cursor.execute("SELECT * FROM shop_drinks_bridge LIMIT 10")
            rows = cursor.fetchall()
            print("Sample rows from shop_drinks_bridge:")
            for row in rows:
                print(row)
                
            cursor.execute("SELECT count(*) as count FROM shop_drinks_bridge WHERE price IS NULL or price = 0")
            null_count = cursor.fetchone()
            print(f"Rows with null/zero price: {null_count['count']}")
            
    finally:
        conn.close()

if __name__ == "__main__":
    check_prices()

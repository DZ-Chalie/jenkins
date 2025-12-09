import os
import pymysql
from dotenv import load_dotenv

load_dotenv('backend/backend.env')

def check_shops():
    conn = pymysql.connect(
        host=os.getenv('MARIADB_HOST'),
        port=int(os.getenv('MARIADB_PORT')),
        user=os.getenv('MARIADB_USER'),
        password=os.getenv('MARIADB_PASSWORD'),
        db=os.getenv('MARIADB_DB'),
        charset='utf8mb4'
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT shop_id, name FROM shops LIMIT 20")
            shops = cursor.fetchall()
            print("Shops in DB:", shops)
            
            cursor.execute("SELECT count(*) as count FROM shops")
            count = cursor.fetchone()
            print("Total shops:", count['count'])
            
    finally:
        conn.close()

if __name__ == "__main__":
    check_shops()

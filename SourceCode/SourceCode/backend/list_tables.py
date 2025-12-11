import os
import pymysql
from dotenv import load_dotenv

load_dotenv('backend/backend.env')

def list_tables():
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
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("Tables in database:")
            for table in tables:
                print(table)
    finally:
        conn.close()

if __name__ == "__main__":
    list_tables()

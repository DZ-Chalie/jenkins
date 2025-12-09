import os
import pymysql
from dotenv import load_dotenv

load_dotenv('backend/backend.env')

def check_schema():
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
            cursor.execute("SHOW TABLES LIKE '%shop%'")
            tables = cursor.fetchall()
            print("Tables containing 'shop':", tables)
            
            for table in tables:
                table_name = table[0]
                print(f"\nSchema for {table_name}:")
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                for col in columns:
                    print(col)
                    
    finally:
        conn.close()

if __name__ == "__main__":
    check_schema()

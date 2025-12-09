import os
import pymysql
from dotenv import load_dotenv

load_dotenv('backend/backend.env')

def fix_schema():
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
            # 1. Truncate shop_drinks_bridge
            print("Truncating shop_drinks_bridge...")
            cursor.execute("TRUNCATE TABLE shop_drinks_bridge")
            
            # 2. Add Unique Index
            print("Adding unique index...")
            try:
                cursor.execute("ALTER TABLE shop_drinks_bridge ADD UNIQUE KEY unique_shop_drink (shop_id, drink_id)")
                print("Unique index added.")
            except pymysql.err.OperationalError as e:
                if e.args[0] == 1061: # Duplicate key name
                    print("Unique index already exists.")
                else:
                    raise e
            
            conn.commit()
            print("Schema fixed.")

    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()

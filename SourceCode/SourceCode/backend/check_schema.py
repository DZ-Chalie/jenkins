import os
import pymysql
import sys

# Environment Variables
MARIADB_HOST = os.getenv("MARIADB_HOST", "192.168.0.36")
MARIADB_PORT = int(os.getenv("MARIADB_PORT", 3306))
MARIADB_USER = os.getenv("MARIADB_USER", "root")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD", "pass123#")
MARIADB_DB = os.getenv("MARIADB_DB", "drink")

def check_schema():
    try:
        conn = pymysql.connect(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
            database=MARIADB_DB,
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute("DESCRIBE drink_info")
        columns = cursor.fetchall()
        for col in columns:
            print(f"{col['Field']} - {col['Type']}")
            
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_schema()

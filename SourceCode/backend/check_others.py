import os
import pymysql
import sys

# Environment Variables
MARIADB_HOST = os.getenv("MARIADB_HOST", "192.168.0.36")
MARIADB_PORT = int(os.getenv("MARIADB_PORT", 3306))
MARIADB_USER = os.getenv("MARIADB_USER", "root")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD", "pass123#")
MARIADB_DB = os.getenv("MARIADB_DB", "drink")

def check_others():
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
        
        # Count '기타'
        cursor.execute("SELECT count(*) as count FROM drink_region WHERE province = '기타'")
        count = cursor.fetchone()['count']
        print(f"📊 '기타'로 분류된 데이터 개수: {count}")
        
        if count > 0:
            print("\n--- '기타' 데이터 샘플 (최대 20개) ---")
            cursor.execute("SELECT * FROM drink_region WHERE province = '기타' LIMIT 20")
            others = cursor.fetchall()
            for row in others:
                print(f"ID: {row['drink_id']}, 주소: {row['city_address']}")
                
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_others()

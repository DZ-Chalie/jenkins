import sys
import os
import pymysql

sys.path.append(os.path.join(os.getcwd(), "backend"))
from app.db.mariadb import get_mariadb_conn

def check_region_table():
    os.environ["MARIADB_HOST"] = "192.168.0.36"
    os.environ["MARIADB_PORT"] = "3306"
    os.environ["MARIADB_USER"] = "root"
    os.environ["MARIADB_PASSWORD"] = "pass123#"
    os.environ["MARIADB_DB"] = "drink"
    
    conn = get_mariadb_conn()
    if not conn: return

    try:
        with conn.cursor() as cursor:
            # Check for Geumjeong-gu
            print("Checking Geumjeong-gu in region table:")
            cursor.execute("SELECT * FROM region WHERE city = '금정구'")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
                
            # Check for existing Busan provinces
            print("\nChecking any '부산광역시' in region table:")
            cursor.execute("SELECT * FROM region WHERE province = '부산광역시' LIMIT 5")
            rows = cursor.fetchall()
            if not rows:
                print("No rows found for Busan.")
            for row in rows:
                print(row)

    finally:
        conn.close()

if __name__ == "__main__":
    check_region_table()

import sys
import os
import pymysql

sys.path.append(os.path.join(os.getcwd(), "backend"))
from app.db.mariadb import get_mariadb_conn

def list_tables_and_columns():
    os.environ["MARIADB_HOST"] = "192.168.0.36"
    os.environ["MARIADB_PORT"] = "3306"
    os.environ["MARIADB_USER"] = "root"
    os.environ["MARIADB_PASSWORD"] = "pass123#"
    os.environ["MARIADB_DB"] = "drink"
    conn = get_mariadb_conn()
    if not conn:
        print("Failed to connect.")
        return

    try:
        with conn.cursor() as cursor:
            # List tables
            print("📊 Tables:")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_names = [list(t.values())[0] for t in tables]
            
            for table in table_names:
                print(f"\nExample Table: {table}")
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                for col in columns:
                    print(f"  - {col['Field']} ({col['Type']})")

    finally:
        conn.close()

if __name__ == "__main__":
    list_tables_and_columns()

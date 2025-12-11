
import pymysql
import sys
import os

try:
    conn = pymysql.connect(
        user="root",
        password=os.environ.get("MARIADB_ROOT_PASSWORD", "pass123#"),
        host="192.168.0.36",
        port=3306,
        database="drink"
    )
    cursor = conn.cursor()

    print("--- TABLES ---")
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor]
    print(tables)

    if 'fair_info' in tables:
        print("\n--- FAIR INFO ---")
        cursor.execute("SELECT * FROM fair_info")
        rows = cursor.fetchall()
        for r in rows:
            print(r)
    else:
        print("\n--- FAIR INFO TABLE MISSING ---")

    if 'cocktail_info' in tables:
        print("\n--- COCKTAIL INFO COUNT ---")
        cursor.execute("SELECT COUNT(*) FROM cocktail_info")
        print(cursor.fetchone()[0])
    
    conn.close()

except pymysql.Error as e:
    print(f"Error connecting to MariaDB: {e}")
    sys.exit(1)

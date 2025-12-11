import mariadb
import os
import sys

def get_mariadb_conn():
    try:
        conn = mariadb.connect(
            user="root",
            password="pass123#",
            host="192.168.0.36",
            port=3306,
            database="drink"
        )
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        sys.exit(1)

def check_data():
    conn = get_mariadb_conn()
    cursor = conn.cursor()
    
    print("--- Sample Data from drink_region ---")
    cursor.execute("SELECT province, city, city_address FROM drink_region LIMIT 10")
    for row in cursor.fetchall():
        print(f"Province: {row[0]}, City: {row[1]}, Address: {row[2]}")
        
    print("\n--- Checking specific examples ---")
    # Check for Mapo-gu (Seoul)
    cursor.execute("SELECT province, city, city_address FROM drink_region WHERE city_address LIKE '%마포구%' LIMIT 1")
    row = cursor.fetchone()
    if row:
        print(f"Mapo-gu Example -> Province: {row[0]}, City: {row[1]}")
    else:
        print("No Mapo-gu data found.")

    # Check for Yeongdong-gun (Chungbuk)
    cursor.execute("SELECT province, city, city_address FROM drink_region WHERE city_address LIKE '%영동군%' LIMIT 1")
    row = cursor.fetchone()
    if row:
        print(f"Yeongdong-gun Example -> Province: {row[0]}, City: {row[1]}")
    else:
        print("No Yeongdong-gun data found.")

if __name__ == "__main__":
    check_data()

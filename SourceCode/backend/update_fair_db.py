import pymysql
import csv
import os

DB_HOST = "192.168.0.36"
DB_PORT = 3306
DB_USER = "root"
DB_PASS = os.environ.get("MARIADB_ROOT_PASSWORD", "pass123#")
DB_NAME = "drink"

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def update_fair_info():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create table if not exists
    create_table_query = """
    CREATE TABLE IF NOT EXISTS fair_info (
        fair_id INT PRIMARY KEY,
        fair_year INT NOT NULL,
        fair_image_url VARCHAR(1000),
        fair_homepage_url VARCHAR(1000)
    )
    """
    cursor.execute(create_table_query)
    
    # Read CSV and insert data
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'fair_info.csv')
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            insert_query = """
            INSERT INTO fair_info (fair_id, fair_year, fair_image_url, fair_homepage_url)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                fair_year = VALUES(fair_year),
                fair_image_url = VALUES(fair_image_url),
                fair_homepage_url = VALUES(fair_homepage_url)
            """
            cursor.execute(insert_query, (
                int(row['fair_id']),
                int(row['fair_year']),
                row['fair_image_url'],
                row['fair_homepage_url']
            ))
    
    conn.commit()
    print(f"Inserted/Updated fair_info data successfully.")
    
    # Verify
    cursor.execute("SELECT * FROM fair_info ORDER BY fair_year DESC")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    
    conn.close()

if __name__ == "__main__":
    update_fair_info()

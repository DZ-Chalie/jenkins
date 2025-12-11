import os
import pymysql
from dotenv import load_dotenv

load_dotenv('backend/backend.env')

def check_images():
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
            # Check drink_info table for image URLs
            cursor.execute("SELECT drink_id, drink_name, drink_image_url FROM drink_info WHERE drink_image_url IS NOT NULL LIMIT 5")
            rows = cursor.fetchall()
            print("Sample drink images from drink_info:")
            for row in rows:
                print(row)
    finally:
        conn.close()

if __name__ == "__main__":
    check_images()


import pymysql
import pandas as pd
import os
import sys

# MariaDB Connection Details
DB_HOST = "192.168.0.36"
DB_PORT = 3306
DB_USER = "root"
DB_PASS = os.environ.get("MARIADB_ROOT_PASSWORD", "pass123#")
DB_NAME = "drink"

CSV_PATH = os.path.join(os.path.dirname(__file__), "data/cocktail_info.csv")

def update_cocktail_info():
    try:
        print("🔌 Connecting to MariaDB...")
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()

        # 1. Read CSV
        print(f"📖 Reading CSV from {CSV_PATH}...")
        df = pd.read_csv(CSV_PATH)
        df = df.where(pd.notnull(df), None) # Replace NaN with None for SQL

        # 2. Upsert Data (Avoid Drop Table due to FK)
        print("🔄 Upserting data into cocktail_info...")
        
        insert_sql = """
        INSERT INTO cocktail_info (
            cocktail_id, cocktail_title, cocktail_base, cocktail_glass, 
            cocktail_technique, cocktail_garnish, cocktail_recipe, 
            cocktail_method, cocktail_subject, cocktail_image_url, 
            cocktail_homepage_url
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            cocktail_title=VALUES(cocktail_title),
            cocktail_base=VALUES(cocktail_base),
            cocktail_glass=VALUES(cocktail_glass),
            cocktail_technique=VALUES(cocktail_technique),
            cocktail_garnish=VALUES(cocktail_garnish),
            cocktail_recipe=VALUES(cocktail_recipe),
            cocktail_method=VALUES(cocktail_method),
            cocktail_subject=VALUES(cocktail_subject),
            cocktail_image_url=VALUES(cocktail_image_url),
            cocktail_homepage_url=VALUES(cocktail_homepage_url)
        """
        
        values = []
        for _, row in df.iterrows():
            values.append((
                row['cocktail_id'], row['cocktail_title'], row['cocktail_base'],
                row['cocktail_glass'], row['cocktail_technique'], row['cocktail_garnish'],
                row['cocktail_recipe'], row['cocktail_method'], row['cocktail_subject'],
                row['cocktail_image_url'], row['cocktail_homepage_url']
            ))
            
        cursor.executemany(insert_sql, values)
        conn.commit()
        print("✅ Cocktail Info Updated Successfully!")
        
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_cocktail_info()

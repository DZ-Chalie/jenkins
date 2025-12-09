
import os
import pymysql
import pandas as pd
import numpy as np

def load_env_file(filepath):
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

def import_data():
    load_env_file('backend.env')
    
    host = os.getenv("MARIADB_HOST", "192.168.0.36")
    port = int(os.getenv("MARIADB_PORT", 3306))
    user = os.getenv("MARIADB_USER", "user")
    password = os.getenv("MARIADB_PASSWORD", "pass123#")
    db_name = os.getenv("MARIADB_DB", "db")

    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        # 1. Add missing column 'cocktail_homepage_url' if it doesn't exist
        print("Checking schema...")
        cursor.execute("DESCRIBE cocktail_info")
        columns = [row['Field'] for row in cursor.fetchall()]
        
        if 'cocktail_homepage_url' not in columns:
            print("Adding missing column 'cocktail_homepage_url'...")
            cursor.execute("ALTER TABLE cocktail_info ADD COLUMN cocktail_homepage_url VARCHAR(500) AFTER cocktail_image_url")
        else:
            print("Column 'cocktail_homepage_url' already exists.")
            
        conn.commit()
        
        # 2. Load CSV
        csv_path = 'data/cocktail_info.csv'
        print(f"Reading CSV from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        # Replace NaN with None for SQL NULL compatibility
        df = df.replace({np.nan: None})
        
        print(f"Loaded {len(df)} rows from CSV.")
        
        # 3. Update/Insert Data
        updated_count = 0
        inserted_count = 0
        
        for _, row in df.iterrows():
            c_id = row['cocktail_id']
            
            # Check if row exists
            cursor.execute("SELECT cocktail_id FROM cocktail_info WHERE cocktail_id = %s", (c_id,))
            exists = cursor.fetchone()
            
            if exists:
                # UPDATE
                sql = """
                    UPDATE cocktail_info SET
                        cocktail_title = %s,
                        cocktail_base = %s,
                        cocktail_glass = %s,
                        cocktail_technique = %s,
                        cocktail_garnish = %s,
                        cocktail_recipe = %s,
                        cocktail_method = %s,
                        cocktail_subject = %s,
                        cocktail_image_url = %s,
                        cocktail_homepage_url = %s
                    WHERE cocktail_id = %s
                """
                cursor.execute(sql, (
                    row['cocktail_title'],
                    row['cocktail_base'],
                    row['cocktail_glass'],
                    row['cocktail_technique'],
                    row['cocktail_garnish'],
                    row['cocktail_recipe'],
                    row['cocktail_method'],
                    row['cocktail_subject'],
                    row['cocktail_image_url'],
                    row['cocktail_homepage_url'],
                    c_id
                ))
                updated_count += 1
            else:
                # INSERT
                # Note: creating a default idx_no if needed, or letting DB handle it if not strict
                # Using a dummy or formatted value for idx_no if required.
                # Assuming 'cocktail_idx_no' allows NULL or we generate something.
                # Let's check from previous DESCRIBE: 'cocktail_idx_no' is VARCHAR(100) YES.
                
                # We'll insert with NULL for idx_no for now to stay safe, 
                # or generate a simple one. The CSV doesn't have it.
                sql = """
                    INSERT INTO cocktail_info (
                        cocktail_id,
                        cocktail_title,
                        cocktail_base,
                        cocktail_glass,
                        cocktail_technique,
                        cocktail_garnish,
                        cocktail_recipe,
                        cocktail_method,
                        cocktail_subject,
                        cocktail_image_url,
                        cocktail_homepage_url,
                        cocktail_idx_no
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)
                """
                cursor.execute(sql, (
                    c_id,
                    row['cocktail_title'],
                    row['cocktail_base'],
                    row['cocktail_glass'],
                    row['cocktail_technique'],
                    row['cocktail_garnish'],
                    row['cocktail_recipe'],
                    row['cocktail_method'],
                    row['cocktail_subject'],
                    row['cocktail_image_url'],
                    row['cocktail_homepage_url']
                ))
                inserted_count += 1
                
        conn.commit()
        print(f"Import complete: {updated_count} updated, {inserted_count} inserted.")

    except Exception as e:
        print(f"Error during import: {e}")
        conn.rollback()
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    import_data()

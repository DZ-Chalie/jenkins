import os
import pandas as pd
import pymysql
from dotenv import load_dotenv

load_dotenv('backend/backend.env')

def import_prices():
    # Connect to MariaDB
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
        # Read CSV
        print("Reading CSV...")
        df = pd.read_csv('backend/data/shop_drinks_bridge.csv', encoding='utf-8')
        print(f"Loaded {len(df)} rows from CSV.")
        
        with conn.cursor() as cursor:
            # Prepare SQL
            sql = """
                INSERT INTO shop_drinks_bridge (shop_id, drink_id, price)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE price = VALUES(price)
            """
            
            success_count = 0
            fail_count = 0
            
            for index, row in df.iterrows():
                shop_id = row.get('shop_id')
                drink_id = row.get('drink_id')
                price = row.get('menu_price')
                
                if pd.isna(shop_id) or pd.isna(drink_id):
                    continue
                    
                # Clean price
                if isinstance(price, str):
                    try:
                        price = int(price.replace('원', '').replace(',', '').strip())
                    except:
                        price = 0
                elif pd.isna(price):
                    price = 0
                
                try:
                    cursor.execute(sql, (shop_id, drink_id, price))
                    success_count += 1
                except Exception as e:
                    print(f"Error inserting shop_id={shop_id}, drink_id={drink_id}: {e}")
                    fail_count += 1
            
            conn.commit()
            print(f"Import finished. Success: {success_count}, Failed: {fail_count}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import_prices()

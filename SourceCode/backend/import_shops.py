import pandas as pd
from sqlalchemy import create_engine, text
import os
import sys

# Database connection settings
DB_USER = os.getenv("MARIADB_USER", "root")
DB_PASSWORD = os.getenv("MARIADB_PASSWORD", "pass123#")
DB_HOST = os.getenv("MARIADB_HOST", "192.168.0.36")
DB_PORT = os.getenv("MARIADB_PORT", "3306")
DB_NAME = os.getenv("MARIADB_DB", "drink")

# Create SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def import_shops():
    try:
        # 1. Import Shops
        print("Importing shops...")
        shops_df = pd.read_csv('data/menu_shop.csv', encoding='cp949') # Assuming Korean encoding
        
        # Rename columns to match DB schema
        # CSV: shop_id,shop_publication_id,shop_name,shop_address,shop_hours,shop_tel,shop_menu,shop_image_url
        # DB: shop_id, name, address, contact, url, description
        
        shops_df = shops_df.rename(columns={
            'shop_name': 'name',
            'shop_address': 'address',
            'shop_tel': 'contact',
            'shop_image_url': 'url',
            'shop_menu': 'description'
        })
        
        # Select only relevant columns
        shops_df = shops_df[['shop_id', 'name', 'address', 'contact', 'url', 'description']]
        # Assumed DB table: menu_shop
        
        # Create table if not exists
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS menu_shop (
                    shop_id INT PRIMARY KEY,
                    name VARCHAR(255),
                    address VARCHAR(255),
                    contact VARCHAR(50),
                    url VARCHAR(255),
                    description TEXT
                )
            """))
            
            # Truncate table
            conn.execute(text("TRUNCATE TABLE menu_shop"))
            conn.commit()

        shops_df.to_sql('menu_shop', con=engine, if_exists='append', index=False)
        print(f"Imported {len(shops_df)} shops.")

        # 2. Import Shop-Drink Bridge
        print("Importing shop-drink bridge...")
        bridge_df = pd.read_csv('data/shop_drinks_bridge.csv', encoding='cp949')
        
        # Assumed CSV headers: shop_id, drink_id, price
        # Assumed DB table: shop_drinks_bridge
        
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS shop_drinks_bridge (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    shop_id INT,
                    drink_id INT,
                    price INT,
                    FOREIGN KEY (shop_id) REFERENCES menu_shop(shop_id),
                    FOREIGN KEY (drink_id) REFERENCES drink_info(drink_id)
                )
            """))
            
            # Truncate table
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            conn.execute(text("TRUNCATE TABLE shop_drinks_bridge"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            conn.commit()

        bridge_df.to_sql('shop_drinks_bridge', con=engine, if_exists='append', index=False)
        print(f"Imported {len(bridge_df)} bridge records.")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import_shops()

from sqlalchemy import create_engine, text
import os

# Database connection settings
DB_USER = os.getenv("MARIADB_USER", "root")
DB_PASSWORD = os.getenv("MARIADB_PASSWORD", "pass123#")
DB_HOST = os.getenv("MARIADB_HOST", "192.168.0.36")
DB_PORT = os.getenv("MARIADB_PORT", "3306")
DB_NAME = os.getenv("MARIADB_DB", "drink")

# Create SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def verify_data():
    try:
        with engine.connect() as conn:
            menu_shop_count = conn.execute(text("SELECT COUNT(1) FROM menu_shop")).scalar()
            bridge_count = conn.execute(text("SELECT COUNT(1) FROM shop_drinks_bridge")).scalar()
            
            print(f"✅ MenuShop Count: {menu_shop_count}")
            print(f"✅ ShopDrinksBridge Count: {bridge_count}")
            
    except Exception as e:
        print(f"❌ Verification Failed: {e}")

if __name__ == "__main__":
    verify_data()

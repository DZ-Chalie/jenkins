import os
import pymysql
import csv
from dotenv import load_dotenv

# Load env vars
load_dotenv("backend.env")

def get_mariadb_conn():
    try:
        conn = pymysql.connect(
            host=os.getenv("MARIADB_HOST", "192.168.0.36"),
            port=int(os.getenv("MARIADB_PORT", 3306)),
            user=os.getenv("MARIADB_USER", "root"),
            password=os.getenv("MARIADB_PASSWORD", "pass123#"),
            database=os.getenv("MARIADB_DB", "drink"),
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4'
        )
        return conn
    except Exception as e:
        print(f"❌ MariaDB Connection Error: {e}")
        return None

def check_relationships_and_export():
    conn = get_mariadb_conn()
    if not conn:
        return

    try:
        with conn.cursor() as cursor:
            # 1. Check Foreign Keys
            print("\n🔍 Checking Foreign Keys...")
            tables = ['drink_info', 'drink_region', 'region']
            for table in tables:
                print(f"\nTable: {table}")
                # Get Create Table statement
                cursor.execute(f"SHOW CREATE TABLE {table}")
                result = cursor.fetchone()
                create_stmt = result['Create Table']
                
                # Parse for CONSTRAINT
                lines = create_stmt.split('\n')
                fks = [line.strip() for line in lines if 'CONSTRAINT' in line]
                if fks:
                    for fk in fks:
                        print(f"  - {fk}")
                else:
                    print("  - No Foreign Keys found.")

            # 2. Export Data to CSV
            print("\n📦 Exporting Data to CSV...")
            
            # Export region
            cursor.execute("SELECT * FROM region")
            regions = cursor.fetchall()
            if regions:
                with open('data/region_export.csv', 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=regions[0].keys())
                    writer.writeheader()
                    writer.writerows(regions)
                print(f"✅ Exported {len(regions)} rows to data/region_export.csv")
            
            # Export drink_region
            cursor.execute("SELECT * FROM drink_region")
            drink_regions = cursor.fetchall()
            if drink_regions:
                with open('data/drink_region_export.csv', 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=drink_regions[0].keys())
                    writer.writeheader()
                    writer.writerows(drink_regions)
                print(f"✅ Exported {len(drink_regions)} rows to data/drink_region_export.csv")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Ensure data dir exists
    os.makedirs('data', exist_ok=True)
    check_relationships_and_export()

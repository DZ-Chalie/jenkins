
import os
import pymysql
import pandas as pd

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

def check_consistency():
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
            charset='utf8mb4'
        )
        
        # Load DB data
        print("Fetching data from DB table 'cocktail_info'...")
        db_df = pd.read_sql("SELECT * FROM cocktail_info", conn)
        
        # Load CSV data
        csv_path = 'data/cocktail_info.csv'
        print(f"Reading CSV from {csv_path}...")
        csv_df = pd.read_csv(csv_path)

        # Identify common columns
        common_cols = list(set(db_df.columns) & set(csv_df.columns))
        print(f"Common columns: {common_cols}")
        
        if 'cocktail_id' in common_cols:
            db_common = db_df[common_cols].sort_values('cocktail_id').reset_index(drop=True)
            csv_common = csv_df[common_cols].sort_values('cocktail_id').reset_index(drop=True)
            
            # Align types (DB might be int, CSV might be int64)
            db_common = db_common.astype(str)
            csv_common = csv_common.astype(str)
            
            # Normalize potential None/NaN strings
            db_common = db_common.replace({'None': 'nan', '<NA>': 'nan'})
            csv_common = csv_common.replace({'None': 'nan', '<NA>': 'nan'})

            diff = db_common.compare(csv_common)
            if diff.empty:
                print(f"SUCCESS: Data content is IDENTICAL for relevant columns.")
            else:
                print("MISMATCH in common columns:")
                print(diff.head())
        else:
            print("No common ID column found.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_consistency()

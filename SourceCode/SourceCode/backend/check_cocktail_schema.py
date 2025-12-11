
import os
import pymysql

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

def check_schema():
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
        with conn.cursor() as cursor:
            print("--- Table Schema for cocktail_info ---")
            cursor.execute("DESCRIBE cocktail_info")
            for row in cursor.fetchall():
                print(row)
            
            print("\n--- Foreign Keys for cocktail_info ---")
            cursor.execute("""
                SELECT 
                    TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                FROM
                    INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE
                    REFERENCED_TABLE_SCHEMA = %s AND
                    TABLE_NAME = 'cocktail_info';
            """, (db_name,))
            for row in cursor.fetchall():
                print(row)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    check_schema()


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

def check_raw_db():
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
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4'
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM cocktail_info LIMIT 5")
            rows = cursor.fetchall()
            print("First 5 rows in DB:")
            for r in rows:
                print(r)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    check_raw_db()

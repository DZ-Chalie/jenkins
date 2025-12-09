import os
import pymysql
import sys

# Load env vars manually if not loaded (Docker should have them)
# But we print them to be sure
print("--- Environment Variables ---")
print(f"MARIADB_HOST: {os.getenv('MARIADB_HOST')}")
print(f"MARIADB_PORT: {os.getenv('MARIADB_PORT')}")
print(f"MARIADB_USER: {os.getenv('MARIADB_USER')}")
print(f"MARIADB_DB: {os.getenv('MARIADB_DB')}")
print("-----------------------------")

try:
    conn = pymysql.connect(
        host=os.getenv("MARIADB_HOST"),
        port=int(os.getenv("MARIADB_PORT", 3306)),
        user=os.getenv("MARIADB_USER"),
        password=os.getenv("MARIADB_PASSWORD"),
        database="drink", # Explicitly check 'drink' database
        charset='utf8mb4'
    )
    print("✅ Connection Successful to 'drink' database!")
    
    with conn.cursor() as cursor:
        # Check drink 424
        cursor.execute("SELECT drink_id, drink_name FROM drink_info WHERE drink_id = 424")
        drink = cursor.fetchone()
        print(f"🍺 Drink 424: {drink}")
        
        if drink:
            # Check linked cocktails
            cursor.execute(f"SELECT * FROM cocktail_base_bridge WHERE drink_id = 424")
            links = cursor.fetchall()
            print(f"🔗 Linked Cocktails: {links}")
            
            if links:
                ids = [str(l['cocktail_id']) for l in links]
                cursor.execute(f"SELECT * FROM cocktail_info WHERE cocktail_id IN ({','.join(ids)})")
                cocktails = cursor.fetchall()
                print(f"🍹 Cocktails Details: {cocktails}")
            
    conn.close()
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    sys.exit(1)

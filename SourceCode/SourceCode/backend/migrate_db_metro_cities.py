import sys
import os
import pymysql

sys.path.append(os.path.join(os.getcwd(), "backend"))
from app.db.mariadb import get_mariadb_conn

def migrate_db_data():
    # Set Env Vars explicitly for the script context
    os.environ["MARIADB_HOST"] = "192.168.0.36"
    os.environ["MARIADB_PORT"] = "3306"
    os.environ["MARIADB_USER"] = "root"
    os.environ["MARIADB_PASSWORD"] = "pass123#"
    os.environ["MARIADB_DB"] = "drink"

    conn = get_mariadb_conn()
    if not conn:
        print("❌ Failed to connect to MariaDB")
        return

    # Mappings: { "CurrentProvince": { "CityName": "NewProvince" } }
    updates = {
        "경상남도": {
            "동래구": "부산광역시",
            "금정구": "부산광역시",
            "해운대구": "부산광역시",
            "영도구": "부산광역시",
            "기장군": "부산광역시",
            "울주군": "울산광역시" 
        },
        "경상북도": {
            "달성군": "대구광역시",
            "달서구": "대구광역시"
        },
        "경기도": {
            # Seoul mappings
            "은평구": "서울특별시",
            "서초구": "서울특별시",
            "성동구": "서울특별시",
            "마포구": "서울특별시",
            "강남구": "서울특별시",
            "종로구": "서울특별시",
            "강북구": "서울특별시",
            "관악구": "서울특별시",
            "성북구": "서울특별시",
            "영등포구": "서울특별시",
            "서대문구": "서울특별시",
            "강서구": "서울특별시", 
            # Incheon mappings
            "남동구": "인천광역시",
            "부평구": "인천광역시",
            "강화군": "인천광역시"
        },
        "충청남도": {
            "유성구": "대전광역시"
        }
    }

    try:
        with conn.cursor() as cursor:
            total_updated = 0
            for current_prov, city_map in updates.items():
                for city, new_prov in city_map.items():
                    print(f"🔄 Migrating {current_prov} > {city}  --->  {new_prov}")
                    
                    sql = """
                        UPDATE region 
                        SET province = %s 
                        WHERE province = %s AND city = %s
                    """
                    cursor.execute(sql, (new_prov, current_prov, city))
                    updated = cursor.rowcount
                    
                    if updated > 0:
                        print(f"   ✅ Updated {updated} rows.")
                        total_updated += updated
                    else:
                        print(f"   ⚠️ No rows matched (already updated?).")
            
            conn.commit()
            print(f"\n🎉 DB Migration Complete. Total rows updated: {total_updated}")

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db_data()

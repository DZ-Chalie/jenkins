import sys
import os

sys.path.append(os.path.join(os.getcwd(), "backend"))
from app.utils.es_client import get_es_client

def migrate_data():
    es = get_es_client()
    if not es:
        print("❌ ES unavailable")
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
            "강서구": "서울특별시", # Assume Seoul for now unless Incheon/Busan context (but this is Gyeonggi)
            # Incheon mappings
            "남동구": "인천광역시",
            "부평구": "인천광역시",
            "강화군": "인천광역시"
        },
        "충청남도": {
            "유성구": "대전광역시"
        }
    }

    # "중구" is tricky because Seoul, Incheon, Busan, Daegu, Daejeon, Ulsan all have "Jung-gu".
    # Items in "Gyeonggi" labeled "Jung-gu"... likely Incheon or Seoul.
    # Given "Mapo", "Eunpyeong" are here, likely Seoul. But "Namdong" is Incheon.
    # I will skip ambiguous "Jung-gu" for now to avoid errors, or map to Incheon if data suggests.
    
    total_updated = 0
    
    for current_prov, city_map in updates.items():
        for city, new_prov in city_map.items():
            print(f"🔄 Migrating {current_prov} > {city}  --->  {new_prov}")
            
            # Update Query
            query = {
                "script": {
                    "source": "ctx._source.province = params.new_prov",
                    "lang": "painless",
                    "params": {
                        "new_prov": new_prov
                    }
                },
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"province.keyword": current_prov}},
                            {"term": {"city.keyword": city}}
                        ]
                    }
                }
            }
            
            res = es.update_by_query(index="drink_info", body=query)
            updated = res['updated']
            print(f"   ✅ Updated {updated} items.")
            total_updated += updated

    print(f"\n🎉 Migration Complete. Total items updated: {total_updated}")

if __name__ == "__main__":
    migrate_data()

import os
import pymysql
import sys

# Environment Variables
MARIADB_HOST = os.getenv("MARIADB_HOST", "192.168.0.36")
MARIADB_PORT = int(os.getenv("MARIADB_PORT", 3306))
MARIADB_USER = os.getenv("MARIADB_USER", "root")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD", "pass123#")
MARIADB_DB = os.getenv("MARIADB_DB", "drink")

def get_mariadb_conn():
    try:
        conn = pymysql.connect(
            host=MARIADB_HOST,
            port=MARIADB_PORT,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
            database=MARIADB_DB,
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4'
        )
        print("✅ MariaDB Connection Successful")
        return conn
    except Exception as e:
        print(f"❌ MariaDB Connection Failed: {e}")
        sys.exit(1)

def map_city_to_province(city_address):
    if not city_address:
        return "기타"
    
    # Simple mapping based on start of string
    mapping = {
        "경기": "경기도",
        "강원": "강원도",
        "충북": "충청북도", "충청북": "충청북도",
        "충남": "충청남도", "충청남": "충청남도",
        "전북": "전라북도", "전라북": "전라북도",
        "전남": "전라남도", "전라남": "전라남도",
        "경북": "경상북도", "경상북": "경상북도",
        "경남": "경상남도", "경상남": "경상남도",
        "제주": "제주도",
        "서울": "경기도", 
        "인천": "경기도",
        "대전": "충청남도",
        "대구": "경상북도",
        "광주": "전라남도",
        "부산": "경상남도",
        "울산": "경상남도",
        "세종": "충청남도"
    }
    
    for key, val in mapping.items():
        if city_address.startswith(key):
            return val
            
    return "기타"

def extract_province_and_city(address):
    if not address:
        return "기타", "기타"
    
    parts = address.split()
    
    province = "기타"
    city = "기타"

    # Case 1: Full Address "Province City ..."
    if len(parts) >= 2:
        raw_prov = parts[0]
        raw_city = parts[1]
        
        # Try to map first part to province
        province = map_city_to_province(raw_prov)
        
        if province != "기타":
            city = raw_city.replace(",", "").strip()
            return province, city
            
    # Case 2: City only "City" or "Province City" where 1st part didn't match
    # Try to find the city name in the address and map back to province
    # We need the reverse map from the `map_city_to_province` function logic
    
    # Let's define the city map here for reverse lookup
    city_map = {
        "경기도": [
            "수원", "성남", "의정부", "안양", "부천", "광명", "평택", "동두천", "안산", "고양", "과천", "구리", "남양주", "오산", "시흥", "군포", "의왕", "하남", "용인", "파주", "이천", "안성", "김포", "화성", "광주", "양주", "포천", "여주", "연천", "가평", "양평",
            "종로", "중구", "용산", "성동", "광진", "동대문", "중랑", "성북", "강북", "도봉", "노원", "은평", "서대문", "마포", "양천", "강서", "구로", "금천", "영등포", "동작", "관악", "서초", "강남", "송파", "강동",
            "미추홀", "연수", "남동", "부평", "계양", "강화", "옹진", "수지"
        ],
        "강원도": ["춘천", "원주", "강릉", "동해", "태백", "속초", "삼척", "홍천", "횡성", "영월", "평창", "정선", "철원", "화천", "양구", "인제", "고성", "양양"],
        "충청북도": ["청주", "충주", "제천", "보은", "옥천", "영동", "증평", "진천", "괴산", "음성", "단양"],
        "충청남도": [
            "천안", "공주", "보령", "아산", "서산", "논산", "계룡", "당진", "금산", "부여", "서천", "청양", "홍성", "예산", "태안",
            "유성", "대덕", "세종", "조치원"
        ],
        "전라북도": ["전주", "군산", "익산", "정읍", "남원", "김제", "완주", "진안", "무주", "장수", "임실", "순창", "고창", "부안"],
        "전라남도": [
            "목포", "여수", "순천", "나주", "광양", "담양", "곡성", "구례", "고흥", "보성", "화순", "장흥", "강진", "해남", "영암", "무안", "함평", "영광", "장성", "완도", "진도", "신안",
            "광산"
        ],
        "경상북도": [
            "포항", "경주", "김천", "안동", "구미", "영주", "영천", "상주", "문경", "경산", "군위", "의성", "청송", "영양", "영덕", "청도", "고령", "성주", "칠곡", "예천", "봉화", "울진", "울릉",
            "수성", "달서", "달성"
        ],
        "경상남도": [
            "창원", "진주", "통영", "사천", "김해", "밀양", "거제", "양산", "의령", "함안", "창녕", "고성", "남해", "하동", "산청", "함양", "거창", "합천",
            "영도", "부산진", "동래", "해운대", "사하", "금정", "연제", "수영", "사상", "기장", "울주"
        ],
        "제주도": ["제주", "서귀포", "한림"]
    }

    # Search for city name in the address
    for prov, cities in city_map.items():
        for c in cities:
            if c in address:
                return prov, address # Use the full address as city if it's short, or extract?
                # Ideally we want the city name like "평창군".
                # If address is "평창군", return "강원도", "평창군"
                # If address is "강원도 평창군", return "강원도", "평창군"
                
                # Let's try to extract the full city word (e.g. "평창군")
                for part in parts:
                    if c in part:
                        return prov, part
    
    # Fallback: Try map_city_to_province again for just province
    province = map_city_to_province(address)
    
    return province, city

def migrate():
    conn = get_mariadb_conn()
    cursor = conn.cursor()

    try:
        # 1. Create Tables (Normalized)
        print("🛠️ Creating normalized tables...")
        
        # Drop old tables if exist (be careful in prod, but fine for dev)
        cursor.execute("DROP TABLE IF EXISTS drink_region") # Drop bridge/old table first
        cursor.execute("DROP TABLE IF EXISTS region")
        
        # Region Table (Dictionary of regions)
        sql_create_region = """
        CREATE TABLE region (
            id INT AUTO_INCREMENT PRIMARY KEY,
            province VARCHAR(50) NOT NULL,
            city VARCHAR(50) NOT NULL,
            UNIQUE KEY unique_region (province, city)
        );
        """
        cursor.execute(sql_create_region)
        
        # Bridge Table
        sql_create_bridge = """
        CREATE TABLE drink_region (
            drink_id INT,
            region_id INT,
            city_address VARCHAR(255), -- Keep original address for reference
            PRIMARY KEY (drink_id, region_id),
            FOREIGN KEY (drink_id) REFERENCES drink_info(drink_id),
            FOREIGN KEY (region_id) REFERENCES region(id)
        );
        """
        cursor.execute(sql_create_bridge)
        conn.commit()

        # 2. Fetch Data
        print("📥 Fetching drink info...")
        cursor.execute("SELECT drink_id, drink_city FROM drink_info")
        drinks = cursor.fetchall()

        # 3. Process Data
        print("🔄 Processing data...")
        
        # First pass: Collect unique regions
        unique_regions = set()
        drink_mappings = [] # (drink_id, province, city, original_address)
        
        for drink in drinks:
            d_id = drink['drink_id']
            address = drink.get('drink_city') or ""
            province, city = extract_province_and_city(address)
            
            unique_regions.add((province, city))
            drink_mappings.append((d_id, province, city, address))
            
        # 4. Insert Regions
        print(f"📥 Inserting {len(unique_regions)} unique regions...")
        region_id_map = {} # (province, city) -> id
        
        for prov, city in unique_regions:
            try:
                cursor.execute("INSERT INTO region (province, city) VALUES (%s, %s)", (prov, city))
                region_id_map[(prov, city)] = cursor.lastrowid
            except Exception as e:
                print(f"⚠️ Error inserting region {prov} {city}: {e}")
        
        conn.commit()
        
        # 5. Insert Bridge Data
        print(f"🔗 Linking {len(drink_mappings)} drinks to regions...")
        for d_id, prov, city, addr in drink_mappings:
            r_id = region_id_map.get((prov, city))
            if r_id:
                try:
                    cursor.execute(
                        "INSERT INTO drink_region (drink_id, region_id, city_address) VALUES (%s, %s, %s)",
                        (d_id, r_id, addr)
                    )
                except Exception as e:
                    print(f"⚠️ Error linking drink {d_id}: {e}")
                    
        conn.commit()
        print("✅ Migration to normalized schema complete.")

    except Exception as e:
        print(f"❌ Migration Failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

import os
import pymysql
import json
import asyncio
from pymongo import MongoClient
from app.utils.es_client import get_es_client
from dotenv import load_dotenv

# Load env
env_path = os.path.join(os.path.dirname(__file__), "backend.env")
load_dotenv(env_path)
print(f"📋 Loading .env from: {env_path}")

# Elasticsearch Index Name
INDEX_NAME = "liquor_integrated"

# Path to Encyclopedia Data
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "../../data/비정형/전통주 지식백과.json")

def parse_encyclopedia_price(price_str):
    """
    Parse encyclopedia price string to integer.
    Input examples:
      - "￦15,000 (가격은 판매처 별로 상이할 수 있습니다.)"
      - "200ml ￦22,000, 500ml ￦49,000 (가격은...)"
    Output: First price found (15000, 22000)
    """
    if not price_str:
        return 0
    
    try:
        import re
        # Find all prices after ￦ symbol (format: ￦숫자,숫자)
        # This pattern matches ￦ followed by numbers with optional commas
        price_pattern = r'￦\s*([\d,]+)'
        matches = re.findall(price_pattern, price_str)
        
        if matches:
            # Take the first price found
            first_price = matches[0]
            # Remove commas and convert to int
            price_int = int(first_price.replace(',', ''))
            return price_int
        
        # Fallback: if no ￦ found, try extracting any number (old logic)
        numbers = re.sub(r'[^\d]', '', price_str)
        return int(numbers) if numbers else 0
    except:
        return 0


def get_mariadb_conn():
    return pymysql.connect(
        host=os.getenv("MARIADB_HOST", "192.168.0.36"),
        port=int(os.getenv("MARIADB_PORT", 3306)),
        user=os.getenv("MARIADB_USER", "root"),
        password=os.getenv("MARIADB_PASSWORD", "pass123#"),
        database=os.getenv("MARIADB_DB", "drink"),
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4'
    )

def connect_mongo():
    try:
        mongo_host = os.getenv("MONGODB_HOST", "192.168.0.36")
        mongo_port = os.getenv("MONGODB_PORT", "27017")
        mongo_user = os.getenv("MONGODB_USER", "root")
        mongo_pass = os.getenv("MONGODB_PASSWORD", "pass123#")
        if mongo_user and mongo_pass:
            mongo_url = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}"
        else:
            mongo_url = f"mongodb://{mongo_host}:{mongo_port}"
        client = MongoClient(mongo_url)
        return client["liquor"] # Return DB object to access multiple collections
    except Exception as e:
        return client["liquor"] # Return DB object to access multiple collections
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {e}")
        return None

def load_encyclopedia():
    """Load encyclopedia data into a dict keyed by normalized name"""
    print("📚 Loading Encyclopedia data...")
    data_map = {}
    if os.path.exists(DATA_FILE_PATH):
        try:
            with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
                items = json.load(f)
                for item in items:
                    # Normalize name: remove spaces
                    norm_name = item.get('name', '').replace(' ', '')
                    data_map[norm_name] = item
            print(f"✅ Loaded {len(data_map)} encyclopedia entries.")
        except Exception as e:
            print(f"⚠️ Failed to load encyclopedia: {e}")
    else:
        print(f"⚠️ Encyclopedia file not found at {DATA_FILE_PATH}")
    return data_map

def setup_index(es):
    """Create or Update Index Mapping"""
    if es.indices.exists(index=INDEX_NAME):
        print(f"Index {INDEX_NAME} exists. Deleting to re-create (for clean schema)...")
        es.indices.delete(index=INDEX_NAME)

    settings = {
        "analysis": {
            "tokenizer": {
                "nori_user_tokenizer": {
                    "type": "nori_tokenizer",
                    "decompound_mode": "mixed"
                }
            },
            "filter": {
                "icu_normalizer_filter": {
                    "type": "icu_normalizer",
                    "name": "nfc"
                },
                "icu_folding_filter": {
                    "type": "icu_folding"
                },
                "icu_transform_hangul_latin": {
                    "type": "icu_transform",
                    "id": "Hangul-Latin; NFD; [:Nonspacing Mark:] Remove; NFC"
                },
                "phonetic_filter": {
                    "type": "phonetic",
                    "encoder": "metaphone",
                    "replace": False
                }
            },
            "analyzer": {
                "nori_analyzer": {
                    "type": "custom",
                    "tokenizer": "nori_user_tokenizer",
                    "filter": ["lowercase", "trim", "icu_normalizer_filter"]
                },
                "nori_phonetic_analyzer": {
                    "type": "custom",
                    "tokenizer": "nori_user_tokenizer",
                    "filter": ["lowercase", "trim", "icu_normalizer_filter", "phonetic_filter"]
                },
                "romanized_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "icu_transform_hangul_latin", "asciifolding"]
                }
            }
        }
    }
    
    mapping = {
        "properties": {
            "drink_id": {"type": "integer"},
            "name": {
                "type": "text", 
                "analyzer": "nori_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"},
                    "romanized": {
                        "type": "text",
                        "analyzer": "romanized_analyzer"
                    },
                    "phonetic": {
                        "type": "text",
                        "analyzer": "nori_phonetic_analyzer"
                    }
                }
            },
            "type": {"type": "keyword"},
            "alcohol": {"type": "float"}, 
            "volume": {"type": "text"},
            "intro": {"type": "text", "analyzer": "nori_analyzer"},
            "description": {"type": "text", "analyzer": "nori_analyzer"}, 
            "image_url": {"type": "keyword"},
            "awards": {"type": "text", "analyzer": "nori_analyzer", "fields": {"keyword": {"type": "keyword"}}},
            "season": {"type": "keyword"}, # Added Season Field
            "price_source": {"type": "keyword"}, # NEW: lowest_price | encyclopedia | null
            "price_is_reference": {"type": "boolean"}, # NEW: true if from encyclopedia
            "encyclopedia_price_text": {"type": "text"}, # NEW: Original price text (e.g., "200ml ₩22,000, 500ml ₩49,000")
            "encyclopedia_url": {"type": "keyword"}, # NEW: Link to encyclopedia source
            "cocktails": {
                "type": "nested",
                "properties": {
                    "name": {"type": "text"},
                    "recipe": {"type": "text"}
                }
            },
            "foods": {"type": "text", "analyzer": "nori_analyzer"},
            "ingredients": {"type": "text", "analyzer": "nori_analyzer"}, 
            "lowest_price": {"type": "long"},
            "selling_shops": {
                "type": "nested",
                "properties": {
                    "name": {"type": "text"},
                    "price": {"type": "long"},
                    "url": {"type": "keyword"}
                }
            },
            "region": {
                "properties": {
                    "province": {"type": "keyword"},
                    "city": {"type": "keyword"}
                }
            },
            "brewery": {
                "properties": {
                    "name": {"type": "text", "analyzer": "nori_analyzer"},
                    "address": {"type": "text"},
                    "contact": {"type": "keyword"},
                    "homepage": {"type": "keyword"}
                }
            }
        }
    }
    
    es.indices.create(index=INDEX_NAME, body={"settings": settings, "mappings": mapping})
    print(f"✅ Created index: {INDEX_NAME}")

def run_etl():
    print("🚀 Starting Unified ETL...")
    
    # 1. Connect
    mariadb = get_mariadb_conn()
    mongo_db = connect_mongo() # Now returns DB object
    es = get_es_client()
    encyclopedia = load_encyclopedia()
    
    if not mariadb or not es:
        print("❌ DB/ES Connection Failed")
        return

    # 2. Setup Index
    setup_index(es)

    # Pre-fetch MongoDB Data
    mongo_products_col = mongo_db["products"] if mongo_db is not None else None
    mongo_seasons_col = mongo_db["seasons"] if mongo_db is not None else None 
    
    season_map = {}
    if mongo_seasons_col is not None:
        print("📦 Fetching Season data...")
        try:
            for doc in mongo_seasons_col.find():
                d_name = doc.get("name")
                d_season = doc.get("season")
                if d_name and d_season:
                    season_map[d_name.strip()] = d_season
            print(f"✅ Loaded {len(season_map)} season entries.")
        except Exception as e:
            print(f"⚠️ Failed to fetch seasons: {e}")

    # 3. Fetch Base Data (MariaDB)
    with mariadb.cursor() as cursor:
        print("📦 Fetching base drinks...")
        # Join with Type and Region
        sql = """
            SELECT 
                d.drink_id, d.drink_name, d.drink_image_url, d.drink_intro, 
                d.drink_abv, d.drink_volume, d.drink_city, 
                t.type_name,
                r.province, r.city as region_city,
                b.brewery_name, b.brewery_address, b.brewery_contact, b.brewery_homepage
            FROM drink_info d
            LEFT JOIN drink_type t ON d.type_id = t.type_id
            LEFT JOIN drink_region dr ON d.drink_id = dr.drink_id
            LEFT JOIN region r ON dr.region_id = r.id
            LEFT JOIN brewery_info b ON d.brewery_id = b.brewery_id
        """
        cursor.execute(sql)
        drinks = cursor.fetchall()
        print(f"Found {len(drinks)} drinks.")

        # Cache Cocktails
        print("📦 Fetching Cocktails...")
        cursor.execute("""
            SELECT b.drink_id, c.cocktail_title, c.cocktail_recipe, c.cocktail_image_url
            FROM cocktail_base_bridge b
            JOIN cocktail_info c ON b.cocktail_id = c.cocktail_id
        """)
        cocktail_map = {}
        for row in cursor.fetchall():
            cocktail_map.setdefault(row['drink_id'], []).append({
                "cocktail_title": row['cocktail_title'],
                "cocktail_recipe": row['cocktail_recipe'],
                "cocktail_image_url": row.get('cocktail_image_url', "")
            })
            
        # Cache Foods
        print("📦 Fetching Foods...")
        cursor.execute("""
            SELECT b.drink_id, f.name as food_name 
            FROM drink_pairing_food_bridge b
            JOIN pairing_food f ON b.food_id = f.id
        """)
        food_map = {}
        for row in cursor.fetchall():
            food_map.setdefault(row['drink_id'], []).append(row['food_name'])
            
        # Cache Shops
        print("📦 Fetching Shops...")
        cursor.execute("""
            SELECT b.drink_id, s.name, b.price, s.url, s.address, s.contact 
            FROM shop_drinks_bridge b
            JOIN menu_shop s ON b.shop_id = s.shop_id
        """)
        shop_map = {}
        for row in cursor.fetchall():
            shop_map.setdefault(row['drink_id'], []).append({
                "shop_id": row.get('shop_id', 0),
                "name": row['name'],
                "price": row['price'],
                "url": row['url'],
                "address": row.get('address', ''),
                "contact": row.get('contact', '')
            })

    # 4. Merge & Index
    actions = []
    
    for drink in drinks:
        d_id = drink['drink_id']
        name = drink['drink_name']
        
        # Parse Alcohol
        try:
            abv = float(str(drink['drink_abv']).replace('%', ''))
        except:
            abv = 0.0

        # Mongo Price - Initialize price tracking
        lprice = 0
        price_source = None
        price_is_reference = False
        
        if mongo_products_col is not None:
            # Try specific match first
            price_doc = mongo_products_col.find_one({"liquor_id": d_id}, sort=[("lprice", 1)])
            if not price_doc:
                price_doc = mongo_products_col.find_one({"drink_name": name}, sort=[("lprice", 1)])
            if price_doc:
                lprice = int(price_doc.get('lprice', 0))
                if lprice > 0:
                    price_source = 'lowest_price'

        # If Mongo has no price, use cheapest from MariaDB shops
        shops = shop_map.get(d_id, [])
        if lprice == 0 and shops:
            min_shop_price = min([s['price'] for s in shops if s['price'] > 0], default=0)
            if min_shop_price > 0:
                lprice = min_shop_price
                price_source = 'lowest_price'
            
        # Encyclopedia Data
        norm_name = name.replace(' ', '').strip()
        enc_data = encyclopedia.get(norm_name, {})
        
        # Helper to safely get nested dict/list
        naver_data = enc_data.get('naver', {})
        
        # 1. Description (Fallback for Intro)
        description = ""
        sections = naver_data.get('sections', [])
        if sections and isinstance(sections, list) and len(sections) > 0:
            description = sections[0].get('text', '')

        # 2. Ingredients
        ingredients = naver_data.get('raw_info_table', {}).get('원재료', '')
        
        # NEW: 2.5 Encyclopedia Price Fallback (last resort)
        encyclopedia_price_text = None
        encyclopedia_url = None
        
        if lprice == 0:
            price_str = naver_data.get('raw_info_table', {}).get('가격', '')
            encyclopedia_price = parse_encyclopedia_price(price_str)
            if encyclopedia_price > 0:
                lprice = encyclopedia_price
                price_source = 'encyclopedia'
                price_is_reference = True
                # Store original price text and URL
                encyclopedia_price_text = price_str
                encyclopedia_url = naver_data.get('source_url', '')
        
        # 3. Full Encyclopedia Structure for Frontend
        encyclopedia_list = sections

        # Region Logic
        prov = drink['province']
        city = drink['region_city']
        if not city and drink['drink_city']:
             city = drink['drink_city']
             if not prov and ' ' in city:
                 prov = city.split(' ')[0]

        # Awards processing
        awards_list = []
        raw_awards = drink.get('drink_awards', '')
        if raw_awards:
            awards_list = [a.strip() for a in str(raw_awards).replace(';', '\n').split('\n') if a.strip()]

        # Season Mapping
        # Try exact match, then trimmed match
        s_val = season_map.get(name.strip(), None)
        
        if not s_val:
            # Optional: fuzzy match or try removing spaces?
            s_val = season_map.get(name.replace(" ", ""), None)
            
        # Brewery Data
        brewery_data = None
        if drink.get('brewery_name'):
            brewery_data = {
                "name": drink.get('brewery_name', ''),
                "address": drink.get('brewery_address', ''),
                "contact": drink.get('brewery_contact', ''),
                "homepage": drink.get('brewery_homepage', '')
            }
        
        doc = {
            "drink_id": d_id,
            "name": name,
            "type": drink['type_name'] or "기타",
            "alcohol": abv,
            "volume": drink['drink_volume'],
            "intro": drink['drink_intro'],
            "description": description,
            "image_url": drink['drink_image_url'],
            "awards": awards_list,
            "season": s_val, # Populated Field
            "cocktails": cocktail_map.get(d_id, []),
            "foods": food_map.get(d_id, []),
            "ingredients": ingredients,
            "lowest_price": lprice,
            "price_source": price_source,  # NEW
            "price_is_reference": price_is_reference,  # NEW
            "encyclopedia_price_text": encyclopedia_price_text,  # NEW: Original price text
            "encyclopedia_url": encyclopedia_url,  # NEW: Encyclopedia source link
            "selling_shops": shops,
            "encyclopedia": encyclopedia_list, 
            "region": {
                "province": prov,
                "city": city
            },
            "brewery": brewery_data  # NEW: Brewery information
        }
        
        action = {
            "index": { "_index": INDEX_NAME, "_id": str(d_id) }
        }
        actions.append(json.dumps(action))
        actions.append(json.dumps(doc))
        
        if len(actions) >= 200: # Bulk size 100 docs
            es.bulk(body="\n".join(actions))
            actions = []
            
    if actions:
        es.bulk(body="\n".join(actions))
        
    print("✅ ETL Complete!")

if __name__ == "__main__":
    run_etl()

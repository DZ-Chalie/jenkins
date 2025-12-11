import sys
import os

# Add backend directory to path so we can import app modules
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Set environment variables for connections
os.environ["ELASTICSEARCH_URL"] = "http://192.168.0.36:9200"
os.environ["ELASTICSEARCH_USERNAME"] = "elastic"
os.environ["ELASTICSEARCH_PASSWORD"] = "pass123"
os.environ["MARIADB_HOST"] = "192.168.0.182"
os.environ["MARIADB_PORT"] = "3306"
os.environ["MARIADB_USER"] = "user"
os.environ["MARIADB_PASSWORD"] = "pass123#"
os.environ["MARIADB_DB"] = "db"

try:
    from app.api.search import search_liquor_fuzzy
    
    # Test case: Search for a known liquor
    query_text = "소백산 막걸리" # Should match "소백산 생 막걸리"
    print(f"🔎 Testing search for: '{query_text}'")
    
    result = search_liquor_fuzzy(query_text)
    
    if result:
        print("\n✅ Search Successful!")
        print(f"   - Name: {result.get('drink_name')}")
        print(f"   - Score: {result.get('es_score')}")
        print(f"   - Source: {result.get('source', 'MariaDB + ES')}")
        print(f"   - Details: {result}")
    else:
        print("\n❌ Search returned None.")

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you are running this from the 'source' directory.")
except Exception as e:
    print(f"❌ Error: {e}")

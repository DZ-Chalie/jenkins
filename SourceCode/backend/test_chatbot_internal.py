import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend.env')

from app.api.chatbot import search_liquor_for_rag, invoke_nova

def test_es_search():
    print("\n🔍 Testing Elasticsearch Search (Internal)...")
    query = "여름에 먹기 좋은 술"
    results = search_liquor_for_rag(query)
    
    if results:
        print(f"✅ Found {len(results)} drinks for query '{query}'")
        for d in results:
            print(f" - {d['name']} ({d['abv']}%)")
    else:
        print("❌ No results found. Check ES connection or data.")

if __name__ == "__main__":
    test_es_search()

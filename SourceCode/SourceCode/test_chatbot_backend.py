import sys
import os
import asyncio
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Load environment variables
load_dotenv('backend/backend.env')

from app.api.chatbot import search_liquor_for_rag, invoke_nova

def test_es_search():
    print("\n🔍 Testing Elasticsearch Search...")
    query = "여름에 먹기 좋은 술"
    results = search_liquor_for_rag(query)
    
    if results:
        print(f"✅ Found {len(results)} drinks for query '{query}'")
        for d in results:
            print(f" - {d['name']} ({d['abv']}%)")
    else:
        print("❌ No results found. Check ES connection or data.")

def test_nova_invocation():
    print("\n🤖 Testing Nova Invocation...")
    system_prompt = "너는 주모다. 짧게 인사해라."
    user_message = "안녕?"
    
    try:
        response = invoke_nova(system_prompt, user_message)
        print(f"✅ Nova Response: {response}")
    except Exception as e:
        print(f"❌ Nova Error: {e}")
        print("Check AWS credentials in backend.env")

if __name__ == "__main__":
    test_es_search()
    # test_nova_invocation() # Uncomment to test real API call (costs money/tokens)

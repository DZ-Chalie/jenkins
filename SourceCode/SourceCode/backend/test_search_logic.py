import sys
import os

# Add /app to sys.path to allow imports from app
sys.path.append('/app')

from app.api.search import search_liquor_fuzzy

def test_search():
    query = "감홍로"
    print(f"🔍 Testing search for: {query}")
    
    result = search_liquor_fuzzy(query)
    
    if result:
        print("✅ Result found:")
        print(f"  - Name: {result.get('name')}")
        print(f"  - Image URL: {result.get('image_url')}")
        print(f"  - Description: {result.get('description')[:50]}...")
        
        detail = result.get('detail', {})
        print(f"  - Detail.Alcohol: {detail.get('알콜도수')}")
        print(f"  - Detail.Volume: {detail.get('용량')}")
        print(f"  - Detail.Type: {detail.get('종류')}")
        print(f"  - Detail.Ingredients: {detail.get('원재료')}")
        
        brewery = result.get('brewery', {})
        print(f"  - Brewery.Address: {brewery.get('address')}")
        
        cocktails = result.get('cocktails')
        print(f"  - Cocktails: {len(cocktails) if cocktails is not None else 'None'}")
        if cocktails:
            print(f"  - First Cocktail: {cocktails[0].get('cocktail_title')}")
        
        if result.get('name') == '감홍로' and cocktails and len(cocktails) > 0:
            print("✅ Data structure mapped correctly and cocktails found.")
        else:
            print(f"❌ Data mismatch. Name: {result.get('name')}, Cocktails: {cocktails}")
    else:
        print("❌ No result found.")

if __name__ == "__main__":
    test_search()

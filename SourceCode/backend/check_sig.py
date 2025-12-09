import json
import sys

def check_sig_names():
    try:
        with open('frontend/public/sig.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print("Checking first 10 city names in sig.json:")
        for feature in data['features'][:10]:
            print(f"- {feature['properties'].get('SIG_KOR_NM')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_sig_names()

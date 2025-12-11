import urllib.request
import json

ES_URL = "http://elasticsearch:9200"

def analyze_text(text, description):
    try:
        url = f"{ES_URL}/liquors/_analyze"
        data = json.dumps({
            "analyzer": "hangul_to_latin",
            "text": text
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            tokens = [t['token'] for t in result['tokens']]
            print(f"[{description}]")
            print(f"Input: {text}")
            print(f"Tokens: {tokens}")
            print("-" * 20)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # 1. How '게이샤' is stored
    analyze_text("게이샤", "1. DB Stored Data (Target)")
    
    # 2. How OCR text is processed
    analyze_text("Geishu JIOLIJI alc.33%", "2. OCR Input (Query)")

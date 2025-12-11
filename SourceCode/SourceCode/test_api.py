import requests
import json

response = requests.get('http://localhost:8000/search/detail/347')
data = response.json()

print("=== API Response Check ===")
print(f"Status Code: {response.status_code}")
print(f"\nName: {data.get('name')}")
print(f"price_is_reference: {data.get('price_is_reference')}")
print(f"encyclopedia_price_text: {data.get('encyclopedia_price_text')}")
print(f"encyclopedia_url: {data.get('encyclopedia_url')}")
print(f"selling_shops count: {len(data.get('selling_shops', []))}")

# Pretty print full response
print("\n=== Full Response (formatted) ===")
print(json.dumps({
    'price_is_reference': data.get('price_is_reference'),
    'encyclopedia_price_text': data.get('encyclopedia_price_text'),
    'encyclopedia_url': data.get('encyclopedia_url'),
    'selling_shops': data.get('selling_shops')
}, ensure_ascii=False, indent=2))

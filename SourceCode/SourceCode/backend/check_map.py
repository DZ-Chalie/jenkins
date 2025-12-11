import json
import sys

try:
    with open('d:/final_project/source/frontend/public/province.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    lats = []
    longs = []

    def extract_coords(coords):
        for item in coords:
            if isinstance(item[0], (int, float)):
                longs.append(item[0])
                lats.append(item[1])
            else:
                extract_coords(item)

    for feature in data['features']:
        extract_coords(feature['geometry']['coordinates'])

    if not lats:
        print("No coordinates found")
    else:
        print(f"Min Lat: {min(lats)}")
        print(f"Max Lat: {max(lats)}")
        print(f"Min Long: {min(longs)}")
        print(f"Max Long: {max(longs)}")

except Exception as e:
    print(f"Error: {e}")

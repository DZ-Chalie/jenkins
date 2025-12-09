import json

def is_ccw(ring):
    return sum((p2[0] - p1[0]) * (p2[1] + p1[1]) for p1, p2 in zip(ring, ring[1:] + [ring[0]])) < 0

try:
    with open('d:/final_project/source/frontend/public/sig.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for feature in data['features']:
        name = feature['properties']['SIG_KOR_NM']
        coords = feature['geometry']['coordinates']
        
        # Handle MultiPolygon
        if feature['geometry']['type'] == 'MultiPolygon':
            first_ring = coords[0][0]
        else:
            first_ring = coords[0]
            
        ccw = is_ccw(first_ring)
        print(f"{name}: {'CCW' if ccw else 'CW'}")

except Exception as e:
    print(f"Error: {e}")

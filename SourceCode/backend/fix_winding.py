import json
import os

def rewind_ring(ring, ensure_ccw=True):
    # Calculate signed area
    area = sum((p2[0] - p1[0]) * (p2[1] + p1[1]) for p1, p2 in zip(ring, ring[1:] + [ring[0]]))
    is_ccw = area < 0
    
    if ensure_ccw != is_ccw:
        return ring[::-1]
    return ring

def rewind_geometry(geometry):
    if geometry['type'] == 'Polygon':
        # Exterior ring (first) should be CCW
        geometry['coordinates'][0] = rewind_ring(geometry['coordinates'][0], True)
        # Interior rings (holes) should be CW (optional, but good practice)
        for i in range(1, len(geometry['coordinates'])):
            geometry['coordinates'][i] = rewind_ring(geometry['coordinates'][i], False)
            
    elif geometry['type'] == 'MultiPolygon':
        for i in range(len(geometry['coordinates'])):
            # Exterior ring
            geometry['coordinates'][i][0] = rewind_ring(geometry['coordinates'][i][0], True)
            # Interior rings
            for j in range(1, len(geometry['coordinates'][i])):
                geometry['coordinates'][i][j] = rewind_ring(geometry['coordinates'][i][j], False)
    return geometry

def fix_file(filepath):
    print(f"Fixing {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for feature in data['features']:
            feature['geometry'] = rewind_geometry(feature['geometry'])
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"Fixed {filepath}")
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")

fix_file('d:/final_project/source/frontend/public/province.json')
fix_file('d:/final_project/source/frontend/public/sig.json')

import json
import os

def rewind_ring(ring, ensure_ccw=True):
    # Calculate signed area
    area = sum((p2[0] - p1[0]) * (p2[1] + p1[1]) for p1, p2 in zip(ring, ring[1:] + [ring[0]]))
    is_ccw = area < 0
    
    if ensure_ccw != is_ccw:
        return ring[::-1]
    return ring

def rewind_geometry(geometry, ensure_ccw=True):
    if geometry['type'] == 'Polygon':
        # Exterior ring (first)
        geometry['coordinates'][0] = rewind_ring(geometry['coordinates'][0], ensure_ccw)
        # Interior rings (holes) should be opposite
        for i in range(1, len(geometry['coordinates'])):
            geometry['coordinates'][i] = rewind_ring(geometry['coordinates'][i], not ensure_ccw)
            
    elif geometry['type'] == 'MultiPolygon':
        for i in range(len(geometry['coordinates'])):
            # Exterior ring
            geometry['coordinates'][i][0] = rewind_ring(geometry['coordinates'][i][0], ensure_ccw)
            # Interior rings
            for j in range(1, len(geometry['coordinates'][i])):
                geometry['coordinates'][i][j] = rewind_ring(geometry['coordinates'][i][j], not ensure_ccw)
    return geometry

def fix_file(filepath, ensure_ccw=True):
    print(f"Fixing {filepath} to {'CCW' if ensure_ccw else 'CW'}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for feature in data['features']:
            feature['geometry'] = rewind_geometry(feature['geometry'], ensure_ccw)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"Fixed {filepath}")
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")

# Force CW (ensure_ccw=False)
fix_file('d:/final_project/source/frontend/public/sig.json', ensure_ccw=False)

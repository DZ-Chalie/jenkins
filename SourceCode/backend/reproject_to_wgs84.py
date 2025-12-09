import json
try:
    from pyproj import Transformer
except ImportError:
    print("Installing pyproj...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'pyproj'])
    from pyproj import Transformer

print("Converting sig.json from UTM-K to WGS84...")

# Create transformer from UTM-K (EPSG:5179 or 5186) to WGS84 (EPSG:4326)
# Try EPSG:5179 first (common for Korean data)
transformer = Transformer.from_crs("EPSG:5179", "EPSG:4326", always_xy=True)

# Read existing GeoJSON
with open('d:/final_project/source/frontend/public/sig.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Converting {len(data['features'])} features...")

# Convert each feature
for i, feature in enumerate(data['features']):
    if i % 50 == 0:
        print(f"  Progress: {i}/{len(data['features'])}")
    
    geom = feature['geometry']
    
    if geom['type'] == 'Polygon':
        new_coords = []
        for ring in geom['coordinates']:
            new_ring = []
            for x, y in ring:
                lon, lat = transformer.transform(x, y)
                new_ring.append([lon, lat])
            new_coords.append(new_ring)
        geom['coordinates'] = new_coords
        
    elif geom['type'] == 'MultiPolygon':
        new_coords = []
        for polygon in geom['coordinates']:
            new_polygon = []
            for ring in polygon:
                new_ring = []
                for x, y in ring:
                    lon, lat = transformer.transform(x, y)
                    new_ring.append([lon, lat])
                new_polygon.append(new_ring)
            new_coords.append(new_polygon)
        geom['coordinates'] = new_coords

print("Writing converted GeoJSON...")
with open('d:/final_project/source/frontend/public/sig.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

# Verify
first_point = data['features'][0]['geometry']['coordinates'][0][0]
print(f"\n✓ Conversion complete!")
print(f"Sample coordinate (should be lon/lat): {first_point}")
print(f"Longitude: {first_point[0]:.6f} (should be ~126-131)")
print(f"Latitude: {first_point[1]:.6f} (should be ~33-39)")

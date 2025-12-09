import json

# Check coordinate range
with open('d:/final_project/source/frontend/public/sig.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Sample first feature coordinates
first_feature = data['features'][0]
first_ring = first_feature['geometry']['coordinates'][0]
first_point = first_ring[0]

print(f"First coordinate point: {first_point}")
print(f"X range sample: {first_point[0]}")
print(f"Y range sample: {first_point[1]}")

# Check if it's in UTM-K range (large numbers) or WGS84 (lat/lon)
if abs(first_point[0]) > 1000:
    print("\n⚠️  PROBLEM: Coordinates are in UTM-K (projected), not WGS84 (lat/lon)")
    print("Need to reproject to WGS84!")
else:
    print("\n✓ Coordinates appear to be in WGS84 (lat/lon)")

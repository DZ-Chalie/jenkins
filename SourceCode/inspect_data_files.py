import os
import json
import glob

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

print(f"Checking data dir: {DATA_DIR}")

# Check '정형' and '비정형'
for subdir in ['정형', '비정형']:
    path = os.path.join(DATA_DIR, subdir)
    if os.path.exists(path):
        print(f"\n--- {subdir} Files Top 5 ---")
        files = glob.glob(os.path.join(path, "**", "*.json"), recursive=True)
        print(f"Total JSON files: {len(files)}")
        for f in files[:5]:
            print(os.path.basename(f))
            
        if files:
            print(f"\n[Sample Content: {os.path.basename(files[0])}]")
            try:
                with open(files[0], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Print first level keys and simplified content
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")
            except Exception as e:
                print(f"Error reading file: {e}")
    else:
        print(f"Subdir {subdir} not found.")

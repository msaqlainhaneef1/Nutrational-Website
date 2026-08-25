import os
import json
import glob

extracted_dir = 'JSON Files'
target_dir = 'src/data/restaurants'

extracted_files = glob.glob(os.path.join(extracted_dir, '*.json'))
existing_files = glob.glob(os.path.join(target_dir, '*.json'))

print(f"Total extracted JSON files: {len(extracted_files)}")
print(f"Total existing restaurant JSON files: {len(existing_files)}")

# Let's inspect a few extracted files to see their structure
sample_types = {}
for fpath in extracted_files:
    fname = os.path.basename(fpath)
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        keys = tuple(sorted(data.keys())) if isinstance(data, dict) else ('LIST',)
        if keys not in sample_types:
            sample_types[keys] = []
        sample_types[keys].append(fname)
    except Exception as e:
        print(f"Error loading {fname}: {e}")

print("\n--- Structural Types Found in Extracted Files ---")
for structure, files in sample_types.items():
    print(f"\nKeys: {structure} (Count: {len(files)})")
    print(f"  Examples: {files[:5]}")

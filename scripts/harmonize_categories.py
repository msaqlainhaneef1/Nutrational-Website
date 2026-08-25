import os
import json
import glob

target_dir = 'src/data/restaurants'
index_file = os.path.join(target_dir, '_index.json')

CAT_MAP = {
    'Chicken': 'Chicken & Wings',
    'Burgers': 'Burgers & Fast Food',
    'Pizza': 'Pizza & Italian',
    'Diners & Breakfast': 'Breakfast & Healthy',
}

with open(index_file, 'r', encoding='utf-8') as f:
    idx_data = json.load(f)

for r in idx_data['restaurants']:
    if r.get('category') in CAT_MAP:
        r['category'] = CAT_MAP[r['category']]

with open(index_file, 'w', encoding='utf-8') as f:
    json.dump(idx_data, f, indent=2)

for fpath in glob.glob(os.path.join(target_dir, '*.json')):
    if fpath.endswith('_index.json'): continue
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if data.get('category') in CAT_MAP:
        data['category'] = CAT_MAP[data['category']]
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

print("Standardized all categories!")

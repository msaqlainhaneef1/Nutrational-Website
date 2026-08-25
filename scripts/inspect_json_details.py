import os
import json
import glob
import re

extracted_dir = 'JSON Files'
target_dir = 'src/data/restaurants'

# Fix dibellas if needed
try:
    with open(os.path.join(extracted_dir, 'dibellas_nutrition.json'), 'r', encoding='utf-8') as f:
        content = f.read()
    # see what line 129 looks like
    lines = content.split('\n')
    print(f"dibellas lines around 129:")
    for i in range(max(0, 125), min(len(lines), 135)):
        print(f"{i+1}: {lines[i]}")
except Exception as e:
    print(f"Dibellas read error: {e}")

# Let's inspect sample products from different formats
print("\n--- Sample Product Keys ---")
for fname in ['54th_street_nutrition.json', 'applebees_nutrition.json', 'checkers_nutrition_final.json', 'crazy_bowls_nutrition.json', 'kfc_nutrition.json']:
    fpath = os.path.join(extracted_dir, fname)
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"\nFile: {fname}")
        if isinstance(data, list):
            print(f"List with {len(data)} items. First item: {data[0] if data else None}")
        elif 'products' in data:
            prods = data['products']
            print(f"Products count: {len(prods)}. First product: {prods[0] if prods else None}")
            if 'categories' in data:
                print(f"Categories: {data.get('categories')}")
            if 'brand' in data:
                print(f"Brand: {data.get('brand')}")
        elif 'menu_items' in data:
            items = data['menu_items']
            print(f"Menu items count: {len(items)}. First item: {items[0] if items else None}")
        elif 'items' in data:
            items = data['items']
            print(f"Items count: {len(items)}. First item: {items[0] if items else None}")
        elif 'restaurants' in data:
            print(f"Restaurants database: {len(data['restaurants'])} restaurants. Names: {[r.get('restaurant_name') or r.get('name') for r in data['restaurants'][:5]]}")

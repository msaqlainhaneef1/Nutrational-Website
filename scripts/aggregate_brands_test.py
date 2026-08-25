import os
import json
import glob
import re

extracted_dir = 'JSON Files'
target_dir = 'src/data/restaurants'

# First fix dibellas JSON if broken
dibellas_path = os.path.join(extracted_dir, 'dibellas_nutrition.json')
if os.path.exists(dibellas_path):
    try:
        with open(dibellas_path, 'r', encoding='utf-8') as f:
            raw = f.read()
        # let's see why it failed
        json.loads(raw)
    except Exception as e:
        print(f"Fixing dibellas: {e}")
        # let's clean trailing garbage or fix
        idx = raw.rfind('}')
        if idx != -1:
            try:
                fixed = raw[:idx+1]
                json.loads(fixed)
                with open(dibellas_path, 'w', encoding='utf-8') as f:
                    f.write(fixed)
                print("dibellas fixed successfully!")
            except Exception as e2:
                print(f"Still failed to fix dibellas: {e2}")

# Let's map existing restaurants
existing_slugs = {}
existing_names = {}
for fpath in glob.glob(os.path.join(target_dir, '*.json')):
    fname = os.path.basename(fpath)
    if fname == '_index.json':
        continue
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        slug = data.get('slug') or fname.replace('.json', '')
        name = data.get('name', slug)
        existing_slugs[slug] = fpath
        existing_names[name.lower().strip()] = slug
    except Exception as e:
        print(f"Error reading existing {fname}: {e}")

print(f"Mapped {len(existing_slugs)} existing restaurants.")

def normalize_slug(name):
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name).strip().lower()
    slug = re.sub(r'[\s_]+', '-', slug)
    if not slug.endswith('-nutrition-calculator') and not slug.endswith('-calories-calculator'):
        slug += '-nutrition-calculator'
    return slug

def parse_item(raw_item):
    if not isinstance(raw_item, dict):
        return None
    name = raw_item.get('name') or raw_item.get('product_name') or raw_item.get('item_name')
    if not name:
        return None
    
    # Nutrition extraction
    nutr = raw_item.get('nutrition') or raw_item
    
    def get_num(keys):
        for k in keys:
            if k in nutr and nutr[k] is not None:
                try:
                    val = str(nutr[k]).replace('g', '').replace('mg', '').replace('kcal', '').replace(',', '').strip()
                    if val.lower() in ('', 'none', 'null', 'n/a', '-'):
                        continue
                    return round(float(val), 1) if '.' in val else int(float(val))
                except:
                    pass
        return 0

    calories = get_num(['calories', 'calories_kcal', 'energy_kcal', 'cal', 'energy'])
    protein = get_num(['protein_g', 'protein', 'proteins'])
    fat = get_num(['fat_g', 'total_fat_g', 'fat', 'total_fat'])
    carbs = get_num(['carbohydrates_g', 'total_carbohydrates_g', 'carbs', 'carbohydrate_g', 'carbohydrates'])
    
    # Optional fields
    fiber = get_num(['fiber_g', 'dietary_fiber_g', 'fiber'])
    sodium = get_num(['sodium_mg', 'sodium'])
    cholesterol = get_num(['cholesterol_mg', 'cholesterol'])
    sat_fat = get_num(['saturated_fat_g', 'saturated_fat'])
    sugars = get_num(['sugars_g', 'sugar_g', 'sugars', 'sugar'])
    
    item = {
        "name": name.strip(),
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs
    }
    if fiber: item["fiber"] = fiber
    if sodium: item["sodium"] = sodium
    if cholesterol: item["cholesterol"] = cholesterol
    if sat_fat: item["saturated_fat"] = sat_fat
    if sugars: item["sugars"] = sugars
    
    return item

# Let's aggregate products from all extracted JSON files
brands = {}

for fpath in glob.glob(os.path.join(extracted_dir, '*.json')):
    fname = os.path.basename(fpath)
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Skipping {fname} due to load error: {e}")
        continue
        
    # Case 1: multi-restaurant DB
    if isinstance(data, dict) and 'restaurants' in data and isinstance(data['restaurants'], list):
        for r in data['restaurants']:
            r_name = r.get('restaurant_name') or r.get('name') or r.get('brand')
            if not r_name: continue
            if r_name not in brands: brands[r_name] = {'categories': {}, 'files': set()}
            brands[r_name]['files'].add(fname)
            items = r.get('items') or r.get('menu_items') or r.get('products') or []
            for item in items:
                cat_name = item.get('category') or 'General Menu'
                parsed = parse_item(item)
                if parsed:
                    if cat_name not in brands[r_name]['categories']:
                        brands[r_name]['categories'][cat_name] = []
                    brands[r_name]['categories'][cat_name].append(parsed)
        continue

    # Identify brand name
    brand_name = None
    if isinstance(data, dict):
        if isinstance(data.get('brand'), dict):
            brand_name = data['brand'].get('name')
        elif isinstance(data.get('brand'), str):
            brand_name = data['brand']
        elif data.get('restaurant_name'):
            brand_name = data['restaurant_name']
        elif data.get('restaurant'):
            brand_name = data['restaurant'] if isinstance(data['restaurant'], str) else data['restaurant'].get('name')
    
    # If still no brand name, deduce from file name
    if not brand_name:
        clean_fn = fname.replace('_nutrition_final.json', '').replace('_nutrition_db.json', '').replace('_nutrition.json', '').replace('_nutrition1.json', '').replace('_database.json', '').replace('.json', '')
        brand_name = clean_fn.replace('_', ' ').title()

    if brand_name not in brands:
        brands[brand_name] = {'categories': {}, 'files': set()}
    brands[brand_name]['files'].add(fname)

    # Extract items
    items_list = []
    if isinstance(data, list):
        items_list = data
    elif isinstance(data, dict):
        if 'products' in data and isinstance(data['products'], list):
            items_list = data['products']
        elif 'menu_items' in data and isinstance(data['menu_items'], list):
            items_list = data['menu_items']
        elif 'items' in data and isinstance(data['items'], list):
            items_list = data['items']
            
    for item in items_list:
        cat_name = item.get('category') or item.get('subcategory') or 'General Menu'
        parsed = parse_item(item)
        if parsed:
            if cat_name not in brands[brand_name]['categories']:
                brands[brand_name]['categories'][cat_name] = []
            brands[brand_name]['categories'][cat_name].append(parsed)

print(f"\nDiscovered {len(brands)} unique brands across extracted files.")

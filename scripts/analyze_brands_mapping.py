import os
import json
import glob
import re

extracted_dir = 'JSON Files'
target_dir = 'src/data/restaurants'

# Existing restaurants mapping
existing_slugs = {}
existing_by_name = {}
for fpath in glob.glob(os.path.join(target_dir, '*.json')):
    fname = os.path.basename(fpath)
    if fname == '_index.json':
        continue
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        slug = data.get('slug') or fname.replace('.json', '')
        name = data.get('name', slug)
        existing_slugs[slug] = {
            'path': fpath,
            'data': data,
            'name': name
        }
        clean_name = re.sub(r'[^a-z0-9]', '', name.lower())
        existing_by_name[clean_name] = slug
    except Exception as e:
        print(f"Error loading existing {fname}: {e}")

print(f"Loaded {len(existing_slugs)} existing restaurant records.")

# Helper to normalize item
def parse_item(raw_item):
    if not isinstance(raw_item, dict):
        return None
    name = raw_item.get('name') or raw_item.get('product_name') or raw_item.get('item_name')
    if not name or not isinstance(name, str):
        return None
    name = name.strip()
    if not name:
        return None
    
    nutr = raw_item.get('nutrition') if isinstance(raw_item.get('nutrition'), dict) else raw_item
    
    def get_num(keys):
        for k in keys:
            if k in nutr and nutr[k] is not None:
                try:
                    val = str(nutr[k]).replace('g', '').replace('mg', '').replace('kcal', '').replace(',', '').strip()
                    if val.lower() in ('', 'none', 'null', 'n/a', '-', 'undefined'):
                        continue
                    v = float(val)
                    return round(v, 1) if '.' in str(val) and not v.is_integer() else int(round(v))
                except:
                    pass
        return 0

    calories = get_num(['calories', 'calories_kcal', 'energy_kcal', 'cal', 'energy'])
    protein = get_num(['protein_g', 'protein', 'proteins', 'proteinContent'])
    fat = get_num(['fat_g', 'total_fat_g', 'fat', 'total_fat', 'fatContent'])
    carbs = get_num(['carbohydrates_g', 'total_carbohydrates_g', 'carbs', 'carbohydrate_g', 'carbohydrates', 'carbohydrateContent'])
    
    fiber = get_num(['fiber_g', 'dietary_fiber_g', 'fiber', 'fiberContent'])
    sodium = get_num(['sodium_mg', 'sodium', 'sodiumContent'])
    cholesterol = get_num(['cholesterol_mg', 'cholesterol'])
    sat_fat = get_num(['saturated_fat_g', 'saturated_fat', 'sat_fat_g'])
    sugars = get_num(['sugars_g', 'sugar_g', 'sugars', 'sugar', 'sugarContent'])
    
    item = {
        "name": name,
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs
    }
    if fiber > 0: item["fiber"] = fiber
    if sodium > 0: item["sodium"] = sodium
    if cholesterol > 0: item["cholesterol"] = cholesterol
    if sat_fat > 0: item["saturated_fat"] = sat_fat
    if sugars > 0: item["sugars"] = sugars
    
    return item

# Category classification
CATEGORY_KEYWORDS = {
    'Burger': ('Burgers & Fast Food', '🍔'),
    'Chicken': ('Chicken & Wings', '🍗'),
    'Wing': ('Chicken & Wings', '🍗'),
    'Pizza': ('Pizza & Italian', '🍕'),
    'Coffee': ('Coffee & Drinks', '☕'),
    'Tea': ('Coffee & Drinks', '🍵'),
    'Cafe': ('Coffee & Bakery', '☕'),
    'Bakery': ('Coffee & Bakery', '🥐'),
    'Bagel': ('Coffee & Bakery', '🥯'),
    'Sandwich': ('Sandwiches & Deli', '🥪'),
    'Deli': ('Sandwiches & Deli', '🥪'),
    'Sub': ('Sandwiches & Deli', '🥪'),
    'Taco': ('Mexican & Tex-Mex', '🌮'),
    'Burrito': ('Mexican & Tex-Mex', '🌯'),
    'Mexican': ('Mexican & Tex-Mex', '🌮'),
    'Asian': ('Asian & Bowls', '🥢'),
    'Sushi': ('Asian & Bowls', '🍣'),
    'Chinese': ('Asian & Bowls', '🥡'),
    'Thai': ('Asian & Bowls', '🍜'),
    'Grill': ('American & Grill', '🍽️'),
    'Diner': ('Diners & Breakfast', '🍳'),
    'Breakfast': ('Diners & Breakfast', '🥞'),
    'Smoothie': ('Smoothies & Shakes', '🥤'),
    'Juice': ('Smoothies & Shakes', '🥤'),
    'Ice Cream': ('Desserts & Treats', '🍦'),
    'Creamery': ('Desserts & Treats', '🍦'),
    'Yogurt': ('Desserts & Treats', '🍦'),
    'Donut': ('Coffee & Bakery', '🍩'),
    'Cinnabon': ('Desserts & Treats', '🧁'),
    'Steak': ('Steakhouse & Grill', '🥩'),
    'Salad': ('Healthy & Bowls', '🥗'),
    'Healthy': ('Healthy & Bowls', '🥗'),
    'Bowl': ('Healthy & Bowls', '🥗'),
    'Mediterranean': ('Mediterranean & Bowls', '🥙'),
    'BBQ': ('Barbecue & Smokehouse', '🍖'),
    'Barbecue': ('Barbecue & Smokehouse', '🍖'),
    'Seafood': ('Seafood', '🦞'),
    'Chili': ('American & Fast Food', '🍲'),
    'Pretzel': ('Snacks & Treats', '🥨'),
}

def guess_category_and_emoji(brand_name, items_sample=[]):
    combined = (brand_name + ' ' + ' '.join(items_sample)).lower()
    for kw, (cat, emoji) in CATEGORY_KEYWORDS.items():
        if kw.lower() in combined:
            return cat, emoji
    return 'Fast Casual & Dining', '🍽️'

def normalize_slug(name):
    # Strip existing suffixes
    s = name.lower().strip()
    s = re.sub(r'\b(nutrition|calculator|calories|menu|database|db)\b', '', s)
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s).strip('-')
    return f"{s}-nutrition-calculator"

# Scan extracted files
raw_brands = {}

def add_items_to_brand(brand_name, cat_name, items):
    brand_name = brand_name.strip()
    if not brand_name:
        return
    if brand_name not in raw_brands:
        raw_brands[brand_name] = {'categories': {}, 'files': set()}
    if cat_name not in raw_brands[brand_name]['categories']:
        raw_brands[brand_name]['categories'][cat_name] = []
    
    for it in items:
        p = parse_item(it)
        if p:
            raw_brands[brand_name]['categories'][cat_name].append(p)

for fpath in glob.glob(os.path.join(extracted_dir, '*.json')):
    fname = os.path.basename(fpath)
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Skipping {fname}: {e}")
        continue
        
    # Multi-restaurant database
    if isinstance(data, dict) and 'restaurants' in data and isinstance(data['restaurants'], list):
        for r in data['restaurants']:
            r_name = r.get('restaurant_name') or r.get('name')
            if isinstance(r_name, dict): r_name = r_name.get('name')
            if not r_name: continue
            items = r.get('items') or r.get('menu_items') or r.get('products') or []
            for item in items:
                cat = item.get('category') or item.get('subcategory') or 'General Menu'
                add_items_to_brand(r_name, cat, [item])
        continue

    # Dict format
    if isinstance(data, dict):
        # Determine brand
        brand_val = data.get('brand')
        if isinstance(brand_val, dict): brand_name = brand_val.get('name')
        elif isinstance(brand_val, str): brand_name = brand_val
        elif data.get('restaurant_name'): brand_name = data.get('restaurant_name')
        elif data.get('restaurant'): 
            brand_name = data['restaurant'] if isinstance(data['restaurant'], str) else data['restaurant'].get('name')
        else:
            brand_name = None
            
        if not brand_name:
            clean_fn = fname.replace('_nutrition_final.json', '').replace('_nutrition_db.json', '')
            clean_fn = clean_fn.replace('_nutrition.json', '').replace('_nutrition1.json', '').replace('_database.json', '')
            clean_fn = clean_fn.replace('_db.json', '').replace('.json', '')
            brand_name = clean_fn.replace('_', ' ').title()

        # Check for nested categories (e.g. DiBella's, Chicken Salad Chick)
        if 'categories' in data and isinstance(data['categories'], dict):
            for cat_k, cat_v in data['categories'].items():
                cat_title = cat_k.replace('_', ' ').title()
                if isinstance(cat_v, list):
                    add_items_to_brand(brand_name, cat_title, cat_v)
                elif isinstance(cat_v, dict):
                    for sub_k, sub_v in cat_v.items():
                        sub_title = f"{cat_title} ({sub_k.replace('_', ' ')})"
                        if isinstance(sub_v, list):
                            add_items_to_brand(brand_name, sub_title, sub_v)
        else:
            items_list = data.get('products') or data.get('menu_items') or data.get('items') or []
            if isinstance(items_list, list):
                for item in items_list:
                    cat = item.get('category') or item.get('subcategory') or 'General Menu'
                    add_items_to_brand(brand_name, cat, [item])
                    
    elif isinstance(data, list):
        clean_fn = fname.replace('_nutrition_final.json', '').replace('_nutrition_db.json', '')
        clean_fn = clean_fn.replace('_nutrition.json', '').replace('_nutrition1.json', '').replace('_database.json', '')
        clean_fn = clean_fn.replace('_db.json', '').replace('.json', '')
        brand_name = clean_fn.replace('_', ' ').title()
        for item in data:
            cat = item.get('category') or item.get('subcategory') or 'General Menu'
            add_items_to_brand(brand_name, cat, [item])

print(f"Extracted {len(raw_brands)} distinct brands.")

# Match raw_brands against existing restaurants
matched_existing = {}
unmatched_new = {}

# Brand aliases / normalizations
ALIASES = {
    'bk': 'burger-king-calories-calculator',
    'burger king': 'burger-king-calories-calculator',
    'bww': 'buffalo-wild-wings-nutrition-calculator',
    'buffalo wild wings': 'buffalo-wild-wings-nutrition-calculator',
    'carls jr': 'carls-jr-calories-calculator',
    'carl\'s jr.': 'carls-jr-calories-calculator',
    'chick-fil-a': 'chick-fil-a-nutrition-calculator',
    'chilis': 'chilis-calories-calculator',
    'chili\'s grill & bar': 'chilis-calories-calculator',
    'dairy queen': 'dairy-queen-nutrition-calculator',
    'dq': 'dairy-queen-nutrition-calculator',
    'dunkin': 'dunkin-donuts-nutrition-calculator',
    'dunkin\'': 'dunkin-donuts-nutrition-calculator',
    'dunkin donuts': 'dunkin-donuts-nutrition-calculator',
    'in-n-out': 'in-n-out-nutrition-calculator',
    'in n out': 'in-n-out-nutrition-calculator',
    'in-n-out burger': 'in-n-out-nutrition-calculator',
    'innout': 'in-n-out-nutrition-calculator',
    'jack in the box': 'jack-in-the-box-nutrition-calculator',
    'jersey mikes': 'jersey-mikes-calories-calculator',
    'jersey mike\'s subs': 'jersey-mikes-calories-calculator',
    'jimmy johns': 'jimmy-johns-calories-calculator',
    'jimmy john\'s': 'jimmy-johns-calories-calculator',
    'kfc': 'kfc-nutrition-calculator',
    'mcdonalds': 'mcdonalds-calories-calculator',
    'mcdonald\'s': 'mcdonalds-calories-calculator',
    'mod pizza': 'mod-pizza-calories-calculator',
    'panera bread': 'panera-bread-nutrition-calculator',
    'panera': 'panera-bread-nutrition-calculator',
    'pizza hut': 'pizza-hut-nutrition-calculator',
    'popeyes': 'popeyes-nutrition-calculator',
    'raising canes': 'raising-canes-calculator',
    'raising cane\'s': 'raising-canes-calculator',
    'shake shack': 'shake-shack-nutrition-calculator',
    'sonic drive-in': 'sonic-drive-in-nutrition-calculator',
    'sonic': 'sonic-drive-in-nutrition-calculator',
    'starbucks': 'starbucks-nutrition-calculator',
    'subway': 'subway-nutrition-calculator',
    'taco bell': 'taco-bell-nutrition-calculator',
    'wendys': 'wendys-nutrition-calculator',
    'wendy\'s': 'wendys-nutrition-calculator',
    'whataburger': 'whataburger-nutrition-calculator',
    'wingstop': 'wingstop-calories-calculator',
    'zaxbys': 'zaxbys-nutrition-calculator',
    'zaxby\'s': 'zaxbys-nutrition-calculator',
    'applebees': 'applebees-nutrition-calculator',
    'applebee\'s grill + bar': 'applebees-nutrition-calculator',
    'applebee\'s': 'applebees-nutrition-calculator',
    'bjs restaurant & brewhouse': 'bjs-nutrition-calculator',
    'bj\'s restaurant & brewhouse': 'bjs-nutrition-calculator',
    'bob evans': 'bob-evans-nutrition-calculator',
    'bob evans restaurant': 'bob-evans-nutrition-calculator',
    'caribou coffee': 'caribou-coffee-nutrition-calculator',
    'costa vida': 'costa-vida-nutrition-calculator',
    'culvers': 'culvers-nutrition-calculator',
    'culver\'s': 'culvers-nutrition-calculator',
    'daves hot chicken': 'daves-hot-chicken-nutrition-calculator',
    'dave\'s hot chicken': 'daves-hot-chicken-nutrition-calculator',
    'firehouse subs': 'firehouse-subs-nutrition-calculator',
    'first watch': 'first-watch-nutrition-calculator',
    'la madeleine': 'la-madeleine-nutrition-calculator',
    'mcalisters deli': 'mcalister\'s-deli-nutrition-calculator',
    'mcalister\'s deli': 'mcalisters-deli-nutrition-calculator',
    'red lobster': 'red-lobster-nutrition-calculator',
    'sheetz': 'sheetz-nutrition-calculator',
    'sweetgreen': 'sweetgreen-nutrition-calculator',
    'tazikis mediterranean cafe': 'tazikis-mediterranean-cafe-nutrition-calculator',
    'teds montana grill': 'teds-montana-grill-nutrition-calculator',
    'ted\'s montana grill': 'teds-montana-grill-nutrition-calculator',
    'the habit burger grill': 'the-habit-burger-grill-nutrition-calculator',
    'the cheesecake factory': 'the-cheesecake-factory-nutrition-calculator',
    'tim hortons': 'tim-hortons-nutrition-calculator',
    'tropical smoothie cafe': 'tropical-smoothie-cafe-nutrition-calculator',
}

for b_name, b_info in raw_brands.items():
    clean_b = re.sub(r'[^a-z0-9]', '', b_name.lower())
    
    # Check alias
    slug = None
    if b_name.lower() in ALIASES:
        slug = ALIASES[b_name.lower()]
    elif clean_b in ALIASES:
        slug = ALIASES[clean_b]
    elif clean_b in existing_by_name:
        slug = existing_by_name[clean_b]
        
    # Check partial match against existing slugs
    if not slug:
        for ex_slug, ex_obj in existing_slugs.items():
            ex_clean = re.sub(r'[^a-z0-9]', '', ex_obj['name'].lower())
            if clean_b == ex_clean or (len(clean_b) > 4 and clean_b in ex_clean) or (len(ex_clean) > 4 and ex_clean in clean_b):
                slug = ex_slug
                break
                
    total_items = sum(len(items) for items in b_info['categories'].values())
    if slug and slug in existing_slugs:
        matched_existing[b_name] = {
            'target_slug': slug,
            'existing_name': existing_slugs[slug]['name'],
            'existing_count': existing_slugs[slug]['data'].get('itemCount', 0),
            'extracted_count': total_items,
            'categories': b_info['categories']
        }
    else:
        unmatched_new[b_name] = {
            'proposed_slug': normalize_slug(b_name),
            'item_count': total_items,
            'categories': b_info['categories']
        }

print(f"\n--- MATCHED EXISTING RESTAURANTS: {len(matched_existing)} ---")
for k, v in list(matched_existing.items())[:15]:
    print(f"  {k} -> {v['target_slug']} (Existing: {v['existing_count']}, Extracted: {v['extracted_count']})")

print(f"\n--- NEW RESTAURANTS TO CREATE: {len(unmatched_new)} ---")
for k, v in sorted(unmatched_new.items(), key=lambda x: x[1]['item_count'], reverse=True)[:30]:
    print(f"  {k} -> {v['proposed_slug']} (Items: {v['item_count']})")

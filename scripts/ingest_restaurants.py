import os
import json
import glob
import re

extracted_dir = 'JSON Files'
target_dir = 'src/data/restaurants'
index_file = os.path.join(target_dir, '_index.json')

# 1. Repair dibellas if needed
dibellas_path = os.path.join(extracted_dir, 'dibellas_nutrition.json')
if os.path.exists(dibellas_path):
    with open(dibellas_path, 'rb') as f:
        raw_bytes = f.read()
    text = raw_bytes.decode('utf-8', errors='ignore').strip()
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
        try:
            json.loads(text)
            with open(dibellas_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print("Repaired dibellas_nutrition.json")
        except Exception as e:
            print(f"Dibellas repair note: {e}")

# Helper to normalize item
def parse_item(raw_item):
    if not isinstance(raw_item, dict):
        return None
    name = raw_item.get('name') or raw_item.get('product_name') or raw_item.get('item_name')
    if not name or not isinstance(name, str):
        return None
    name = name.strip()
    if not name or len(name) < 2:
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
    
    # Serving size if available
    serving = None
    if isinstance(raw_item.get('serving'), dict):
        serving = raw_item['serving'].get('size')
    elif isinstance(raw_item.get('serving_size'), str):
        serving = raw_item['serving_size']
    elif isinstance(raw_item.get('servingSize'), str):
        serving = raw_item['servingSize']

    item = {
        "name": name,
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs
    }
    if serving: item["servingSize"] = serving
    if fiber > 0: item["fiber"] = fiber
    if sodium > 0: item["sodium"] = sodium
    if cholesterol > 0: item["cholesterol"] = cholesterol
    if sat_fat > 0: item["saturated_fat"] = sat_fat
    if sugars > 0: item["sugars"] = sugars
    
    return item

# Category keywords & emojis
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
    s = name.lower().strip()
    s = re.sub(r'\b(nutrition|calculator|calories|menu|database|db)\b', '', s)
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s).strip('-')
    return f"{s}-nutrition-calculator"

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

# Brand Aliases
ALIASES = {
    '54th street grill & bar': '54th-street-grill-bar-nutrition-calculator',
    'another broken egg cafe': 'another-broken-egg-cafe-nutrition-calculator',
    'applebees': 'applebees-nutrition-calculator',
    'applebee\'s grill + bar': 'applebees-nutrition-calculator',
    'applebee\'s': 'applebees-nutrition-calculator',
    'arctic circle': 'arctic-circle-nutrition-calculator',
    'auntie anne\'s': 'auntie-annes-nutrition-calculator',
    'a&w restaurants': 'aw-restaurants-nutrition-calculator',
    'barberitos': 'barberitos-nutrition-calculator',
    'baskin-robbins': 'baskin-robbins-nutrition-calculator',
    'baskin robbins': 'baskin-robbins-nutrition-calculator',
    'bibibop asian grill': 'bibibop-calories-calculator',
    'bibibop': 'bibibop-calories-calculator',
    'bjs restaurant & brewhouse': 'bjs-nutrition-calculator',
    'bj\'s restaurant & brewhouse': 'bjs-nutrition-calculator',
    'bj\'s restaurants': 'bjs-nutrition-calculator',
    'black bear diner': 'black-bear-diner-nutrition-calculator',
    'blaze pizza': 'blaze-pizza-calories-calculator',
    'bob evans': 'bob-evans-nutrition-calculator',
    'bob evans restaurant': 'bob-evans-nutrition-calculator',
    'bojangles': 'bojangles-nutrition-calculator',
    'bonefish grill': 'bonefish-grill-nutrition-calculator',
    'bruegger\'s bagels': 'brueggers-bagels-nutrition-calculator',
    'brueggers bagels': 'brueggers-bagels-nutrition-calculator',
    'burgerfi': 'burgerfi-nutrition-calculator',
    'burgerville': 'burgerville-nutrition-calculator',
    'burger king': 'burger-king-calories-calculator',
    'bk': 'burger-king-calories-calculator',
    'buffalo wild wings': 'buffalo-wild-wings-nutrition-calculator',
    'bww': 'buffalo-wild-wings-nutrition-calculator',
    'cafe rio': 'cafe-rio-calories-calculator',
    'caribou coffee': 'caribou-coffee-nutrition-calculator',
    'carl\'s jr.': 'carls-jr-calories-calculator',
    'carls jr': 'carls-jr-calories-calculator',
    'casey\'s general stores': 'caseys-nutrition-calculator',
    'caseys': 'caseys-nutrition-calculator',
    'checkers': 'checkers-nutrition-calculator',
    'chicken express': 'chicken-express-nutrition-calculator',
    'chicken salad chick': 'chicken-salad-chick-nutrition-calculator',
    'chick-fil-a': 'chick-fil-a-nutrition-calculator',
    'chili\'s grill & bar': 'chilis-calories-calculator',
    'chilis': 'chilis-calories-calculator',
    'chipotle': 'chipotle-nutrition-calculator',
    'chopt creative salad co.': 'chopt-nutrition-calculator',
    'chopt': 'chopt-nutrition-calculator',
    'cinnabon': 'cinnabon-nutrition-calculator',
    'cold stone creamery': 'cold-stone-creamery-nutrition-calculator',
    'cook out': 'cookout-nutrition-calculator',
    'cookout': 'cookout-nutrition-calculator',
    'costa vida': 'costa-vida-nutrition-calculator',
    'cracker barrel': 'cracker-barrel-nutrition-calculator',
    'crazy bowls & wraps': 'crazy-bowls-wraps-nutrition-calculator',
    'culver\'s': 'culvers-nutrition-calculator',
    'culvers': 'culvers-nutrition-calculator',
    'dairy queen': 'dairy-queen-nutrition-calculator',
    'dq': 'dairy-queen-nutrition-calculator',
    'dave\'s hot chicken': 'daves-hot-chicken-nutrition-calculator',
    'daves hot chicken': 'daves-hot-chicken-nutrition-calculator',
    'del taco': 'del-taco-nutrition-calculator',
    'dibella\'s subs': 'dibellas-nutrition-calculator',
    'dickey\'s barbecue pit': 'dickeys-barbecue-pit-nutrition-calculator',
    'domino\'s': 'dominos-nutrition-calculator',
    'donatos pizza': 'donatos-pizza-nutrition-calculator',
    'dunkin\'': 'dunkin-nutrition-calculator',
    'dunkin donuts': 'dunkin-nutrition-calculator',
    'dunkin': 'dunkin-nutrition-calculator',
    'einstein bros. bagels': 'einstein-bros-bagels-nutrition-calculator',
    'el pollo loco': 'el-pollo-loco-nutrition-calculator',
    'fazoli\'s': 'fazolis-nutrition-calculator',
    'firehouse subs': 'firehouse-subs-nutrition-calculator',
    'first watch': 'first-watch-nutrition-calculator',
    'garbanzo mediterranean grill': 'garbanzo-mediterranean-grill-nutrition-calculator',
    'golden spoon': 'golden-spoon-nutrition-calculator',
    'hardee\'s': 'hardees-nutrition-calculator',
    'honey baked ham': 'honey-baked-ham-nutrition-calculator',
    'hoss\'s family steak & sea house': 'hosss-nutrition-calculator',
    'ihop': 'ihop-nutrition-calculator',
    'in-n-out': 'in-n-out-nutrition-calculator',
    'in-n-out burger': 'in-n-out-nutrition-calculator',
    'jack in the box': 'jack-in-the-box-nutrition-calculator',
    'jaggers': 'jaggers-nutrition-calculator',
    'jason\'s deli': 'jasons-deli-nutrition-calculator',
    'jersey mike\'s subs': 'jersey-mikes-calories-calculator',
    'jersey mikes': 'jersey-mikes-calories-calculator',
    'jet\'s pizza': 'jets-pizza-nutrition-calculator',
    'jimmy john\'s': 'jimmy-johns-calories-calculator',
    'jose pepper\'s': 'jose-peppers-nutrition-calculator',
    'kfc': 'kfc-nutrition-calculator',
    'krystal': 'krystal-nutrition-calculator',
    'la madeleine': 'la-madeleine-nutrition-calculator',
    'lamar\'s donuts': 'lamars-donuts-nutrition-calculator',
    'ledo pizza': 'ledo-pizza-nutrition-calculator',
    'little caesars': 'little-caesars-nutrition-calculator',
    'l&l hawaiian barbecue': 'll-hawaiian-bbq-nutrition-calculator',
    'longhorn steakhouse': 'longhorn-steakhouse-nutrition-calculator',
    'manhattan bagel': 'manhattan-bagel-nutrition-calculator',
    'marco\'s pizza': 'marcos-pizza-nutrition-calculator',
    'mcalister\'s deli': 'mcalisters-deli-nutrition-calculator',
    'mcdonald\'s': 'mcdonalds-calories-calculator',
    'menchie\'s frozen yogurt': 'menchies-frozen-yogurt-nutrition-calculator',
    'mission bbq': 'mission-bbq-nutrition-calculator',
    'mr. pickles sandwich shop': 'mr-pickles-sandwich-shop-nutrition-calculator',
    'newk\'s eatery': 'newks-eatery-nutrition-calculator',
    'noodles & company': 'noodles-company-nutrition-calculator',
    'olive garden': 'olive-garden-nutrition-calculator',
    'orange leaf': 'orange-leaf-nutrition-calculator',
    'pancheros mexican grill': 'pancheros-mexican-grill-nutrition-calculator',
    'panera bread': 'panera-bread-nutrition-calculator',
    'papa murphy\'s': 'papa-murphys-nutrition-calculator',
    'perkins restaurant & bakery': 'perkins-nutrition-calculator',
    'peter piper pizza': 'peter-piper-pizza-nutrition-calculator',
    'p.f. chang\'s': 'pf-changs-nutrition-calculator',
    'pieology pizzeria': 'pieology-nutrition-calculator',
    'pita pit': 'pita-pit-nutrition-calculator',
    'pizza hut': 'pizza-hut-nutrition-calculator',
    'pizza ranch': 'pizza-ranch-nutrition-calculator',
    'popeyes': 'popeyes-nutrition-calculator',
    'portillo\'s': 'portillos-nutrition-calculator',
    'port of subs': 'port-of-subs-nutrition-calculator',
    'potbelly': 'potbelly-nutrition-calculator',
    'quiznos': 'quiznos-nutrition-calculator',
    'raising cane\'s': 'raising-canes-calculator',
    'red lobster': 'red-lobster-nutrition-calculator',
    'robeks': 'robeks-nutrition-calculator',
    'round table pizza': 'round-table-pizza-nutrition-calculator',
    'roxberry juice': 'roxberry-juice-nutrition-calculator',
    'saladworks': 'saladworks-nutrition-calculator',
    'schlotzsky\'s': 'schlotzskys-nutrition-calculator',
    'sheetz': 'sheetz-nutrition-calculator',
    'skyline chili': 'skyline-chili-nutrition-calculator',
    'sonic drive-in': 'sonic-drive-in-nutrition-calculator',
    'sonic': 'sonic-drive-in-nutrition-calculator',
    'starbucks': 'starbucks-nutrition-calculator',
    'steak \'n shake': 'steak-n-shake-nutrition-calculator',
    'subway': 'subway-nutrition-calculator',
    'sweetgreen': 'sweetgreen-nutrition-calculator',
    'taco john\'s': 'taco-johns-nutrition-calculator',
    'taco bell': 'taco-bell-nutrition-calculator',
    'taziki\'s mediterranean cafe': 'tazikis-mediterranean-cafe-nutrition-calculator',
    'ted\'s montana grill': 'teds-montana-grill-nutrition-calculator',
    'texas de brazil': 'texas-de-brazil-nutrition-calculator',
    'the cheesecake factory': 'the-cheesecake-factory-nutrition-calculator',
    'the habit burger grill': 'the-habit-burger-grill-nutrition-calculator',
    'tim hortons': 'tim-hortons-nutrition-calculator',
    'urbane cafe': 'urbane-cafe-nutrition-calculator',
    'waba grill': 'waba-grill-nutrition-calculator',
    'wahoo\'s fish taco': 'wahoos-fish-taco-nutrition-calculator',
    'wawa': 'wawa-nutrition-calculator',
    'wendy\'s': 'wendys-nutrition-calculator',
    'whataburger': 'whataburger-nutrition-calculator',
    'wienerschnitzel': 'wienerschnitzel-nutrition-calculator',
    'yard house': 'yard-house-nutrition-calculator',
    'yoshinoya': 'yoshinoya-nutrition-calculator',
    'zaxby\'s': 'zaxbys-nutrition-calculator',
    'zoup!': 'zoup-nutrition-calculator',
}

# Scan extracted files
raw_brands = {}

def add_items_to_brand(brand_name, cat_name, items):
    if not brand_name: return
    brand_name = brand_name.strip()
    if not brand_name: return
    if brand_name not in raw_brands:
        raw_brands[brand_name] = {'categories': {}, 'files': set()}
    cat_name = cat_name.strip() or 'General Menu'
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

print(f"Extracted data for {len(raw_brands)} distinct brands.")

# Process each brand
updated_count = 0
created_count = 0

all_final_restaurants = {}

# First, populate all_final_restaurants with all existing records
for slug, ex_obj in existing_slugs.items():
    all_final_restaurants[slug] = ex_obj['data']

for b_name, b_info in raw_brands.items():
    clean_b = re.sub(r'[^a-z0-9]', '', b_name.lower())
    
    slug = None
    if b_name.lower() in ALIASES:
        slug = ALIASES[b_name.lower()]
    elif clean_b in ALIASES:
        slug = ALIASES[clean_b]
    elif clean_b in existing_by_name:
        slug = existing_by_name[clean_b]
        
    if not slug:
        for ex_slug, ex_obj in existing_slugs.items():
            ex_clean = re.sub(r'[^a-z0-9]', '', ex_obj['name'].lower())
            if clean_b == ex_clean or (len(clean_b) > 4 and clean_b in ex_clean) or (len(ex_clean) > 4 and ex_clean in clean_b):
                slug = ex_slug
                break
                
    if not slug:
        slug = normalize_slug(b_name)

    # Flatten extracted items
    extracted_categories = b_info['categories']
    
    if slug in all_final_restaurants:
        # MERGE with existing restaurant
        target_res = all_final_restaurants[slug]
        existing_cats = {c['name'].lower().strip(): c for c in target_res.get('categories', [])}
        existing_item_names = set()
        for c in target_res.get('categories', []):
            for it in c.get('items', []):
                existing_item_names.add(it['name'].lower().strip())
                
        added_items = 0
        for cat_name, items in extracted_categories.items():
            cat_lower = cat_name.lower().strip()
            # If category exists, append unique items
            if cat_lower in existing_cats:
                for it in items:
                    it_lower = it['name'].lower().strip()
                    if it_lower not in existing_item_names:
                        existing_cats[cat_lower]['items'].append(it)
                        existing_item_names.add(it_lower)
                        added_items += 1
            else:
                # Add new category with unique items
                unique_new_items = []
                for it in items:
                    it_lower = it['name'].lower().strip()
                    if it_lower not in existing_item_names:
                        unique_new_items.append(it)
                        existing_item_names.add(it_lower)
                        added_items += 1
                if unique_new_items:
                    target_res.setdefault('categories', []).append({
                        'name': cat_name,
                        'items': unique_new_items
                    })
                    existing_cats[cat_lower] = target_res['categories'][-1]
                    
        total_items = sum(len(c['items']) for c in target_res.get('categories', []))
        target_res['itemCount'] = total_items
        updated_count += 1
    else:
        # CREATE NEW RESTAURANT
        all_items_sample = [it['name'] for items in extracted_categories.values() for it in items[:5]]
        category_name, emoji = guess_category_and_emoji(b_name, all_items_sample)
        
        # Build category list
        formatted_cats = []
        total_items = 0
        seen_names = set()
        for cat_name, items in extracted_categories.items():
            unique_items = []
            for it in items:
                it_name_clean = it['name'].lower().strip()
                if it_name_clean not in seen_names:
                    seen_names.add(it_name_clean)
                    unique_items.append(it)
            if unique_items:
                formatted_cats.append({
                    'name': cat_name,
                    'items': unique_items
                })
                total_items += len(unique_items)
                
        if total_items == 0:
            continue
            
        new_res = {
            "name": b_name,
            "slug": slug,
            "tagline": f"Track nutrition for {b_name} menu items, meals, calories, and macros.",
            "description": f"Calculate calories, protein, carbs, fat, sodium, and nutrients across {total_items} menu items at {b_name}.",
            "category": category_name,
            "emoji": emoji,
            "itemCount": total_items,
            "categories": formatted_cats
        }
        all_final_restaurants[slug] = new_res
        created_count += 1

print(f"\nProcessing summary: {updated_count} merged/updated, {created_count} newly created.")
print(f"Total restaurants in database: {len(all_final_restaurants)}")

# Write all restaurant JSON files to target_dir
for slug, res_data in all_final_restaurants.items():
    file_path = os.path.join(target_dir, f"{slug}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(res_data, f, indent=2)

# Generate updated _index.json
index_list = []
total_site_items = 0
for slug, res_data in all_final_restaurants.items():
    item_cnt = res_data.get('itemCount') or sum(len(c.get('items', [])) for c in res_data.get('categories', []))
    total_site_items += item_cnt
    index_list.append({
        "slug": slug,
        "name": res_data.get('name', slug),
        "category": res_data.get('category', 'Fast Casual & Dining'),
        "itemCount": item_cnt,
        "emoji": res_data.get('emoji', '🍽️')
    })

index_list.sort(key=lambda x: x['name'].lower())

final_index_data = {
    "totalRestaurants": len(index_list),
    "totalItems": total_site_items,
    "restaurants": index_list
}

with open(index_file, 'w', encoding='utf-8') as f:
    json.dump(final_index_data, f, indent=2)

print(f"\nUpdated _index.json with {len(index_list)} restaurants and {total_site_items} total items.")

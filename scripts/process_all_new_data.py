import os
import json
import glob
import re

extracted_dir = 'JSON Files'
target_dir = 'src/data/restaurants'

# Fix dibellas
dibellas_path = os.path.join(extracted_dir, 'dibellas_nutrition.json')
if os.path.exists(dibellas_path):
    with open(dibellas_path, 'rb') as f:
        raw_bytes = f.read()
    # Decode utf-8 and clean
    text = raw_bytes.decode('utf-8', errors='ignore').strip()
    # Find valid json bounds
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
        try:
            parsed_test = json.loads(text)
            with open(dibellas_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print("Successfully repaired dibellas_nutrition.json")
        except Exception as e:
            print(f"Error repairing dibellas: {e}")

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
        existing_slugs[slug] = (fpath, data)
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

def clean_brand_name(brand_val, filename=""):
    if isinstance(brand_val, dict):
        brand_val = brand_val.get('name', '')
    if not brand_val or not isinstance(brand_val, str):
        brand_val = ""
        
    brand_str = brand_val.strip()
    if not brand_str or len(brand_str) < 2 or brand_str.lower() in ('unknown', 'brand', 'restaurant', 'n/a'):
        # Deduce from filename
        base = filename.replace('_nutrition_final.json', '').replace('_nutrition_db.json', '')
        base = base.replace('_nutrition.json', '').replace('_nutrition1.json', '').replace('_database.json', '')
        base = base.replace('_db.json', '').replace('.json', '')
        brand_str = base.replace('_', ' ').title()
        
    # Common cleanups
    brand_str = brand_str.replace('', "'")
    return brand_str

# Known category & emoji mapping
CATEGORY_KEYWORDS = {
    'Burger': ('Burgers & Fast Food', '🍔'),
    'Chicken': ('Chicken & Wings', '🍗'),
    'Pizza': ('Pizza & Italian', '🍕'),
    'Coffee': ('Coffee & Drinks', '☕'),
    'Cafe': ('Coffee & Bakery', '☕'),
    'Bakery': ('Coffee & Bakery', '🥐'),
    'Sandwich': ('Sandwiches & Deli', '🥪'),
    'Deli': ('Sandwiches & Deli', '🥪'),
    'Sub': ('Sandwiches & Deli', '🥪'),
    'Taco': ('Mexican & Tex-Mex', '🌮'),
    'Burrito': ('Mexican & Tex-Mex', '🌯'),
    'Mexican': ('Mexican & Tex-Mex', '🌮'),
    'Asian': ('Asian & Bowls', '🥢'),
    'Sushi': ('Asian & Bowls', '🍣'),
    'Chinese': ('Asian & Bowls', '🥡'),
    'Smoothie': ('Smoothies & Shakes', '🥤'),
    'Juice': ('Smoothies & Shakes', '🥤'),
    'Ice Cream': ('Desserts & Treats', '🍦'),
    'Frozen Yogurt': ('Desserts & Treats', '🍦'),
    'Steak': ('Steakhouse & Grill', '🥩'),
    'Grill': ('American & Grill', '🍽️'),
    'Diner': ('Diners & Breakfast', '🍳'),
    'Breakfast': ('Diners & Breakfast', '🥞'),
    'Salad': ('Healthy & Bowls', '🥗'),
    'Healthy': ('Healthy & Bowls', '🥗'),
    'Mediterranean': ('Mediterranean & Bowls', '🥙'),
    'BBQ': ('Barbecue & Smokehouse', '🍖'),
    'Barbecue': ('Barbecue & Smokehouse', '🍖'),
    'Seafood': ('Seafood', '🦞')
}

def guess_category_and_emoji(brand_name, items_sample=[]):
    combined = (brand_name + ' ' + ' '.join(items_sample)).lower()
    for kw, (cat, emoji) in CATEGORY_KEYWORDS.items():
        if kw.lower() in combined:
            return cat, emoji
    return 'Fast Casual & Dining', '🍽️'

print("Ready to process all extracted files.")

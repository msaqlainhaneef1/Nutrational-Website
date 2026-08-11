import os
import json
import re
from bs4 import BeautifulSoup

workspace_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website"
extracted_dir = os.path.join(workspace_dir, "extracted_articles")
restaurants_dir = os.path.join(workspace_dir, "src", "data", "restaurants")
foods_dir = os.path.join(workspace_dir, "src", "data", "foods")
registry_path = os.path.join(workspace_dir, "src", "features", "calculators", "shared", "registry.ts")

print("==================================================")
print("AUDITING ARTICLE CONTENT ACROSS 100% OF SITE PAGES")
print("==================================================")

# 1. Audit Restaurant JSON files
restaurant_files = [f for f in os.listdir(restaurants_dir) if f.endswith(".json") and f != "_index.json"]
print(f"Total Restaurant Pages to Audit: {len(restaurant_files)}")

short_restaurants = []
healthy_restaurants = []

for rfile in restaurant_files:
    rpath = os.path.join(restaurants_dir, rfile)
    with open(rpath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    name = data.get("name", "")
    slug = data.get("slug", "")
    html = data.get("articleHtml", "")
    text_len = len(BeautifulSoup(html, "html.parser").get_text()) if html else 0
    
    if text_len < 1000:
        short_restaurants.append((name, slug, text_len, rpath))
        print(f"[TRUNCATED/SHORT] Restaurant '{name}' ({slug}): Only {text_len} chars")
    else:
        healthy_restaurants.append((name, slug, text_len))

print(f"\n[SUMMARY] Healthy Restaurant Articles: {len(healthy_restaurants)} / {len(restaurant_files)}")
print(f"[SUMMARY] Truncated/Short Restaurant Articles: {len(short_restaurants)} / {len(restaurant_files)}\n")

# 2. Audit Food JSON files
food_files = [f for f in os.listdir(foods_dir) if f.endswith(".json")]
print(f"Total Food Pages to Audit: {len(food_files)}")

short_foods = []
healthy_foods = []

for ffile in food_files:
    fpath = os.path.join(foods_dir, ffile)
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    name = data.get("name", "")
    slug = data.get("slug", "")
    html = data.get("articleHtml", "")
    text_len = len(BeautifulSoup(html, "html.parser").get_text()) if html else 0
    
    if text_len < 1000:
        short_foods.append((name, slug, text_len, fpath))
        print(f"[TRUNCATED/SHORT] Food '{name}' ({slug}): Only {text_len} chars")
    else:
        healthy_foods.append((name, slug, text_len))

print(f"\n[SUMMARY] Healthy Food Articles: {len(healthy_foods)} / {len(food_files)}")
print(f"[SUMMARY] Truncated/Short Food Articles: {len(short_foods)} / {len(food_files)}\n")

# 3. Audit Health Calculator Registry
with open(registry_path, "r", encoding="utf-8") as f:
    reg_code = f.read()

calc_slugs = ["bmi", "bmr", "tdee", "macro", "calorie-deficit", "protein", "water-intake", "ideal-weight"]
print(f"Total Calculator Pages to Audit: {len(calc_slugs)}")

short_calcs = []
healthy_calcs = []

for cslug in calc_slugs:
    m = re.search(f"slug:\\s*'{cslug}'.*?articleHtml:\\s*(\"(?:\\\\.|[^\"\\\\])*\")", reg_code, re.DOTALL)
    if m:
        try:
            raw_html = json.loads(m.group(1))
            text_len = len(BeautifulSoup(raw_html, "html.parser").get_text())
            if text_len < 1000:
                short_calcs.append((cslug, text_len))
                print(f"[TRUNCATED/SHORT] Calculator '{cslug}': Only {text_len} chars")
            else:
                healthy_calcs.append((cslug, text_len))
        except Exception:
            short_calcs.append((cslug, 0))
    else:
        short_calcs.append((cslug, 0))
        print(f"[TRUNCATED/SHORT] Calculator '{cslug}': Missing articleHtml")

print(f"\n[SUMMARY] Healthy Calculator Articles: {len(healthy_calcs)} / {len(calc_slugs)}")
print(f"[SUMMARY] Truncated/Short Calculator Articles: {len(short_calcs)} / {len(calc_slugs)}")

print("\n==================================================")

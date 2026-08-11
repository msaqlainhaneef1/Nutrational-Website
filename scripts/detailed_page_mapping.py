import os
import json
import re
from bs4 import BeautifulSoup

workspace_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website"
data_restaurants_dir = os.path.join(workspace_dir, "src", "data", "restaurants")
data_foods_dir = os.path.join(workspace_dir, "src", "data", "foods")
extracted_dir = os.path.join(workspace_dir, "extracted_articles")

# 1. Health Calculators (from src/pages/calculators/)
calculators = [
    {"slug": "bmi", "route": "/calculators/bmi", "name": "BMI Calculator"},
    {"slug": "bmr", "route": "/calculators/bmr", "name": "BMR Calculator"},
    {"slug": "body-fat", "route": "/calculators/body-fat", "name": "Body Fat Calculator"},
    {"slug": "calorie-deficit", "route": "/calculators/calorie-deficit", "name": "Calorie Deficit Calculator"},
    {"slug": "ideal-weight", "route": "/calculators/ideal-weight", "name": "Ideal Weight Calculator"},
    {"slug": "macro", "route": "/calculators/macro", "name": "Macro Calculator"},
    {"slug": "protein", "route": "/calculators/protein", "name": "Protein Calculator"},
    {"slug": "tdee", "route": "/calculators/tdee", "name": "TDEE Calculator"},
    {"slug": "water-intake", "route": "/calculators/water-intake", "name": "Water Intake Calculator"}
]

# 2. Restaurant Pages (from src/data/restaurants/)
restaurants = []
if os.path.exists(data_restaurants_dir):
    for f in os.listdir(data_restaurants_dir):
        if f.endswith(".json") and f != "_index.json":
            slug = f.replace(".json", "")
            route = f"/restaurants/{slug}"
            restaurants.append({"slug": slug, "route": route, "file": f})

# 3. Food Pages (from src/data/foods/)
foods = []
if os.path.exists(data_foods_dir):
    for f in os.listdir(data_foods_dir):
        if f.endswith(".json") and f != "_index.json":
            slug = f.replace(".json", "")
            route = f"/foods/{slug}"
            foods.append({"slug": slug, "route": route, "file": f})

# 4. Extracted HTML files
extracted_htmls = []
html_files = [f for f in os.listdir(extracted_dir) if f.endswith(".html")]

for fname in html_files:
    fpath = os.path.join(extracted_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.title.string.strip() if soup.title and soup.title.string else fname.replace(".html", "")
    h1 = soup.find("h1") or soup.find(class_="title")
    h1_text = h1.get_text().strip() if h1 else title_tag
    clean_title = re.sub(r'^(Meta Title|SEO Title)[:\s]*', '', title_tag, flags=re.IGNORECASE).strip()

    # slugify helper
    slug_key = re.sub(r'[^a-z0-9]', '', fname.lower())

    extracted_htmls.append({
        "filename": fname,
        "title_tag": title_tag,
        "clean_title": clean_title,
        "h1_text": h1_text,
        "slug_key": slug_key,
        "raw_text": (clean_title + " " + fname).lower()
    })

print(f"Website Resources Discovered:")
print(f"  - Health Calculators: {len(calculators)}")
print(f"  - Restaurant Pages (JSON data): {len(restaurants)}")
print(f"  - Food Pages (JSON data): {len(foods)}")
print(f"  - Total Website Content Pages: {len(calculators) + len(restaurants) + len(foods)}")
print(f"  - Total Extracted HTML Articles: {len(extracted_htmls)}")

def norm_str(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

used_htmls = set()
matched_results = []
missing_html_for_pages = []

# Match Calculators
for calc in calculators:
    c_norm = norm_str(calc["name"])
    match = None
    for h in extracted_htmls:
        if c_norm in h["slug_key"] or norm_str(calc["slug"]) in h["slug_key"]:
            match = h
            break
    if match:
        used_htmls.add(match["filename"])
        matched_results.append(("Calculator", calc["route"], calc["name"], match["filename"]))
    else:
        missing_html_for_pages.append(("Calculator", calc["route"], calc["name"]))

# Match Restaurants
for rest in restaurants:
    # clean slug
    r_slug = rest["slug"]
    r_norm = norm_str(r_slug)
    match = None
    for h in extracted_htmls:
        h_norm = h["slug_key"]
        # Match slug key or keywords
        if r_norm in h_norm or h_norm in r_norm:
            match = h
            break
    if not match:
        # try matching core brand name
        brand = r_slug.replace("-nutrition-calculator", "").replace("-calories-calculator", "").replace("-calculator", "")
        b_norm = norm_str(brand)
        for h in extracted_htmls:
            if b_norm and b_norm in h["slug_key"]:
                match = h
                break

    if match:
        used_htmls.add(match["filename"])
        matched_results.append(("Restaurant", rest["route"], rest["slug"], match["filename"]))
    else:
        missing_html_for_pages.append(("Restaurant", rest["route"], rest["slug"]))

# Match Foods
for food in foods:
    f_slug = food["slug"]
    f_norm = norm_str(f_slug)
    match = None
    for h in extracted_htmls:
        if f_norm in h["slug_key"]:
            match = h
            break
    if match:
        used_htmls.add(match["filename"])
        matched_results.append(("Food", food["route"], food["slug"], match["filename"]))
    else:
        missing_html_for_pages.append(("Food", food["route"], food["slug"]))

unmatched_html_files = [h for h in extracted_htmls if h["filename"] not in used_htmls]

print("\n==================================================")
print("AUDIT RESULTS SUMMARY")
print("==================================================")
print(f"Total Matches Found (Page <---> HTML): {len(matched_results)}")
print(f"Website Pages Missing HTML File: {len(missing_html_for_pages)}")
print(f"Extracted HTML Files Missing Dedicated Website Page: {len(unmatched_html_files)}")

print("\n--- SAMPLE MATCHED PAGES (15 examples) ---")
for cat, route, name, h_file in matched_results[:15]:
    print(f"[{cat}] {route} <---> '{h_file}'")

print("\n--- WEBSITE PAGES MISSING HTML FILES ---")
for cat, route, name in missing_html_for_pages:
    print(f"[{cat}] {route} ({name})")

print("\n--- EXTRACTED HTML FILES THAT ARE NEW / MISSING FROM WEBSITE DATA (Sample 25) ---")
for h in unmatched_html_files[:25]:
    print(f"- '{h['filename']}'")


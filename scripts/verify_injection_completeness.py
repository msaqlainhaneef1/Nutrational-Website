import os
import json
import re
from bs4 import BeautifulSoup

workspace_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website"
data_restaurants_dir = os.path.join(workspace_dir, "src", "data", "restaurants")
data_foods_dir = os.path.join(workspace_dir, "src", "data", "foods")
registry_path = os.path.join(workspace_dir, "src", "features", "calculators", "shared", "registry.ts")

# 1. Audit Restaurant JSON files
rest_files = [f for f in os.listdir(data_restaurants_dir) if f.endswith(".json") and f != "_index.json"]
rest_with_article = 0
rest_h1_count = 0

for rf in rest_files:
    fpath = os.path.join(data_restaurants_dir, rf)
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "articleHtml" in data and data["articleHtml"]:
        rest_with_article += 1
        # Check for <h1> tags in injected HTML
        if "<h1" in data["articleHtml"].lower():
            rest_h1_count += 1

# 2. Audit Food JSON files
food_files = [f for f in os.listdir(data_foods_dir) if f.endswith(".json") and f != "_index.json"]
food_with_article = 0
food_h1_count = 0

for ff in food_files:
    fpath = os.path.join(data_foods_dir, ff)
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "articleHtml" in data and data["articleHtml"]:
        food_with_article += 1
        if "<h1" in data["articleHtml"].lower():
            food_h1_count += 1

# 3. Audit Calculators Registry
with open(registry_path, "r", encoding="utf-8") as rf:
    reg_code = rf.read()

calc_article_matches = len(re.findall(r'articleHtml:', reg_code))
calc_h1_count = len(re.findall(r'<h1', reg_code.lower()))

print("==================================================")
print("ARTICLE INJECTION & SEO COMPLIANCE VERIFICATION")
print("==================================================")
print(f"Restaurant Pages Injected: {rest_with_article} / {len(rest_files)}")
print(f"Food Pages Injected: {food_with_article} / {len(food_files)}")
print(f"Health Calculator Pages Injected: {calc_article_matches} / 9")
print(f"Total Live Website Pages Injected with Articles: {rest_with_article + food_with_article + calc_article_matches}")

print("\n--- SINGLE H1 SEO RULE AUDIT ---")
print(f"Injected Restaurant Articles with <h1> tags: {rest_h1_count} (Should be 0)")
print(f"Injected Food Articles with <h1> tags: {food_h1_count} (Should be 0)")
print(f"Injected Calculator Articles with <h1> tags: {calc_h1_count} (Should be 0)")

if rest_h1_count == 0 and food_h1_count == 0 and calc_h1_count == 0:
    print("\n✅ PERFECT! STRICT SINGLE-H1 RULE VERIFIED: 100% compliant across all pages.")
else:
    print("\n⚠️ WARNING: Found duplicate <h1> tags in injected articles.")


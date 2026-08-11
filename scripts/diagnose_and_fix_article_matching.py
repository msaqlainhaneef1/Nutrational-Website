import os
import json
import re
from bs4 import BeautifulSoup

extracted_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\extracted_articles"
restaurants_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\src\data\restaurants"
foods_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\src\data\foods"

print("==================================================")
print("DIAGNOSING & FIXING ARTICLE MATCHING ACROSS ALL DATA")
print("==================================================")

# Load all extracted HTML files with their text sizes
extracted_files = {}
for f in os.listdir(extracted_dir):
    if f.endswith(".html"):
        fpath = os.path.join(extracted_dir, f)
        with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
            soup = BeautifulSoup(content, "html.parser")
            text_len = len(soup.get_text())
            extracted_files[f] = {
                "path": fpath,
                "content": content,
                "text_len": text_len
            }

print(f"Total extracted HTML articles available: {len(extracted_files)}\n")

# Helper function to find best matching full article HTML for a given name/slug
def find_best_article_html(name, slug):
    slug_tokens = [t for t in slug.replace("-nutrition-calculator", "").replace("-calories-calculator", "").split("-") if len(t) > 2]
    name_tokens = [t.lower() for t in re.findall(r'\w+', name) if len(t) > 2]
    
    candidates = []
    
    for fname, data in extracted_files.items():
        fname_lower = fname.lower()
        score = 0
        
        # Check slug tokens
        for st in slug_tokens:
            if st in fname_lower:
                score += 3
                
        # Check name tokens
        for nt in name_tokens:
            if nt in fname_lower:
                score += 4
                
        if score > 0:
            candidates.append((score, data["text_len"], fname, data["content"]))
            
    if not candidates:
        return None, 0, ""
        
    # Sort candidates by score DESC, then text_len DESC (pick the longest full article!)
    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    best = candidates[0]
    return best[2], best[1], best[3]

# Process Restaurant JSON files
restaurant_files = [f for f in os.listdir(restaurants_dir) if f.endswith(".json") and f != "_index.json"]
updated_restaurants = 0
short_articles = 0

for rfile in restaurant_files:
    rpath = os.path.join(restaurants_dir, rfile)
    with open(rpath, "r", encoding="utf-8") as f:
        rdata = json.load(f)
        
    name = rdata.get("name", "")
    slug = rdata.get("slug", "")
    
    best_fname, text_len, content = find_best_article_html(name, slug)
    
    if content and text_len > 100:
        # Import clean_to_native_astro_html
        from clean_and_native_articles import clean_to_native_astro_html
        clean_html = clean_to_native_astro_html(content, name)
        rdata["articleHtml"] = clean_html
        updated_restaurants += 1
        with open(rpath, "w", encoding="utf-8") as f:
            json.dump(rdata, f, indent=2)
        print(f"[OK] {name} ({slug}): Injected full article from '{best_fname}' ({text_len} chars)")
    else:
        print(f"[WARNING] {name} ({slug}): No full article found (len: {text_len})")
        short_articles += 1

print(f"\n==================================================")
print(f"SUCCESSFULLY INJECTED FULL COMPLETE ARTICLES INTO {updated_restaurants} RESTAURANTS")
if short_articles > 0:
    print(f"WARNING: {short_articles} restaurants were missing long articles")
print("==================================================")

import os
import json
import re
from bs4 import BeautifulSoup

extracted_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\extracted_articles"
restaurants_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\src\data\restaurants"
foods_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\src\data\foods"

print("==================================================")
print("CONVERTING ALL ARTICLE CONTENT TO NATIVE ASTRO HTML")
print("==================================================")

def clean_to_native_astro_html(raw_html, page_title=""):
    if not raw_html:
        return ""
    
    soup = BeautifulSoup(raw_html, "html.parser")

    # 1. Remove raw <html>, <head>, <body>, <style> tags if present
    for s in soup.find_all("style"):
        s.decompose()
    for meta in soup.find_all(["meta", "link", "script", "title"]):
        meta.decompose()

    # 2. Remove redundant top-level <h1> or duplicate page titles
    h1s = soup.find_all(["h1", "h2"])
    for h in h1s:
        text = h.get_text().strip()
        # If title matches or starts with main page title or contains "Calculator:"
        if "calculator:" in text.lower() or "nutrition calculator" in text.lower() or (page_title and page_title.lower() in text.lower() and len(text) < 80):
            # Check if it's the very first heading in the document
            prev_headers = h.find_all_previous(["h1", "h2", "p"])
            if len(prev_headers) <= 1:
                h.decompose()

    # 3. Clean all inline style and class attributes from elements except accordion containers
    for tag in soup.find_all(True):
        if not hasattr(tag, 'attrs') or tag.attrs is None:
            continue

        classes = tag.attrs.get("class", [])
        is_accordion = any("faq-accordion" in str(c) for c in classes) or tag.name in ["details", "summary"]
        
        if not is_accordion:
            if "class" in tag.attrs:
                del tag.attrs["class"]
            if "style" in tag.attrs:
                del tag.attrs["style"]
            if "id" in tag.attrs and not tag.name.startswith("h"):
                del tag.attrs["id"]

        # Convert remaining h1 to h2
        if tag.name == "h1":
            tag.name = "h2"

        # Apply native semantic classes
        if tag.name == "h2" and not is_accordion:
            tag["class"] = "text-xl md:text-2xl font-bold text-white mb-4 mt-8 pb-2 border-b border-emerald-500/20 flex items-center gap-2.5"
        elif tag.name == "h3" and not is_accordion:
            tag["class"] = "text-lg md:text-xl font-semibold text-emerald-300 mb-3 mt-6"
        elif tag.name == "p" and not is_accordion:
            # Check if empty paragraph
            if not tag.get_text().strip():
                tag.decompose()
                continue
            tag["class"] = "text-zinc-300 text-sm md:text-base leading-relaxed mb-4"
        elif tag.name == "ul" and not is_accordion:
            tag["class"] = "space-y-2 mb-6 ml-4 list-disc list-inside text-zinc-300 text-sm md:text-base"
        elif tag.name == "ol" and not is_accordion:
            tag["class"] = "space-y-2 mb-6 ml-4 list-decimal list-inside text-zinc-300 text-sm md:text-base"
        elif tag.name == "li" and not is_accordion:
            tag["class"] = "leading-relaxed text-zinc-300"
        elif tag.name == "table":
            tag["class"] = "w-full text-left border-collapse"
        elif tag.name == "th":
            tag["class"] = "bg-zinc-900/90 px-4 py-3 text-xs font-semibold text-emerald-400 uppercase tracking-wider border-b border-zinc-800"
        elif tag.name == "td":
            tag["class"] = "px-4 py-3 text-sm text-zinc-300 border-b border-zinc-800/50"

    # Wrap tables in responsive glass container
    for table in soup.find_all("table"):
        if table.parent and table.parent.name != "div" or "overflow-x-auto" not in table.parent.get("class", []):
            wrapper = soup.new_tag("div", attrs={"class": "overflow-x-auto my-6 rounded-xl border border-zinc-800/80 glass-card-static"})
            table.wrap(wrapper)

    # Return body content string
    if soup.body:
        html_str = "".join(str(child) for child in soup.body.children).strip()
    else:
        html_str = str(soup).strip()

    return html_str

# 1. Clean restaurant JSON files
restaurant_files = [f for f in os.listdir(restaurants_dir) if f.endswith(".json") and f != "_index.json"]
cleaned_restaurants = 0

for fname in restaurant_files:
    fpath = os.path.join(restaurants_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "articleHtml" in data and data["articleHtml"]:
        page_title = data.get("name", "")
        data["articleHtml"] = clean_to_native_astro_html(data["articleHtml"], page_title)
        cleaned_restaurants += 1
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

print(f"[OK] Cleaned and converted native Astro article HTML in {cleaned_restaurants} restaurant JSON files.")

# 2. Clean food JSON files
food_files = [f for f in os.listdir(foods_dir) if f.endswith(".json")]
cleaned_foods = 0

for fname in food_files:
    fpath = os.path.join(foods_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "articleHtml" in data and data["articleHtml"]:
        page_title = data.get("name", "")
        data["articleHtml"] = clean_to_native_astro_html(data["articleHtml"], page_title)
        cleaned_foods += 1
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

# 3. Clean calculator registry.ts
registry_path = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\src\features\calculators\shared\registry.ts"

if os.path.exists(registry_path):
    with open(registry_path, "r", encoding="utf-8") as f:
        reg_content = f.read()

    # Match articleHtml: "..." or articleHtml: `...`
    def clean_reg_article(match):
        raw_json_str = match.group(1)
        try:
            raw_html = json.loads(raw_json_str)
            clean_astro_html = clean_to_native_astro_html(raw_html)
            return f"articleHtml: {json.dumps(clean_astro_html)}"
        except Exception:
            return match.group(0)

    updated_reg = re.sub(r'articleHtml:\s*("(?:\\.|[^"\\])*")', clean_reg_article, reg_content)
    with open(registry_path, "w", encoding="utf-8") as f:
        f.write(updated_reg)
    print("[OK] Cleaned and converted native Astro article HTML in health calculator registry.ts.")

print("==================================================")

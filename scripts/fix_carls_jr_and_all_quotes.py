import os
import json
import re
from bs4 import BeautifulSoup
from clean_and_native_articles import clean_to_native_astro_html

extracted_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\extracted_articles"
restaurants_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\src\data\restaurants"

print("==================================================")
print("FIXING CARL'S JR & QUOTE VARIATION MATCHING")
print("==================================================")

def normalize(text):
    return text.lower().replace("’", "'").replace("`", "'").replace("“", '"').replace("”", '"').strip()

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

for fname, data in extracted_files.items():
    if "carl" in fname.lower():
        print(f"Candidate file: {fname} -> text_len: {data['text_len']}")

# Fix Carl's Jr
carls_json_path = os.path.join(restaurants_dir, "carls-jr-calories-calculator.json")
if os.path.exists(carls_json_path):
    with open(carls_json_path, "r", encoding="utf-8") as f:
        cdata = json.load(f)

    # Find longest carls jr file
    carls_candidates = [v for k, v in extracted_files.items() if "carl" in k.lower()]
    carls_candidates.sort(key=lambda x: x["text_len"], reverse=True)

    if carls_candidates:
        best_carls = carls_candidates[0]
        cleaned_html = clean_to_native_astro_html(best_carls["content"], "Carl's Jr.")
        cdata["articleHtml"] = cleaned_html
        with open(carls_json_path, "w", encoding="utf-8") as f:
            json.dump(cdata, f, indent=2)
        print(f"\n[SUCCESS] Injected full article into Carl's Jr. ({best_carls['text_len']} chars)")

print("==================================================")

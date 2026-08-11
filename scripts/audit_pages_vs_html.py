import os
import re
from bs4 import BeautifulSoup

workspace_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website"
pages_dir = os.path.join(workspace_dir, "src", "pages")
extracted_dir = os.path.join(workspace_dir, "extracted_articles")

# 1. Discover all Astro pages in src/pages/
website_pages = []
for root, dirs, files in os.walk(pages_dir):
    for f in files:
        if f.endswith(".astro"):
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, pages_dir).replace("\\", "/")
            
            # Read title / description / headings from astro file if present
            with open(full_p, "r", encoding="utf-8") as file:
                content = file.read()
            
            # Match title in Astro component or schema
            title_match = re.search(r'title\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE) or \
                          re.search(r'pageTitle\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE) or \
                          re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
            
            title = title_match.group(1).strip() if title_match else f
            
            # Route path
            route = "/" + rel_p.replace("/index.astro", "").replace(".astro", "")
            if route == "/index":
                route = "/"

            website_pages.append({
                "rel_path": rel_p,
                "route": route,
                "title": title,
                "raw_file": f
            })

# 2. Discover all extracted HTML articles
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
    
    extracted_htmls.append({
        "filename": fname,
        "title_tag": title_tag,
        "clean_title": clean_title,
        "h1_text": h1_text
    })

print(f"Total Website Pages found in src/pages: {len(website_pages)}")
print(f"Total Extracted HTML files found: {len(extracted_htmls)}")

# Helper for string similarity / matching
def normalize(s):
    s = re.sub(r'nutrition calculator|calculator|nutrition facts|calories|nutrition|&|and|\b\w{1,2}\b', '', s, flags=re.IGNORECASE)
    return re.sub(r'[^a-z0-9]', '', s.lower())

matched_pages = [] # (page, html)
unmatched_pages = [] # pages without HTML
used_html_files = set()

for page in website_pages:
    p_norm = normalize(page["route"] + " " + page["title"])
    best_match = None
    best_score = 0
    
    for html_item in extracted_htmls:
        h_norm = normalize(html_item["filename"] + " " + html_item["clean_title"] + " " + html_item["h1_text"])
        
        # Check direct keyword match
        if p_norm and h_norm:
            if p_norm in h_norm or h_norm in p_norm:
                best_match = html_item
                used_html_files.add(html_item["filename"])
                break
    
    if best_match:
        matched_pages.append((page, best_match))
    else:
        unmatched_pages.append(page)

unmatched_htmls = [h for h in extracted_htmls if h["filename"] not in used_html_files]

print(f"\nMatched Pages: {len(matched_pages)}")
print(f"Unmatched Pages in Website: {len(unmatched_pages)}")
print(f"Unmatched HTML Files (Extracted articles without dedicated page): {len(unmatched_htmls)}")

print("\n--- SAMPLE MATCHES ---")
for p, h in matched_pages[:15]:
    print(f"PAGE: [{p['route']}] ({p['title'][:40]}) <---> HTML: '{h['filename']}'")

print("\n--- UNMATCHED WEBSITE PAGES (MISSING HTML CONTENT) ---")
for p in unmatched_pages[:20]:
    print(f"- Route: [{p['route']}] (File: {p['rel_path']})")

print("\n--- UNMATCHED HTML ARTICLES (NEW CONTENT THAT CAN BE CREATED AS PAGES) ---")
for h in unmatched_htmls[:20]:
    print(f"- HTML File: '{h['filename']}' (Title: {h['clean_title'][:50]})")

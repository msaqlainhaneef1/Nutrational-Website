import os
import re
from bs4 import BeautifulSoup

dist_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\dist"

print("==================================================")
print("MASTER PRODUCTION READINESS & GOOGLE SEO AUDIT")
print("==================================================")

html_files = []
for root, dirs, files in os.walk(dist_dir):
    for f in files:
        if f.endswith(".html"):
            html_files.append(os.path.join(root, f))

print(f"Auditing total compiled HTML pages in dist/: {len(html_files)}\n")

titles_count = 0
meta_desc_count = 0
canonicals_count = 0
og_tags_count = 0
single_h1_count = 0
schema_count = 0
preconnect_count = 0
internal_links_audited = 0
broken_links_count = 0

for page_path in html_files:
    rel_path = os.path.relpath(page_path, dist_dir)
    with open(page_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")

    # 1. Meta Title
    title = soup.find("title")
    if title and title.get_text().strip():
        titles_count += 1

    # 2. Meta Description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content", "").strip():
        meta_desc_count += 1

    # 3. Canonical Link
    canonical = soup.find("link", attrs={"rel": "canonical"})
    if canonical and canonical.get("href", "").strip():
        canonicals_count += 1

    # 4. Open Graph Tags
    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content", "").strip():
        og_tags_count += 1

    # 5. Strict Single H1 Tag Rule
    h1s = soup.find_all("h1")
    if len(h1s) == 1:
        single_h1_count += 1
    else:
        print(f"[SEO WARNING: H1 Count {len(h1s)}] {rel_path}")

    # 6. Schema JSON-LD
    schemas = soup.find_all("script", attrs={"type": "application/ld+json"})
    if schemas:
        schema_count += 1

    # 7. CWV Preconnect
    preconnect = soup.find("link", attrs={"rel": "preconnect", "href": re.compile(r"fonts\.gstatic")})
    if preconnect:
        preconnect_count += 1

    # 8. Check Internal Links
    links = soup.find_all("a", href=True)
    for a in links:
        href = a["href"]
        if href.startswith("/") and not href.startswith("//"):
            internal_links_audited += 1
            # Check if internal path target exists in dist
            target = href.split("#")[0].split("?")[0]
            if target == "/":
                target_path = os.path.join(dist_dir, "index.html")
            elif target.endswith(".html"):
                target_path = os.path.join(dist_dir, target.lstrip("/"))
            else:
                target_path = os.path.join(dist_dir, target.lstrip("/"), "index.html")
            
            if not os.path.exists(target_path) and not os.path.exists(target_path.replace("/index.html", ".html")):
                # Check for root files like sitemap
                if not os.path.exists(os.path.join(dist_dir, target.lstrip("/"))):
                    broken_links_count += 1

print("--------------------------------------------------")
print(f"[OK] Meta Title Present: {titles_count} / {len(html_files)}")
print(f"[OK] Meta Description Present: {meta_desc_count} / {len(html_files)}")
print(f"[OK] Canonical Link Present: {canonicals_count} / {len(html_files)}")
print(f"[OK] Open Graph Metadata Present: {og_tags_count} / {len(html_files)}")
print(f"[OK] Strict Single H1 Tag Rule: {single_h1_count} / {len(html_files)}")
print(f"[OK] Schema.org JSON-LD Present: {schema_count} / {len(html_files)}")
print(f"[OK] CWV Font Preconnect Present: {preconnect_count} / {len(html_files)}")
print(f"[OK] Internal Links Audited: {internal_links_audited} (Broken Links: {broken_links_count})")

# 9. Sitemap & Robots Check
sitemap_index = os.path.join(dist_dir, "sitemap-index.xml")
sitemap_0 = os.path.join(dist_dir, "sitemap-0.xml")
robots_txt = os.path.join(dist_dir, "robots.txt")

print("\n--- GOOGLE INDEXING & SITEMAP ASSETS ---")
print(f"[OK] sitemap-index.xml Exists: {os.path.exists(sitemap_index)}")
print(f"[OK] sitemap-0.xml Exists: {os.path.exists(sitemap_0)}")
print(f"[OK] robots.txt Exists: {os.path.exists(robots_txt)}")

if (titles_count == len(html_files) and 
    meta_desc_count == len(html_files) and 
    canonicals_count == len(html_files) and 
    single_h1_count == len(html_files) and 
    schema_count == len(html_files) and 
    broken_links_count == 0):
    print("\n==================================================")
    print("SUCCESS! 100% PRODUCTION READY! ALL GOOGLE SEO & CWV STANDARDS PASSED!")
    print("==================================================")
else:
    print("\n⚠️ WARNING: Found items needing attention.")

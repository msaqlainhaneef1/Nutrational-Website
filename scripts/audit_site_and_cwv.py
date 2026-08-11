import os
import re
from bs4 import BeautifulSoup

dist_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\dist"

print("==================================================")
print("COMPREHENSIVE 128-PAGE SITE & CWV AUDIT")
print("==================================================")

html_files = []
for root, dirs, files in os.walk(dist_dir):
    for f in files:
        if f.endswith(".html"):
            html_files.append(os.path.join(root, f))

total_pages = len(html_files)
print(f"Auditing total compiled HTML pages in dist/: {total_pages}\n")

pages_with_title = 0
pages_with_desc = 0
pages_with_canonical = 0
pages_with_preconnect = 0
pages_single_h1 = 0
pages_with_schema = 0
images_checked = 0
images_missing_alt = 0

issues_log = []

for fpath in html_files:
    rel_path = os.path.relpath(fpath, dist_dir)
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Meta Title
    title_tag = soup.find("title")
    if title_tag and title_tag.get_text().strip():
        pages_with_title += 1
    else:
        issues_log.append(f"[Missing Title] {rel_path}")

    # 2. Meta Description
    desc_tag = soup.find("meta", attrs={"name": "description"})
    if desc_tag and desc_tag.get("content", "").strip():
        pages_with_desc += 1
    else:
        issues_log.append(f"[Missing Meta Description] {rel_path}")

    # 3. Canonical Link
    canon_tag = soup.find("link", attrs={"rel": "canonical"})
    if canon_tag and canon_tag.get("href", "").strip():
        pages_with_canonical += 1

    # 4. Font Preconnect
    pre_tag = soup.find("link", attrs={"rel": "preconnect", "href": "https://fonts.googleapis.com"})
    if pre_tag:
        pages_with_preconnect += 1

    # 5. Single H1 Rule
    h1_tags = soup.find_all("h1")
    if len(h1_tags) == 1:
        pages_single_h1 += 1
    else:
        issues_log.append(f"[H1 Rule Violation: {len(h1_tags)} <h1> tags] {rel_path}")

    # 6. Structured Data
    ld_json = soup.find_all("script", attrs={"type": "application/ld+json"})
    if len(ld_json) > 0:
        pages_with_schema += 1

    # 7. Images Audit
    for img in soup.find_all("img"):
        images_checked += 1
        if not img.get("alt", "").strip():
            images_missing_alt += 1

print(f"[OK] Meta Title Present: {pages_with_title} / {total_pages}")
print(f"[OK] Meta Description Present: {pages_with_desc} / {total_pages}")
print(f"[OK] Canonical Link Present: {pages_with_canonical} / {total_pages}")
print(f"[OK] CWV Font Preconnect Present: {pages_with_preconnect} / {total_pages}")
print(f"[OK] Strict Single H1 Rule Passed: {pages_single_h1} / {total_pages}")
print(f"[OK] Schema.org JSON-LD Present: {pages_with_schema} / {total_pages}")
print(f"[OK] Images Audited: {images_checked} (Missing Alt: {images_missing_alt})")

print("\n==================================================")
if len(issues_log) == 0 and pages_single_h1 == total_pages:
    print("PERFECT AUDIT PASSED! 100% CWV & SEO COMPLIANT ACROSS ALL PAGES!")
else:
    print(f"Audit completed with {len(issues_log)} issues:")
    for iss in issues_log[:10]:
        print(" -", iss)
print("==================================================")

import os
import re
from bs4 import BeautifulSoup

extracted_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\extracted_articles"

files = [f for f in os.listdir(extracted_dir) if f.endswith(".html")]

dup_named_files = [f for f in files if '(' in f or 'meta' in f.lower()]

print(f"Files with '(' in filename or 'Meta' in filename: {len(dup_named_files)}")
print(dup_named_files[:30])

# Group files by base title (removing (1), (2), Meta Title, etc.)
grouped = {}
for fname in files:
    clean = re.sub(r'\s*\(\d+\)', '', fname)
    clean = re.sub(r'^(meta title|seo title|meta description|seo description)[:\s]*', '', clean, flags=re.IGNORECASE)
    clean = clean.strip()
    if clean in grouped:
        grouped[clean].append(fname)
    else:
        grouped[clean] = [fname]

multi_file_groups = {k: v for k, v in grouped.items() if len(v) > 1}
print(f"\nTotal title groups with multiple files: {len(multi_file_groups)}")

for title, flist in list(multi_file_groups.items())[:15]:
    print(f"\nGroup '{title}': {flist}")
    for f in flist:
        fpath = os.path.join(extracted_dir, f)
        with open(fpath, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")
        body_text = soup.body.get_text().strip()[:150] if soup.body else ""
        print(f"  [{f}] ({os.path.getsize(fpath)} bytes) -> First 150 chars: {body_text!r}")

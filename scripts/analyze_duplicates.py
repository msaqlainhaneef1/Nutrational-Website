import os
import hashlib
import re
from bs4 import BeautifulSoup

extracted_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\extracted_articles"

files = [f for f in os.listdir(extracted_dir) if f.endswith(".html")]
print(f"Total HTML files before deduplication: {len(files)}")

hashes = {} # hash -> list of filenames
dup_groups = []

def get_body_text_hash(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    # Get normalized body text (strip tags, extra spaces)
    body = soup.body
    if not body:
        text = html
    else:
        text = body.get_text()
    # Normalize whitespace
    text_norm = re.sub(r'\s+', ' ', text).strip().lower()
    return hashlib.sha256(text_norm.encode('utf-8')).hexdigest(), text_norm

for fname in files:
    fpath = os.path.join(extracted_dir, fname)
    h, norm_text = get_body_text_hash(fpath)
    if h in hashes:
        hashes[h].append(fname)
    else:
        hashes[h] = [fname]

duplicates_to_delete = []
unique_kept = []

for h, flist in hashes.items():
    if len(flist) > 1:
        # Sort to keep the cleanest name (without "(1)" or shorter name first)
        flist_sorted = sorted(flist, key=lambda x: (1 if '(' in x else 0, len(x), x))
        keep = flist_sorted[0]
        delete = flist_sorted[1:]
        unique_kept.append(keep)
        duplicates_to_delete.extend(delete)
        dup_groups.append((keep, delete))
    else:
        unique_kept.append(flist[0])

print(f"Unique articles count: {len(unique_kept)}")
print(f"Duplicates identified for deletion: {len(duplicates_to_delete)}")
print("\n--- SAMPLE DUPLICATE GROUPS ---")
for keep, del_list in dup_groups[:10]:
    print(f"KEEP: '{keep}'")
    print(f"  DELETE: {del_list}")


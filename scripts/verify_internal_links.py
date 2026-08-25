import os
import glob
import re
from urllib.parse import urlparse, unquote

dist_dir = 'dist'
html_files = glob.glob(os.path.join(dist_dir, '**', '*.html'), recursive=True)

print(f"Total HTML files generated in dist/: {len(html_files)}")

# Map each file to its canonical URL path
file_to_url = {}
url_to_file = {}

for fpath in html_files:
    rel = os.path.relpath(fpath, dist_dir).replace('\\', '/')
    if rel == 'index.html':
        url_path = '/'
    elif rel.endswith('/index.html'):
        url_path = '/' + rel[:-11]
    elif rel.endswith('.html'):
        url_path = '/' + rel[:-5]
    else:
        url_path = '/' + rel
        
    file_to_url[fpath] = url_path
    url_to_file[url_path] = fpath

outbound_links = {url: set() for url in url_to_file}
inbound_links = {url: set() for url in url_to_file}

link_pattern = re.compile(r'<a\s+[^>]*href=["\']([^"\']+)["\']', re.IGNORECASE)

for fpath, from_url in file_to_url.items():
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    matches = link_pattern.findall(content)
    for target in matches:
        if target.startswith('#') or target.startswith('mailto:') or target.startswith('tel:') or target.startswith('javascript:'):
            continue
            
        parsed = urlparse(target)
        if parsed.scheme and not target.startswith('/'):
            continue  # external link
            
        clean_target = parsed.path
        if not clean_target:
            clean_target = '/'
        elif clean_target != '/' and clean_target.endswith('/'):
            clean_target = clean_target[:-1]
            
        clean_target = unquote(clean_target)
        
        # Check if target matches any valid page
        matched_url = None
        if clean_target in url_to_file:
            matched_url = clean_target
        elif clean_target + '/index' in url_to_file:
            matched_url = clean_target + '/index'
        elif clean_target.endswith('/index') and clean_target[:-6] in url_to_file:
            matched_url = clean_target[:-6]
            
        if matched_url:
            outbound_links[from_url].add(matched_url)
            inbound_links[matched_url].add(from_url)

# Orphan analysis
orphan_inbound = [url for url, links in inbound_links.items() if len(links) == 0 and url != '/404']
orphan_outbound = [url for url, links in outbound_links.items() if len(links) == 0 and url != '/404']

outbound_counts = [len(links) for url, links in outbound_links.items() if url != '/404']
inbound_counts = [len(links) for url, links in inbound_links.items() if url != '/404']

print("\n--- Internal Link Graph Health Report ---")
print(f"Total Evaluated Pages: {len(outbound_counts)}")
print(f"Orphan Pages (0 Incoming Links): {len(orphan_inbound)} -> {orphan_inbound}")
print(f"Dead-End Pages (0 Outgoing Links): {len(orphan_outbound)} -> {orphan_outbound}")
print(f"Average Outbound Links per Page: {sum(outbound_counts)/len(outbound_counts):.1f}")
print(f"Min Outbound Links: {min(outbound_counts)}, Max: {max(outbound_counts)}")
print(f"Average Inbound Links per Page: {sum(inbound_counts)/len(inbound_counts):.1f}")
print(f"Min Inbound Links: {min(inbound_counts)}, Max: {max(inbound_counts)}")

print("\nSample Restaurant Link Stats:")
for sample_url in ['/restaurants/pizza-hut-nutrition-calculator', '/restaurants/kfc-nutrition-calculator', '/restaurants/olive-garden-nutrition-calculator', '/calculators/tdee', '/calculators/calorie-deficit']:
    if sample_url in outbound_links:
        print(f"  {sample_url}: {len(outbound_links[sample_url])} outbound links, {len(inbound_links[sample_url])} inbound links")

import os
import re
from bs4 import BeautifulSoup

extracted_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\extracted_articles"
html_files = [f for f in os.listdir(extracted_dir) if f.endswith(".html")]

print(f"Applying professional CSS design system to {len(html_files)} HTML files...")

processed = 0

for fname in html_files:
    fpath = os.path.join(extracted_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")

    # 1. Head setup
    head = soup.head
    if not head:
        head = soup.new_tag("head")
        if soup.html:
            soup.html.insert(0, head)
        else:
            soup.insert(0, head)

    # Ensure meta charset
    if not head.find("meta", charset=True):
        m_char = soup.new_tag("meta", attrs={"charset": "UTF-8"})
        head.insert(0, m_char)

    # Ensure viewport
    if not head.find("meta", attrs={"name": "viewport"}):
        m_vp = soup.new_tag("meta", attrs={"name": "viewport", "content": "width=device-width, initial-scale=1.0"})
        head.append(m_vp)

    # Remove inline old doc styles
    for old_style in head.find_all("style"):
        old_style.decompose()

    # Link article_styles.css
    css_link = head.find("link", attrs={"href": "article_styles.css"})
    if not css_link:
        new_link = soup.new_tag("link", attrs={"rel": "stylesheet", "href": "article_styles.css"})
        head.append(new_link)

    # 2. Body & Container setup
    body = soup.body
    if not body:
        continue

    # Clean existing main or wrappers if re-running
    existing_main = body.find("main")
    if existing_main:
        # Extract children out of main
        main_children = list(existing_main.children)
        existing_main.unwrap()

    # Wrap all body contents in main.article-container
    container = soup.new_tag("main", attrs={"class": "article-container"})
    body_children = list(body.children)
    for child in body_children:
        container.append(child)
    body.append(container)

    # 3. Meta info box grouping
    meta_paras = []
    for p in container.find_all("p"):
        p_text = p.get_text().strip()
        if any(p_text.startswith(prefix) for prefix in ["Meta Title:", "SEO Title:", "Meta Description:", "SEO Description:", "Page Title:"]):
            meta_paras.append(p)

    if meta_paras:
        card = soup.new_tag("div", attrs={"class": "meta-info-card"})
        meta_paras[0].insert_before(card)
        for mp in meta_paras:
            card.append(mp)

    # 4. Table responsive wrappers
    for tbl in container.find_all("table"):
        wrapper = soup.new_tag("div", attrs={"class": "table-responsive"})
        tbl.insert_before(wrapper)
        wrapper.append(tbl)

    # Save output HTML
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(str(soup.prettify()))

    processed += 1

print(f"\n==================================================")
print(f"SUCCESSFULLY APPLIED DESIGN SYSTEM TO {processed} HTML FILES")
print(f"==================================================")

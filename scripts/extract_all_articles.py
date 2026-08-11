import os
import re
import html as html_lib
from bs4 import BeautifulSoup, NavigableString

# Input and output paths
workspace_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website"
scratch_dir = r"C:\Users\Saqlain\.gemini\antigravity-ide\brain\6e8a3b57-b474-491e-bd79-63c922ed230a\scratch"
output_dir = os.path.join(workspace_dir, "extracted_articles")

os.makedirs(output_dir, exist_ok=True)

doc1_path = os.path.join(scratch_dir, "doc1.html")
doc2_path = os.path.join(scratch_dir, "doc2.html")

def sanitize_filename(title):
    # Strip any prefix like Meta Title, Meta Description, etc if present
    title = re.sub(r'^(Meta Title|SEO Title|Meta Description|SEO Description|Page Title)[:\s]*', '', title, flags=re.IGNORECASE)
    # Remove invalid Windows filename characters: \ / : * ? " < > |
    clean = re.sub(r'[\\/:*?"<>|\t\n\r]', ' ', title)
    clean = re.sub(r'\s+', ' ', clean).strip()
    clean = clean.strip('. ')
    if not clean:
        clean = "Untitled_Article"
    return clean[:100] # Safe length for Windows path limits

def process_document(doc_name, file_path):
    print(f"\n==================================================")
    print(f"Processing {doc_name} -> {file_path}")
    print(f"==================================================")
    
    with open(file_path, "r", encoding="utf-8") as f:
        full_html = f.read()

    soup = BeautifulSoup(full_html, "html.parser")
    
    # Extract head styles
    head_style = ""
    style_tags = soup.head.find_all("style") if soup.head else []
    for st in style_tags:
        head_style += str(st) + "\n"

    body = soup.body
    if not body:
        print(f"Error: No body tag in {doc_name}")
        return 0

    body_children = [c for c in body.children if not isinstance(c, NavigableString) or c.strip()]

    articles = []
    current_elements = []
    current_title = ""

    def is_title_node(elem):
        if not elem.name:
            return False, ""
        text = elem.get_text().strip()
        classes = elem.get("class", [])
        
        # Check if element has "title" class or is h1 tag
        if "title" in classes or elem.name == "h1":
            if text and not any(text.startswith(prefix) for prefix in ["Meta Title:", "SEO Title:", "Page Title:", "Meta Description:", "SEO Description:"]):
                return True, text
        return False, ""

    for elem in body_children:
        is_title, t_text = is_title_node(elem)
        if is_title and current_elements:
            articles.append({
                "title": current_title,
                "elements": current_elements
            })
            current_elements = [elem]
            current_title = t_text
        else:
            if not current_title and is_title:
                current_title = t_text
            current_elements.append(elem)

    if current_elements:
        articles.append({
            "title": current_title,
            "elements": current_elements
        })

    saved_count = 0
    seen_filenames = set()

    for idx, art in enumerate(articles):
        elements = art["elements"]
        title_text = art["title"].strip()

        # Fallback to first non-empty text if title was missing
        if not title_text or any(title_text.startswith(p) for p in ["Meta Title:", "SEO Title:", "Meta Description:", "SEO Description:"]):
            for e in elements:
                t = e.get_text().strip()
                if t and not any(t.startswith(p) for p in ["Meta Title:", "SEO Title:", "Meta Description:", "SEO Description:"]):
                    title_text = t
                    break
        if not title_text:
            title_text = f"Article_{idx+1}"

        base_fname = sanitize_filename(title_text)
        fname = base_fname
        counter = 1
        while fname.lower() in seen_filenames:
            fname = f"{base_fname} ({counter})"
            counter += 1
        seen_filenames.add(fname.lower())

        out_filepath = os.path.join(output_dir, f"{fname}.html")

        # Build full standalone HTML string
        body_inner_html = "".join(str(e) for e in elements)
        
        article_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_lib.escape(title_text)}</title>
{head_style}
</head>
<body>
{body_inner_html}
</body>
</html>
"""
        with open(out_filepath, "w", encoding="utf-8") as out_f:
            out_f.write(article_html)

        saved_count += 1

    print(f"Successfully extracted {saved_count} articles from {doc_name}.")
    return saved_count

tot1 = process_document("Doc 1", doc1_path)
tot2 = process_document("Doc 2", doc2_path)
print(f"\n==================================================")
print(f"TOTAL ARTICLES SAVED: {tot1 + tot2} HTML files into '{output_dir}'")
print(f"==================================================")

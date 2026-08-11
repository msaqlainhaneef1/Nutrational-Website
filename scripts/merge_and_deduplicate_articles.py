import os
import re
import html as html_lib
from bs4 import BeautifulSoup, NavigableString

workspace_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website"
scratch_dir = r"C:\Users\Saqlain\.gemini\antigravity-ide\brain\6e8a3b57-b474-491e-bd79-63c922ed230a\scratch"
output_dir = os.path.join(workspace_dir, "extracted_articles")

doc1_path = os.path.join(scratch_dir, "doc1.html")
doc2_path = os.path.join(scratch_dir, "doc2.html")

def sanitize_filename(title):
    # Strip Meta Title / SEO Title / etc prefix
    title = re.sub(r'^(Meta Title|SEO Title|Meta Description|SEO Description|Page Title)[:\s]*', '', title, flags=re.IGNORECASE)
    # Remove invalid Windows filename characters: \ / : * ? " < > |
    clean = re.sub(r'[\\/:*?"<>|\t\n\r]', ' ', title)
    clean = re.sub(r'\s+', ' ', clean).strip()
    clean = clean.strip('. ')
    if not clean:
        clean = "Untitled_Article"
    return clean[:100]

def extract_and_merge_articles(doc_name, file_path):
    print(f"\n==================================================")
    print(f"Extracting & Merging {doc_name}")
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
        return []

    body_children = [c for c in body.children if not isinstance(c, NavigableString) or c.strip()]

    articles = []
    current_elements = []
    current_title = ""

    def get_element_text(elem):
        if not elem or not elem.name:
            return ""
        return elem.get_text().strip()

    for elem in body_children:
        text = get_element_text(elem)
        classes = elem.get("class", []) if elem.name else []

        # An article boundary starts when we see a title class or H1 element that is an article title
        # (NOT a Meta Title / SEO Title paragraph)
        is_title_class_or_h1 = ("title" in classes or elem.name == "h1")
        is_meta_tag = any(text.startswith(prefix) for prefix in ["Meta Title:", "SEO Title:", "Page Title:", "Meta Description:", "SEO Description:"])

        if is_title_class_or_h1 and not is_meta_tag:
            # Check if current_elements already has content
            if current_elements and len(current_elements) > 1:
                articles.append({
                    "title": current_title,
                    "elements": current_elements
                })
                current_elements = [elem]
                current_title = text
            else:
                # If current_elements only had meta tags or 1 title, attach to this article
                if not current_title:
                    current_title = text
                current_elements.append(elem)
        else:
            if not current_title and is_title_class_or_h1 and not is_meta_tag:
                current_title = text
            current_elements.append(elem)

    if current_elements:
        articles.append({
            "title": current_title,
            "elements": current_elements
        })

    # Post-process articles: merge articles that belong to the same article title
    # (e.g. Meta Title stub + Article Body)
    merged_map = {}
    for art in articles:
        title_text = art["title"].strip()
        
        # If title_text is missing or is a meta tag, find real H1 or Title inside elements
        if not title_text or any(title_text.startswith(p) for p in ["Meta Title:", "SEO Title:", "Meta Description:", "SEO Description:"]):
            for e in art["elements"]:
                txt = get_element_text(e)
                if txt and not any(txt.startswith(p) for p in ["Meta Title:", "SEO Title:", "Meta Description:", "SEO Description:"]):
                    title_text = txt
                    break
        
        if not title_text:
            continue

        clean_name = sanitize_filename(title_text)
        if clean_name in merged_map:
            merged_map[clean_name]["elements"].extend(art["elements"])
        else:
            merged_map[clean_name] = {
                "title": title_text,
                "elements": art["elements"]
            }

    results = []
    for clean_name, data in merged_map.items():
        results.append({
            "clean_title": clean_name,
            "display_title": data["title"],
            "elements": data["elements"],
            "head_style": head_style
        })

    print(f"Found {len(results)} merged complete articles in {doc_name}.")
    return results

def main():
    doc1_articles = extract_and_merge_articles("Doc 1", doc1_path)
    doc2_articles = extract_and_merge_articles("Doc 2", doc2_path)

    all_articles = doc1_articles + doc2_articles
    print(f"\nTotal Merged Articles: {len(all_articles)}")

    # Clear existing extracted_articles folder
    for f in os.listdir(output_dir):
        if f.endswith(".html"):
            os.remove(os.path.join(output_dir, f))

    saved_count = 0
    seen_names = set()

    for art in all_articles:
        base_name = art["clean_title"]
        fname = base_name
        counter = 1
        while fname.lower() in seen_names:
            fname = f"{base_name} ({counter})"
            counter += 1
        seen_names.add(fname.lower())

        out_path = os.path.join(output_dir, f"{fname}.html")
        body_html = "".join(str(e) for e in art["elements"])

        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_lib.escape(art['display_title'])}</title>
{art['head_style']}
</head>
<body>
{body_html}
</body>
</html>
"""
        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write(html_doc)

        saved_count += 1

    print(f"\n==================================================")
    print(f"SUCCESSFULLY SAVED {saved_count} UNIQUE HTML ARTICLES INTO '{output_dir}'")
    print(f"==================================================")

if __name__ == "__main__":
    main()

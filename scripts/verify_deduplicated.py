import os
from bs4 import BeautifulSoup

extracted_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\extracted_articles"

files = [f for f in os.listdir(extracted_dir) if f.endswith(".html")]
print(f"Total Unique HTML files in extracted_articles: {len(files)}")

files_with_paren = [f for f in files if '(' in f]
print(f"Files with '(' suffix remaining: {len(files_with_paren)}")
if files_with_paren:
    print("  List:", files_with_paren)

print("\n--- SAMPLE FILE CONTENT & STRUCTURE VERIFICATION ---")
sample_names = [
    "Sonic Drive-In Nutrition Calculator.html",
    "BMI Calculator Calculate Your Body Mass Index.html",
    "Apple Nutrition Facts.html",
    "Starbucks Nutrition Calculator.html",
    "Chipotle Nutrition Calculator.html",
    "Avocado Nutrition Facts.html"
]

for sname in sample_names:
    matching = [f for f in files if sname.lower() == f.lower()]
    if matching:
        target = matching[0]
        tpath = os.path.join(extracted_dir, target)
        size = os.path.getsize(tpath)
        with open(tpath, "r", encoding="utf-8") as tf:
            content = tf.read()
        soup = BeautifulSoup(content, "html.parser")
        h1 = soup.find("h1") or soup.find(class_="title")
        paras = soup.find_all("p")
        headings = soup.find_all(["h1", "h2", "h3"])

        # Check meta title inside text
        has_meta_title = "Meta Title:" in content or "SEO Title:" in content
        has_meta_desc = "Meta Description:" in content or "SEO Description:" in content

        print(f"\nFile: '{target}' ({size} bytes)")
        print(f"  Title tag: {soup.title.string if soup.title else 'None'}")
        print(f"  Main Header H1: {h1.get_text().strip() if h1 else 'None'}")
        print(f"  Has Meta Title: {has_meta_title}, Has Meta Description: {has_meta_desc}")
        print(f"  Total Headings: {len(headings)}, Total Paragraphs: {len(paras)}")
        if paras:
            p_text = paras[0].get_text().strip()[:100]
            print(f"  First paragraph: {p_text!r}")
    else:
        print(f"Sample '{sname}' not found!")


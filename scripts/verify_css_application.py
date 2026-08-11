import os
from bs4 import BeautifulSoup

extracted_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\extracted_articles"

html_files = [f for f in os.listdir(extracted_dir) if f.endswith(".html")]

print(f"Verifying {len(html_files)} HTML files for CSS design system integration...")

valid_count = 0
has_css_link_count = 0
has_container_count = 0
has_meta_card_count = 0
has_table_wrapper_count = 0

sample_files = [
    "Sonic Drive-In Nutrition Calculator.html",
    "BMI Calculator Calculate Your Body Mass Index.html",
    "Apple Nutrition Facts.html",
    "Starbucks Nutrition Calculator.html",
    "Chipotle Nutrition Calculator.html"
]

for fname in html_files:
    fpath = os.path.join(extracted_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    css_link = soup.find("link", href="article_styles.css")
    container = soup.find("main", class_="article-container")
    meta_card = soup.find("div", class_="meta-info-card")
    tbl_wrapper = soup.find("div", class_="table-responsive")

    if css_link:
        has_css_link_count += 1
    if container:
        has_container_count += 1
    if meta_card:
        has_meta_card_count += 1
    if tbl_wrapper:
        has_table_wrapper_count += 1

print("\n--- VERIFICATION SUMMARY ---")
print(f"Total HTML Files: {len(html_files)}")
print(f"Files with article_styles.css linked: {has_css_link_count} / {len(html_files)}")
print(f"Files with <main class='article-container'> wrapper: {has_container_count} / {len(html_files)}")
print(f"Files with <div class='meta-info-card'> meta box: {has_meta_card_count}")
print(f"Files with <div class='table-responsive'> table wrapper: {has_table_wrapper_count}")

print("\n--- SAMPLE FILE INSPECTION ---")
for sname in sample_files:
    fpath = os.path.join(extracted_dir, sname)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        h1 = soup.find("h1")
        m_card = soup.find("div", class_="meta-info-card")
        t_wrap = soup.find("div", class_="table-responsive")
        print(f"\nFile: '{sname}'")
        print(f"  H1 Title: {h1.get_text().strip() if h1 else 'None'}")
        print(f"  Meta Card Present: {bool(m_card)}")
        print(f"  Table Responsive Wrapper Present: {bool(t_wrap)}")


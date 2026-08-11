import os
from bs4 import BeautifulSoup

extracted_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\extracted_articles"

files = [f for f in os.listdir(extracted_dir) if f.endswith(".html")]
print(f"Total HTML files generated in extracted_articles: {len(files)}")

invalid_files = []
total_bytes = 0

sample_files = [
    "Sonic Drive-In Nutrition Calculator.html",
    "BMI Calculator Calculate Your Body Mass Index.html",
    "Apple Nutrition Facts.html",
    "Starbucks Nutrition Calculator.html",
    "Chipotle Nutrition Calculator.html"
]

for fname in files:
    fpath = os.path.join(extracted_dir, fname)
    size = os.path.getsize(fpath)
    total_bytes += size
    if size < 500:
        invalid_files.append((fname, size))

print(f"Total size of all extracted articles: {total_bytes / (1024*1024):.2f} MB")
print(f"Invalid / empty files count: {len(invalid_files)}")

print("\n--- SAMPLE FILE VERIFICATION ---")
for sname in sample_files:
    matching = [f for f in files if sname.lower() in f.lower() or f.lower().startswith(sname[:15].lower())]
    if matching:
        target = matching[0]
        tpath = os.path.join(extracted_dir, target)
        with open(tpath, "r", encoding="utf-8") as tf:
            content = tf.read()
        soup = BeautifulSoup(content, "html.parser")
        h1_title = soup.find("h1") or soup.find(class_="title")
        paras = soup.find_all("p")
        headings = soup.find_all(["h1", "h2", "h3"])
        print(f"\nFile: '{target}' ({os.path.getsize(tpath)} bytes)")
        print(f"  Title tag: {soup.title.string if soup.title else 'None'}")
        print(f"  Main Header: {h1_title.get_text().strip() if h1_title else 'None'}")
        print(f"  Headings count: {len(headings)}, Paragraphs count: {len(paras)}")
        first_p = paras[0].get_text().strip()[:100] if paras else 'None'
        print(f"  First paragraph text: {first_p!r}")
    else:
        print(f"Sample '{sname}' not found!")


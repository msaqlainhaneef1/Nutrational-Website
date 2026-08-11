import os
from bs4 import BeautifulSoup

extracted_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\extracted_articles"

f1 = os.path.join(extracted_dir, "Sonic Drive-In Nutrition Calculator.html")
f2 = os.path.join(extracted_dir, "Sonic Drive-In Nutrition Calculator (1).html")

with open(f1, "r", encoding="utf-8") as f:
    s1 = BeautifulSoup(f.read(), "html.parser").body.get_text()[:300].strip()

with open(f2, "r", encoding="utf-8") as f:
    s2 = BeautifulSoup(f.read(), "html.parser").body.get_text()[:300].strip()

print("Sonic 1:", s1)
print("\nSonic 2:", s2)

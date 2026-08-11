import os
from bs4 import BeautifulSoup

fpath = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\extracted_articles\Sonic Drive-In Nutrition Calculator.html"

with open(fpath, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

print("Body tag children count:", len(list(soup.body.children)))
print("First 3 elements in body:")
for child in list(soup.body.children)[:5]:
    if child.name:
        print(f"  <{child.name} class='{child.get('class')}'>")

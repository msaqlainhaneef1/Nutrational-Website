import os
import json
import re
from bs4 import BeautifulSoup

workspace_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website"
extracted_dir = os.path.join(workspace_dir, "extracted_articles")
registry_path = os.path.join(workspace_dir, "src", "features", "calculators", "shared", "registry.ts")

# Clean HTML for injection
def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # Remove meta p
    for p in soup.find_all("p"):
        txt = p.get_text().strip()
        if any(txt.startswith(prefix) for prefix in ["Meta Title:", "SEO Title:", "Meta Description:", "SEO Description:"]):
            p.decompose()

    # STRICT SEO RULE: Ensure ONLY ONE <h1> per page. Convert <h1> inside article to <h2>
    for h1 in soup.find_all("h1"):
        h2 = soup.new_tag("h2")
        h2.string = h1.get_text().strip()
        h2["class"] = "text-2xl md:text-3xl font-extrabold text-white mb-4 mt-8 flex items-center gap-2"
        h1.replace_with(h2)

    for h2 in soup.find_all("h2"):
        h2["class"] = "text-xl md:text-2xl font-bold text-emerald-400 mb-3 mt-6 border-b border-zinc-800 pb-2"

    for h3 in soup.find_all("h3"):
        h3["class"] = "text-lg font-semibold text-zinc-200 mb-2 mt-4"

    for tbl in soup.find_all("table"):
        tbl["class"] = "min-w-full text-left text-xs md:text-sm border-collapse"
        for th in tbl.find_all("th"):
          th["class"] = "bg-zinc-900 text-emerald-400 font-bold p-3 border-b border-zinc-800"
        for td in tbl.find_all("td"):
          td["class"] = "p-3 border-b border-zinc-900/60 text-zinc-300"
        
        if tbl.parent.name != "div" or "table-responsive" not in tbl.parent.get("class", []):
            wrapper = soup.new_tag("div", attrs={"class": "overflow-x-auto my-6 rounded-xl border border-zinc-800/80 bg-zinc-950/60 p-1"})
            tbl.insert_before(wrapper)
            wrapper.append(tbl)

    for p in soup.find_all("p"):
        p["class"] = "text-zinc-300 text-sm md:text-base leading-relaxed mb-4"

    for ul in soup.find_all("ul"):
        ul["class"] = "list-disc list-inside space-y-2 mb-4 text-zinc-300 text-sm md:text-base pl-2"
    for ol in soup.find_all("ol"):
        ol["class"] = "list-decimal list-inside space-y-2 mb-4 text-zinc-300 text-sm md:text-base pl-2"

    main_elem = soup.find("main")
    if main_elem:
        inner_html = "".join(str(c) for c in main_elem.children)
    else:
        body_elem = soup.find("body")
        inner_html = "".join(str(c) for c in body_elem.children) if body_elem else str(soup)

    return inner_html.strip()

calc_map = {
    "bmi": "BMI Calculator Calculate Your Body Mass Index.html",
    "bmr": "BMR Calculator Calculate Your Basal MetaboliC.html",
    "body-fat": "Body Fat Calculator Estimate Your Bo.html",
    "calorie-deficit": "Calorie Deficit Calculator.html",
    "ideal-weight": "Ideal Weight Calculator.html",
    "macro": "Macro Calculator.html",
    "protein": "Protein Calculator.html",
    "tdee": "TDEE Calculator.html",
    "water-intake": "Water Intake Calculator.html"
}

with open(registry_path, "r", encoding="utf-8") as rf:
    registry_code = rf.read()

injected_count = 0

for slug, html_filename in calc_map.items():
    hpath = os.path.join(extracted_dir, html_filename)
    if os.path.exists(hpath):
        with open(hpath, "r", encoding="utf-8") as hf:
            cleaned_html = clean_html(hf.read())
        
        target_str = f"slug: '{slug}',"
        replacement_str = f"slug: '{slug}',\n    articleHtml: {json.dumps(cleaned_html)},"
        if target_str in registry_code:
            registry_code = registry_code.replace(target_str, replacement_str, 1)
            injected_count += 1

with open(registry_path, "w", encoding="utf-8") as rf:
    rf.write(registry_code)

print(f"Successfully injected HTML article content into {injected_count} health calculator registry objects!")

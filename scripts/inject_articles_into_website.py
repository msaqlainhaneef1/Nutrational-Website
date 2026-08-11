import os
import json
import re
from bs4 import BeautifulSoup

workspace_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website"
extracted_dir = os.path.join(workspace_dir, "extracted_articles")
data_restaurants_dir = os.path.join(workspace_dir, "src", "data", "restaurants")
data_foods_dir = os.path.join(workspace_dir, "src", "data", "foods")

# Clean HTML for injection and extract FAQs for JSON-LD schema
def clean_html_for_injection(raw_html, page_title):
    soup = BeautifulSoup(raw_html, "html.parser")
    
    meta_title = ""
    meta_desc = ""

    meta_p = soup.find_all("p")
    for p in meta_p:
        txt = p.get_text().strip()
        if txt.startswith("Meta Title:") or txt.startswith("SEO Title:"):
            meta_title = re.sub(r'^(Meta Title|SEO Title)[:\s]*', '', txt, flags=re.IGNORECASE).strip()
            p.decompose()
        elif txt.startswith("Meta Description:") or txt.startswith("SEO Description:"):
            meta_desc = re.sub(r'^(Meta Description|SEO Description)[:\s]*', '', txt, flags=re.IGNORECASE).strip()
            p.decompose()

    # STRICT SEO RULE: Ensure ONLY ONE <h1> per page.
    for h1 in soup.find_all("h1"):
        h2 = soup.new_tag("h2")
        h2.string = h1.get_text().strip()
        h2["class"] = "text-2xl md:text-3xl font-extrabold text-white mb-4 mt-8 flex items-center gap-2"
        h1.replace_with(h2)

    for h2 in soup.find_all("h2"):
        if "faq" not in h2.get_text().lower() and "questions" not in h2.get_text().lower():
            h2["class"] = "text-xl md:text-2xl font-bold text-emerald-400 mb-3 mt-6 border-b border-zinc-800 pb-2"
        else:
            h2["class"] = "text-2xl font-bold text-white mb-4 mt-8 flex items-center gap-2 border-b border-zinc-800 pb-2"

    for h3 in soup.find_all("h3"):
        h3["class"] = "text-lg font-semibold text-zinc-200 mb-2 mt-4"

    # Extract FAQs for Schema.org JSON-LD
    faqs = []
    for details in soup.find_all("details", class_="faq-accordion-item"):
        summary = details.find("summary")
        ans_div = details.find("div", class_="faq-accordion-answer")
        if summary and ans_div:
            q_text = summary.get_text().replace("+", "").strip()
            a_text = ans_div.get_text().strip()
            if q_text and a_text:
                faqs.append({"q": q_text, "a": a_text})

    # Enhance tables for mobile responsiveness and dark theme
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
        if p.parent.name != "div" or "faq-accordion-answer" not in p.parent.get("class", []):
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

    return {
        "meta_title": meta_title,
        "meta_desc": meta_desc,
        "html_content": inner_html.strip(),
        "faqs": faqs
    }

extracted_files = [f for f in os.listdir(extracted_dir) if f.endswith(".html")]

def super_clean(s):
    s = s.replace("’", "").replace("'", "").replace("“", "").replace("”", "").replace('"', "")
    s = re.sub(r'nutrition calculator|calculator|nutrition facts|calories|nutrition|guide|&|and', '', s, flags=re.IGNORECASE)
    return re.sub(r'[^a-z0-9]', '', s.lower())

restaurant_injected_count = 0
if os.path.exists(data_restaurants_dir):
    for f in os.listdir(data_restaurants_dir):
        if f.endswith(".json") and f != "_index.json":
            json_path = os.path.join(data_restaurants_dir, f)
            with open(json_path, "r", encoding="utf-8") as jf:
                rdata = json.load(jf)
            
            slug = rdata.get("slug", f.replace(".json", ""))
            rname = rdata.get("name", "")
            
            s_clean = super_clean(slug)
            n_clean = super_clean(rname)
            
            match_file = None
            for hfname in extracted_files:
                h_clean = super_clean(hfname)
                if (s_clean and s_clean in h_clean) or (n_clean and n_clean in h_clean) or (h_clean and h_clean in s_clean):
                    match_file = hfname
                    break
                if "jamba" in slug and "jamba" in hfname.lower():
                    match_file = hfname
                    break

            if match_file:
                hpath = os.path.join(extracted_dir, match_file)
                with open(hpath, "r", encoding="utf-8") as hf:
                    raw_html = hf.read()
                
                cleaned = clean_html_for_injection(raw_html, rname)
                rdata["articleHtml"] = cleaned["html_content"]
                if cleaned["meta_title"]:
                    rdata["seoTitle"] = cleaned["meta_title"]
                if cleaned["meta_desc"]:
                    rdata["seoDescription"] = cleaned["meta_desc"]
                if cleaned["faqs"]:
                    rdata["faqs"] = cleaned["faqs"]

                with open(json_path, "w", encoding="utf-8") as jf:
                    json.dump(rdata, jf, indent=2, ensure_ascii=False)
                
                restaurant_injected_count += 1

print(f"INJECTED ACCORDION HTML AND SCHEMA FAQS INTO {restaurant_injected_count} RESTAURANT JSON FILES")

food_injected_count = 0
if os.path.exists(data_foods_dir):
    for f in os.listdir(data_foods_dir):
        if f.endswith(".json") and f != "_index.json":
            json_path = os.path.join(data_foods_dir, f)
            with open(json_path, "r", encoding="utf-8") as jf:
                fdata = json.load(jf)
            
            slug = fdata.get("slug", f.replace(".json", ""))
            fname_str = fdata.get("name", "")
            
            s_clean = super_clean(slug)
            n_clean = super_clean(fname_str)
            
            match_file = None
            for hfname in extracted_files:
                h_clean = super_clean(hfname)
                if (s_clean and s_clean in h_clean) or (n_clean and n_clean in h_clean):
                    match_file = hfname
                    break

            if match_file:
                hpath = os.path.join(extracted_dir, match_file)
                with open(hpath, "r", encoding="utf-8") as hf:
                    raw_html = hf.read()
                
                cleaned = clean_html_for_injection(raw_html, fname_str)
                fdata["articleHtml"] = cleaned["html_content"]
                if cleaned["meta_title"]:
                    fdata["seoTitle"] = cleaned["meta_title"]
                if cleaned["meta_desc"]:
                    fdata["seoDescription"] = cleaned["meta_desc"]
                if cleaned["faqs"]:
                    fdata["faqs"] = cleaned["faqs"]

                with open(json_path, "w", encoding="utf-8") as jf:
                    json.dump(fdata, jf, indent=2, ensure_ascii=False)
                
                food_injected_count += 1

print(f"INJECTED ACCORDION HTML AND SCHEMA FAQS INTO {food_injected_count} FOOD JSON FILES")

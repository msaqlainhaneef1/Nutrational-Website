import os
import json
import re
from bs4 import BeautifulSoup

extracted_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\extracted_articles"
html_files = [f for f in os.listdir(extracted_dir) if f.endswith(".html")]

print(f"Cleaning duplicates and converting FAQ sections across {len(html_files)} extracted HTML files...")

converted_count = 0
total_accordions = 0

def convert_faqs_in_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # 0. Clean out existing accordion containers from previous runs to prevent re-duplication
    for existing_acc in soup.find_all("div", class_="faq-accordion-container"):
        existing_acc.decompose()

    # 1. Locate all potential FAQ section headings
    faq_headings = []
    for h in soup.find_all(["h2", "h3"]):
        txt = h.get_text().strip().lower()
        if any(kw in txt for kw in ["questions", "faq", "frequently asked", "q&a", "common questions", "queries"]):
            faq_headings.append(h)

    if not faq_headings:
        q_h3s = [h for h in soup.find_all("h3") if h.get_text().strip().endswith("?")]
        if len(q_h3s) >= 2:
            first_q = q_h3s[0]
            prev_h2 = first_q.find_previous(["h2", "h1"])
            if prev_h2 and prev_h2 not in faq_headings:
                faq_headings.append(prev_h2)

    accordions_created = 0
    extracted_faqs = []

    for faq_h in faq_headings:
        accordion_container = soup.new_tag("div", attrs={"class": "faq-accordion-container space-y-3 my-6"})
        
        curr = faq_h.next_sibling
        current_q = None
        current_ans_nodes = []
        nodes_to_remove = []

        while curr:
            next_sib = curr.next_sibling
            if curr.name in ["h1", "h2"] and curr != faq_h:
                txt = curr.get_text().strip().lower()
                if not any(kw in txt for kw in ["questions", "faq", "frequently asked", "q&a"]):
                    # Reached next major section
                    break

            if curr.name in ["h3", "p", "h2", "div"]:
                txt = curr.get_text().strip()
                is_q = (curr.name in ["h3", "h2"] and ("?" in txt or any(txt.lower().startswith(w) for w in ["what", "how", "why", "are", "is", "can", "does", "do"]))) or \
                       (curr.name == "p" and txt.endswith("?") and len(txt) < 150)
                
                if is_q and txt and not any(kw in txt.lower() for kw in ["frequently asked questions", "nutrition questions", "common questions"]) and txt != faq_h.get_text().strip():
                    if current_q and current_ans_nodes:
                        ans_text = " ".join(n.get_text().strip() for n in current_ans_nodes).strip()
                        if current_q and ans_text:
                            extracted_faqs.append({"q": current_q, "a": ans_text})

                        details = soup.new_tag("details", attrs={"class": "faq-accordion-item glass-card-static rounded-xl border border-zinc-800/80 p-0 mb-3 overflow-hidden group"})
                        summary = soup.new_tag("summary", attrs={"class": "faq-accordion-summary font-bold text-white text-sm md:text-base cursor-pointer list-none flex items-center justify-between p-4 bg-zinc-900/60 hover:bg-zinc-900 transition-colors"})
                        
                        q_span = soup.new_tag("span")
                        q_span.string = current_q
                        summary.append(q_span)
                        
                        icon_span = soup.new_tag("span", attrs={"class": "faq-icon text-emerald-400 text-lg leading-none transition-transform group-open:rotate-45 ml-2"})
                        icon_span.string = "+"
                        summary.append(icon_span)
                        
                        details.append(summary)
                        
                        ans_div = soup.new_tag("div", attrs={"class": "faq-accordion-answer p-4 text-zinc-300 text-sm leading-relaxed border-t border-zinc-800/60 bg-zinc-950/40"})
                        for node in current_ans_nodes:
                            # Clone node for accordion answer
                            ans_div.append(node)
                        
                        details.append(ans_div)
                        accordion_container.append(details)
                        accordions_created += 1

                    current_q = txt
                    current_ans_nodes = []
                    nodes_to_remove.append(curr)
                else:
                    if current_q:
                        current_ans_nodes.append(curr)
                        nodes_to_remove.append(curr)

            curr = next_sib

        if current_q and current_ans_nodes:
            ans_text = " ".join(n.get_text().strip() for n in current_ans_nodes).strip()
            if current_q and ans_text:
                extracted_faqs.append({"q": current_q, "a": ans_text})

            details = soup.new_tag("details", attrs={"class": "faq-accordion-item glass-card-static rounded-xl border border-zinc-800/80 p-0 mb-3 overflow-hidden group"})
            summary = soup.new_tag("summary", attrs={"class": "faq-accordion-summary font-bold text-white text-sm md:text-base cursor-pointer list-none flex items-center justify-between p-4 bg-zinc-900/60 hover:bg-zinc-900 transition-colors"})
            
            q_span = soup.new_tag("span")
            q_span.string = current_q
            summary.append(q_span)
            
            icon_span = soup.new_tag("span", attrs={"class": "faq-icon text-emerald-400 text-lg leading-none transition-transform group-open:rotate-45 ml-2"})
            icon_span.string = "+"
            summary.append(icon_span)
            
            details.append(summary)
            
            ans_div = soup.new_tag("div", attrs={"class": "faq-accordion-answer p-4 text-zinc-300 text-sm leading-relaxed border-t border-zinc-800/60 bg-zinc-950/40"})
            for node in current_ans_nodes:
                ans_div.append(node)
            
            details.append(ans_div)
            accordion_container.append(details)
            accordions_created += 1

        if accordions_created > 0:
            faq_h.insert_after(accordion_container)
            # DECOMPOSE ORIGINAL NODES TO PREVENT DUPLICATION!
            for node in nodes_to_remove:
                node.decompose()

    return {
        "html": str(soup),
        "accordions_created": accordions_created,
        "faqs": extracted_faqs
    }

for fname in html_files:
    fpath = os.path.join(extracted_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        raw = f.read()

    res = convert_faqs_in_html(raw)
    if res["accordions_created"] > 0:
        converted_count += 1
        total_accordions += res["accordions_created"]
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(res["html"])

print(f"\n==================================================")
print(f"CLEANED AND CONVERTED FAQ SECTIONS IN {converted_count} EXTRACTED HTML FILES")
print(f"TOTAL INTERACTIVE FAQ ACCORDIONS CREATED: {total_accordions}")
print(f"==================================================")

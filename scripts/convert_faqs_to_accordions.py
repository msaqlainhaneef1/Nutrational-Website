import os
import re
from bs4 import BeautifulSoup

extracted_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\extracted_articles"
html_files = [f for f in os.listdir(extracted_dir) if f.endswith(".html")]

print(f"Converting FAQ sections to interactive accordions across {len(html_files)} HTML files...")

converted_files_count = 0
total_accordions_count = 0

for fname in html_files:
    fpath = os.path.join(extracted_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")
    
    # Locate FAQ H2 section
    faq_h2 = None
    for h2 in soup.find_all(["h2", "h3"]):
        txt = h2.get_text().strip().lower()
        if "frequently asked questions" in txt or txt == "faqs" or "faq" in txt:
            faq_h2 = h2
            break

    if not faq_h2:
        continue

    # Create accordion container
    accordion_container = soup.new_tag("div", attrs={"class": "faq-accordion-container space-y-3 my-6"})
    
    # Collect nodes after faq_h2 until next H2
    current_q = None
    current_answers = []
    nodes_to_remove = []
    accordions_in_file = 0

    curr = faq_h2.next_sibling
    while curr:
        next_sibling = curr.next_sibling
        if curr.name and curr.name.startswith("h") and curr.name != "h3" and not ("frequently" in curr.get_text().lower() or "faq" in curr.get_text().lower()):
            # Reached next major section
            break
        
        if curr.name in ["h3", "p", "h2", "div"]:
            text = curr.get_text().strip()
            # Check if this node is a question (h3 or strong question)
            is_q = curr.name == "h3" or (curr.name == "p" and ("?" in text or text.lower().startswith("what") or text.lower().startswith("how") or text.lower().startswith("is ") or text.lower().startswith("can ")))
            
            if is_q and text and not ("frequently asked questions" in text.lower() or text.lower() == "faqs"):
                # Save previous Q&A
                if current_q and current_answers:
                    # Create details tag
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
                    for ans_node in current_answers:
                        ans_div.append(ans_node)
                    
                    details.append(ans_div)
                    accordion_container.append(details)
                    accordions_in_file += 1

                current_q = text
                current_answers = []
                nodes_to_remove.append(curr)
            else:
                if current_q:
                    current_answers.append(curr)
                    nodes_to_remove.append(curr)

        curr = next_sibling

    # Handle final Q&A in section
    if current_q and current_answers:
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
        for ans_node in current_answers:
            ans_div.append(ans_node)
        
        details.append(ans_div)
        accordion_container.append(details)
        accordions_in_file += 1

    if accordions_in_file > 0:
        faq_h2.insert_after(accordion_container)
        converted_files_count += 1
        total_accordions_count += accordions_in_file

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(str(soup))

print(f"\n==================================================")
print(f"SUCCESSFULLY CONVERTED FAQ SECTIONS IN {converted_files_count} FILES")
print(f"TOTAL INTERACTIVE FAQ ACCORDIONS CREATED: {total_accordions_count}")
print(f"==================================================")

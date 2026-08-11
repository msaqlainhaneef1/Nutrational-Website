import os
import json
import re

workspace_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website"
data_restaurants_dir = os.path.join(workspace_dir, "src", "data", "restaurants")

bob_evans_path = os.path.join(data_restaurants_dir, "bob-evans-nutrition-calculator.json")
with open(bob_evans_path, "r", encoding="utf-8") as f:
    bob_data = json.load(f)

print("==================================================")
print("VERIFYING BOB EVANS ACCORDION & SCHEMA INJECTION")
print("==================================================")
has_details = "<details" in bob_data.get("articleHtml", "")
has_summary = "<summary" in bob_data.get("articleHtml", "")
faqs_count = len(bob_data.get("faqs", []))

print(f"Contains <details> accordion elements: {has_details}")
print(f"Contains <summary> question elements: {has_summary}")
print(f"Extracted FAQs for JSON-LD Schema: {faqs_count} items")

if faqs_count > 0:
    print("\nSample Extracted FAQ for Schema.org:")
    print(json.dumps(bob_data["faqs"][0], indent=2))

# Audit total restaurants with accordions & FAQs schema
all_rests = [f for f in os.listdir(data_restaurants_dir) if f.endswith(".json") and f != "_index.json"]
rests_with_faqs = 0
total_faq_items = 0

for rf in all_rests:
    fpath = os.path.join(data_restaurants_dir, rf)
    with open(fpath, "r", encoding="utf-8") as f:
        d = json.load(f)
    if "faqs" in d and len(d["faqs"]) > 0:
        rests_with_faqs += 1
        total_faq_items += len(d["faqs"])

print("\n--------------------------------------------------")
print(f"Total Restaurant Pages with FAQ Accordions & Schema: {rests_with_faqs} / {len(all_rests)}")
print(f"Total Structured FAQ Items Extracted Across Site: {total_faq_items}")
print("--------------------------------------------------")

import os

pages_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\src\pages"

print("==================================================")
print("AUDITING COMMON HEADER & FOOTER LAYOUT USAGE")
print("==================================================")

astro_pages = []
for root, dirs, files in os.walk(pages_dir):
    for f in files:
        if f.endswith(".astro"):
            astro_pages.append(os.path.join(root, f))

print(f"Auditing total page routes in src/pages/: {len(astro_pages)}\n")

pages_with_layout = 0
pages_with_duplicate_header = 0
pages_with_duplicate_footer = 0

for ppath in astro_pages:
    rel_path = os.path.relpath(ppath, pages_dir)
    with open(ppath, "r", encoding="utf-8") as f:
        content = f.read()

    if "<Layout" in content:
        pages_with_layout += 1
    else:
        print(f"[WARNING: Missing Layout import] {rel_path}")

    if "<header" in content.lower():
        pages_with_duplicate_header += 1
        print(f"[WARNING: Duplicate <header> tag found] {rel_path}")

    if "<footer" in content.lower():
        pages_with_duplicate_footer += 1
        print(f"[WARNING: Duplicate <footer> tag found] {rel_path}")

print("--------------------------------------------------")
print(f"[OK] Pages wrapping content in <Layout>: {pages_with_layout} / {len(astro_pages)}")
print(f"[OK] Pages with duplicate inline <header>: {pages_with_duplicate_header} (Should be 0)")
print(f"[OK] Pages with duplicate inline <footer>: {pages_with_duplicate_footer} (Should be 0)")

if pages_with_layout == len(astro_pages) and pages_with_duplicate_header == 0 and pages_with_duplicate_footer == 0:
    print("\nPERFECT! 100% OF SITE PAGES USE THE COMMON CENTRALIZED HEADER & FOOTER!")
else:
    print("\n⚠️ WARNING: Found layout inconsistencies.")
print("==================================================")

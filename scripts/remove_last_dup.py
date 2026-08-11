import os

extracted_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website\extracted_articles"
dup_path = os.path.join(extracted_dir, "Sonic Drive-In Nutrition Calculator (1).html")

if os.path.exists(dup_path):
    os.remove(dup_path)
    print("Successfully removed duplicate: Sonic Drive-In Nutrition Calculator (1).html")

files = [f for f in os.listdir(extracted_dir) if f.endswith(".html")]
print(f"FINAL TOTAL UNIQUE ARTICLE HTML FILES: {len(files)}")

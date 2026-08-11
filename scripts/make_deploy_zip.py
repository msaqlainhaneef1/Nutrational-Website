import os
import zipfile

workspace_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website"
dist_dir = os.path.join(workspace_dir, "dist")
zip_path = os.path.join(workspace_dir, "website_deploy.zip")

print("==================================================")
print("CREATING ZIP DEPLOYMENT PACKAGE FROM DIST/")
print("==================================================")

file_count = 0
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(dist_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, dist_dir)
            zipf.write(file_path, arcname)
            file_count += 1

zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
print(f"[OK] Archived {file_count} files into '{zip_path}'")
print(f"[OK] Deployment Zip Size: {zip_size_mb:.2f} MB")
print("==================================================")

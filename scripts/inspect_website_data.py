import os

workspace_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website"
data_dir = os.path.join(workspace_dir, "src", "data")
content_dir = os.path.join(workspace_dir, "src", "content")

print("=== FILES IN src/data ===")
if os.path.exists(data_dir):
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            p = os.path.join(root, f)
            print(f"- {os.path.relpath(p, workspace_dir)} ({os.path.getsize(p)} bytes)")

print("\n=== FILES IN src/content ===")
if os.path.exists(content_dir):
    for root, dirs, files in os.walk(content_dir):
        for f in files:
            p = os.path.join(root, f)
            print(f"- {os.path.relpath(p, workspace_dir)} ({os.path.getsize(p)} bytes)")

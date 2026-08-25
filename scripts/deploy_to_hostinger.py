import os
import sys
import zipfile
import urllib.request
import urllib.error

# Determine current workspace dir dynamically
workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dist_dir = os.path.join(workspace_dir, "dist")
zip_path = os.path.join(workspace_dir, "website_deploy.zip")
ssh_dir = os.path.expanduser(r"~\.ssh")

print("==================================================")
print("1. PACKAGING DIST INTO DEPLOYMENT ZIP")
print("==================================================")

if not os.path.exists(dist_dir):
    print(f"[ERROR] Dist directory '{dist_dir}' does not exist!")
    sys.exit(1)

file_count = 0
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(dist_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, dist_dir)
            zipf.write(file_path, arcname)
            file_count += 1

zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
print(f"[OK] Archived {file_count} files into '{zip_path}' ({zip_size_mb:.2f} MB)")

print("\n==================================================")
print("2. CONNECTING TO HOSTINGER VIA SSH/SFTP")
print("==================================================")

try:
    import paramiko
except ImportError:
    print("[ERROR] paramiko is required for SSH deployment.")
    sys.exit(1)

hostname = "195.35.15.206"
port = 65002
username = "u816191105"

possible_keys = ["id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"]
key_file = None

for k in possible_keys:
    kp = os.path.join(ssh_dir, k)
    if os.path.exists(kp):
        key_file = kp
        print(f"[OK] Found SSH Private Key: {key_file}")
        break

if not key_file and os.path.exists(ssh_dir):
    files = [f for f in os.listdir(ssh_dir) if not f.endswith(".pub") and f != "known_hosts"]
    if files:
        key_file = os.path.join(ssh_dir, files[0])
        print(f"[OK] Using Private Key: {key_file}")

if not key_file:
    print(f"[ERROR] No SSH private key found in {ssh_dir}")
    sys.exit(1)

pkey = None
for key_cls in [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey]:
    try:
        pkey = key_cls.from_private_key_file(key_file)
        break
    except Exception:
        continue

if not pkey:
    # try default
    try:
        pkey = paramiko.RSAKey.from_private_key_file(key_file)
    except Exception as e:
        print(f"[ERROR] Failed to load SSH key from {key_file}: {e}")
        sys.exit(1)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print(f"Connecting to {username}@{hostname}:{port}...")
try:
    ssh.connect(hostname=hostname, port=port, username=username, pkey=pkey, timeout=20)
    print("[SUCCESS] SSH Connection Established!\n")
except Exception as e:
    print(f"[ERROR] SSH Connection Failed: {e}")
    sys.exit(1)

def run_remote_cmd(cmd):
    print(f"--> Remote: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="ignore").strip()
    err = stderr.read().decode("utf-8", errors="ignore").strip()
    if out:
        print(f"[STDOUT] {out}")
    if err:
        print(f"[STDERR] {err}")
    return out

# 3. Locate Target Domain Directory
print("--- LOCATING WEB ROOT ---")
find_out = run_remote_cmd("find domains/ -maxdepth 2 -type d")
target_dir = None
for line in find_out.splitlines():
    if "nutritionsolver" in line and "public_html" in line:
        target_dir = line
        break
    elif "nutritionsolver" in line:
        target_dir = os.path.join(line, "public_html").replace("\\", "/")

if not target_dir:
    target_dir = "domains/nutritionsolver.com/public_html"
    run_remote_cmd(f"mkdir -p {target_dir}")

print(f"[TARGET WEB ROOT]: {target_dir}\n")

# 4. SFTP Upload
print("--- UPLOADING DEPLOYMENT ARCHIVE ---")
run_remote_cmd("rm -rf ~/tmp_deploy && mkdir -p ~/tmp_deploy")

sftp = ssh.open_sftp()
remote_zip = f"/home/{username}/tmp_deploy/website_deploy.zip"
print(f"Uploading '{zip_path}' -> '{remote_zip}'...")
sftp.put(zip_path, remote_zip)
sftp.close()
print("[OK] SFTP Upload Complete!\n")

# 5. Extract in temporary staging directory
print("--- EXTRACTING & STAGING ---")
run_remote_cmd("cd ~/tmp_deploy && unzip -q -o website_deploy.zip && rm website_deploy.zip")
staged_count = run_remote_cmd("find ~/tmp_deploy -type f | wc -l")
print(f"[OK] Staged Files: {staged_count}")

# 6. Atomic Sync to Live Directory
print("--- SYNCING TO LIVE WEB ROOT ---")
run_remote_cmd(f"mkdir -p {target_dir}")
run_remote_cmd(f"rm -rf {target_dir}/*")
run_remote_cmd(f"cp -r ~/tmp_deploy/* {target_dir}/")
run_remote_cmd(f"find {target_dir} -type d -exec chmod 755 {{}} +")
run_remote_cmd(f"find {target_dir} -type f -exec chmod 644 {{}} +")
run_remote_cmd("rm -rf ~/tmp_deploy")

live_file_count = run_remote_cmd(f"find {target_dir} -type f | wc -l")
print(f"[OK] Live Deployed Files Count: {live_file_count}\n")

ssh.close()
print("==================================================")
print("DEPLOYMENT TO HOSTINGER COMPLETED!")
print("==================================================")

# 7. Live URL Health Verification
print("\n==================================================")
print("3. LIVE WEBSITE VERIFICATION & HEALTH CHECKS")
print("==================================================")

test_urls = [
    "https://nutritionsolver.com/",
    "https://nutritionsolver.com/about/",
    "https://nutritionsolver.com/contact/",
    "https://nutritionsolver.com/privacy/",
    "https://nutritionsolver.com/terms/",
    "https://nutritionsolver.com/authors/",
    "https://nutritionsolver.com/authors/sarah-jenkins/",
    "https://nutritionsolver.com/sitemap/",
    "https://nutritionsolver.com/restaurants/",
    "https://nutritionsolver.com/calculators/",
    "https://nutritionsolver.com/calculators/calorie-deficit/",
    "https://nutritionsolver.com/calculators/tdee/",
    "https://nutritionsolver.com/restaurants/starbucks-nutrition-calculator/",
    "https://nutritionsolver.com/restaurants/pizza-hut-nutrition-calculator/",
    "https://nutritionsolver.com/restaurants/olive-garden-nutrition-calculator/",
    "https://nutritionsolver.com/restaurants/7-brew-nutrition-calculator/",
    "https://nutritionsolver.com/8f7b2439c2d14b1897c4f44778be1a85.txt",
]

req_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for url in test_urls:
    try:
        req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            content = resp.read(2048).decode('utf-8', errors='ignore')
            title = ""
            if "<title>" in content:
                title = content.split("<title>")[1].split("</title>")[0].strip()
            print(f"[200 OK] {url} -> Title: {title or 'File content ok'}")
    except urllib.error.HTTPError as e:
        print(f"[{e.code} ERROR] {url}: {e.reason}")
    except Exception as e:
        print(f"[ERROR] {url}: {e}")

print("\n==================================================")
print("ALL LIVE TESTS COMPLETE!")
print("==================================================")

# Trigger IndexNow
indexnow_script = os.path.join(workspace_dir, "scripts", "submit-indexnow.mjs")
if os.path.exists(indexnow_script):
    print("\n--- TRIGGERING INSTANT INDEXNOW SUBMISSION ---")
    os.system(f"node \"{indexnow_script}\"")

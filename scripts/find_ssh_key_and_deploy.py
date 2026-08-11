import os
import sys
import paramiko

ssh_dir = r"C:\Users\Saqlain\.ssh"
workspace_dir = r"c:\Users\Saqlain\OneDrive\Documents\Nutrational Website"
zip_path = os.path.join(workspace_dir, "website_deploy.zip")

hostname = "195.35.15.206"
port = 65002
username = "u816191105"

print("==================================================")
print("HOSTINGER SSH DEPLOYMENT VIA PRIVATE KEY")
print("==================================================")

# 1. Locate SSH Key
possible_keys = ["id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"]
key_file = None

for k in possible_keys:
    kp = os.path.join(ssh_dir, k)
    if os.path.exists(kp):
        key_file = kp
        print(f"[OK] Found SSH Private Key: {key_file}")
        break

if not key_file:
    print(f"[SEARCHING] Checking all files in {ssh_dir}...")
    if os.path.exists(ssh_dir):
        files = [f for f in os.listdir(ssh_dir) if not f.endswith(".pub") and f != "known_hosts"]
        if files:
            key_file = os.path.join(ssh_dir, files[0])
            print(f"[OK] Using Private Key: {key_file}")

if not key_file:
    print("[ERROR] No SSH private key found in C:\\Users\\Saqlain\\.ssh\\")
    sys.exit(1)

# 2. Connect Paramiko SSH
pkey = None
try:
    pkey = paramiko.RSAKey.from_private_key_file(key_file)
except Exception:
    try:
        pkey = paramiko.Ed25519Key.from_private_key_file(key_file)
    except Exception:
        try:
            pkey = paramiko.ECDSAKey.from_private_key_file(key_file)
        except Exception as e:
            print(f"[ERROR] Failed to load SSH key: {e}")
            sys.exit(1)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print("Connecting to u816191105@195.35.15.206:65002 using id_rsa...")
try:
    ssh.connect(hostname=hostname, port=port, username=username, pkey=pkey, timeout=15)
    print("[SUCCESS] SSH Connection Successful!\n")
except Exception as e:
    print(f"[ERROR] SSH Connection Failed: {e}")
    sys.exit(1)

def run_remote_cmd(cmd):
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    if out.strip():
        print(f"[STDOUT]\n{out.strip()}")
    if err.strip():
        print(f"[STDERR]\n{err.strip()}")
    return out.strip()

# 3. Remote Directory Inspection
print("--- STEP 1: REMOTE DIRECTORY INSPECTION ---")
run_remote_cmd("pwd; ls -la")
run_remote_cmd("ls -la domains/")

# Locate target domain directory
target_dir = None
output = run_remote_cmd("find domains/ -maxdepth 2 -type d")

if "nutritionsolver" in output:
    for line in output.splitlines():
        if "nutritionsolver" in line and "public_html" in line:
            target_dir = line
            break
        elif "nutritionsolver" in line:
            target_dir = os.path.join(line, "public_html")

if not target_dir:
    target_dir = "domains/nutritionsolver.com/public_html"
    # Ensure folder exists
    run_remote_cmd(f"mkdir -p {target_dir}")

print(f"\n[TARGET WEB ROOT]: {target_dir}\n")

# 4. Upload zip to temporary folder
print("--- STEP 2: UPLOADING DEPLOYMENT ZIP TO TEMP VERIFICATION FOLDER ---")
run_remote_cmd("rm -rf ~/tmp_deploy_verify && mkdir -p ~/tmp_deploy_verify")

sftp = ssh.open_sftp()
remote_zip = "/home/u816191105/tmp_deploy_verify/website_deploy.zip"

print("SFTP Uploading '{zip_path}' -> '{remote_zip}'...")
sftp.put(zip_path, remote_zip)
sftp.close()
print("[OK] Upload Complete!\n")

# 5. Extract & Verify in Temporary Folder
print("--- STEP 3: EXTRACTING & VERIFYING IN TEMP FOLDER ---")
run_remote_cmd("cd ~/tmp_deploy_verify && unzip -o website_deploy.zip && rm website_deploy.zip")
temp_file_count = run_remote_cmd("find ~/tmp_deploy_verify -type f | wc -l")
print(f"[OK] Extracted Files Count in Temp Folder: {temp_file_count}")

# 6. Deploy to Real Target Folder (Atomic Update)
print("--- STEP 4: DEPLOYING TO LIVE TARGET FOLDER ---")

# Back up old target files or clean old build files
run_remote_cmd(f"mkdir -p {target_dir}")
run_remote_cmd(f"rm -rf {target_dir}/*")

# Copy verified contents from temp to target web root
run_remote_cmd(f"cp -r ~/tmp_deploy_verify/* {target_dir}/")

# Fix permissions
run_remote_cmd(f"find {target_dir} -type d -exec chmod 755 {{}} +")
run_remote_cmd(f"find {target_dir} -type f -exec chmod 644 {{}} +")

# 7. Clean up Temporary Directory
print("--- STEP 5: CLEANING UP TEMP FOLDER ---")
run_remote_cmd("rm -rf ~/tmp_deploy_verify")

# 8. Final Verification
print("--- STEP 6: VERIFYING LIVE DEPLOYMENT ---")
live_file_count = run_remote_cmd(f"find {target_dir} -type f | wc -l")
print(f"[OK] Live Target Folder Files: {live_file_count}")

ssh.close()

print("\n==================================================")
print("HOSTINGER LIVE DEPLOYMENT SUCCESSFULLY COMPLETED!")
print("==================================================")

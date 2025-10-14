import os
import requests

url_file = r"C:/Users/ek675/OneDrive - University of Cambridge/Documents/INI/Codes/urls.txt"  # Update this path
save_folder = r"C:/Users/ek675/OneDrive - University of Cambridge/Documents/INI"
os.makedirs(save_folder, exist_ok=True)

with open(url_file, 'r') as file:
    lines = file.readlines()

# Skip header and parse the rest
for line in lines[1:]:
    if not line.strip():
        continue
    parts = line.strip().split('\t')  # split by tab
    
    # Defensive: check if line has at least 3 columns
    if len(parts) < 3:
        print(f"⚠️ Skipping malformed line: {line.strip()}")
        continue
    
    isaac_id, sms_id, url = parts[0], parts[1], parts[2]

    # Use ISAACID_SMSID.mp4 as filename
    filename = f"{isaac_id}_{sms_id}.mp4"
    filepath = os.path.join(save_folder, filename)

    try:
        print(f"⬇️ Downloading {url} ...")
        response = requests.get(url, stream=True, timeout=20)

        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"✅ Saved: {filepath}")
        elif response.status_code == 404:
            print(f"❌ 404 Not Found: {url}")
        else:
            print(f"⚠️ Failed with status {response.status_code}: {url}")
    except requests.RequestException as e:
        print(f"🚫 Error downloading {url}: {e}")

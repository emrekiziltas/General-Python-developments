import os
import requests

# Path to the input file
url_file = r"C:/Users/ek675/OneDrive - University of Cambridge/Documents/INI/Codes/urls.txt"

print("🔍 Checking video URLs from file...\n")

# Read and process the file
try:
    with open(url_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Skip the header
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue  # Skip empty lines

        try:
            isaac_id, sms_id, url = line.split('\t')
        except ValueError:
            print(f"⚠️ Skipping malformed line: {line}")
            continue

        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            status = response.status_code
            if status == 404:
                print(f"❌ 404 Not Found | ISAAC ID: {isaac_id} | SMS ID: {sms_id}")
            elif status >= 400:
                print(f"⚠️ {status} Error: | ISAAC ID: {isaac_id} | SMS ID: {sms_id}")
            else:
                print(f"✅ {status} OK: | ISAAC ID: {isaac_id} | SMS ID: {sms_id}")
        except requests.RequestException as e:
            print(f"⚠️ Error accessing {url}: {e} | ISAAC ID: {isaac_id} | SMS ID: {sms_id}")

except FileNotFoundError:
    print(f"❌ File not found: {url_file}")
except Exception as e:
    print(f"⚠️ Unexpected error: {e}")

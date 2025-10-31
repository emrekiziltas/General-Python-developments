"""
orcid_zbmath_fetcher.py
Fetches ORCID and zbMath author data and exports results to Excel.
"""

import pandas as pd
import requests
import urllib.parse
import os
import json
import traceback

# ---------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------
# File paths
INPUT_CSV = "list.csv"
OUTPUT_EXCEL = "orcid_full_data.xlsx"
JSON_OUTPUT_DIR = "orcid_json"

# API endpoints
ORCID_SEARCH_BASE = "https://pub.orcid.org/v3.0/search/?q="
ORCID_RECORD_BASE = "https://pub.orcid.org/v3.0/"
ZBMATH_SEARCH_URL = "https://api.zbmath.org/v1/author/_search"

# Request settings
MAX_RETRIES = 3
REQUEST_TIMEOUT = 10
ZBMATH_RESULTS_SIZE = 5

# Headers
JSON_HEADERS = {"Accept": "application/json"}

# ---------------------------------------------------------------
# Initialize
# ---------------------------------------------------------------
os.makedirs(JSON_OUTPUT_DIR, exist_ok=True)
summary_list = []

# ---------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------

def safe_get(url, headers=None, params=None, max_retries=MAX_RETRIES, timeout=REQUEST_TIMEOUT):
    """Safe GET request with retries and timeout."""
    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=timeout)
            r.raise_for_status()
            return r
        except Exception as e:
            print(f"   ⚠️ Request failed ({attempt + 1}/{max_retries}) for {url}: {e}")
    return None

# ---------------------------------------------------------------
# zbMath API
# ---------------------------------------------------------------
def zbmath_id(firstname, lastname, orcid_id=None, size=ZBMATH_RESULTS_SIZE):
    """Fetch zbMath author data and merge into summary_list by firstname+lastname."""
    search_string = f"ln:{lastname} fn:{firstname}"
    params = {"search_string": search_string, "size": size}

    print(f"   🔎 Searching zbMath for: {search_string}")
    response = safe_get(ZBMATH_SEARCH_URL, params=params)
    if not response:
        return []

    try:
        data = response.json()
        results_list = data.get("result", [])
        print(results_list)
        if not results_list:
            print("   ⚠️ No zbMath results found")
            return []

        for author in results_list:
            # Find if person already in summary_list by firstname + lastname
            matched_entry = None
            for entry in summary_list:
                if (entry.get("firstname") == firstname and entry.get("lastname") == lastname):
                    matched_entry = entry
                    break

            zb_info = {
                "zbmath_author_id": author.get("code"),
                "zbmath_name": author.get("name"),
                "orcid_from_zbmath": author.get("orcid"),
            }

            if matched_entry:
                # Update the existing entry with zbMath info
                matched_entry.update(zb_info)
                print(f"   ✓ Updated summary with zbMath author for {firstname} {lastname}: {zb_info['zbmath_name']}")
            else:
                # No existing ORCID entry, create new summary row with zbMath info
                new_entry = {
                    "firstname": firstname,
                    "lastname": lastname,
                    "orcid_id": orcid_id,
                    **zb_info
                }
                summary_list.append(new_entry)
                print(f"   ✓ Added new summary entry for zbMath author: {zb_info['zbmath_name']}")

        return results_list

    except Exception as e:
        print(f"   ⚠️ zbMath error for {firstname} {lastname}: {e}")
        return []

# ---------------------------------------------------------------
# ORCID API
# ---------------------------------------------------------------
def orchid_finder(search_data, first, last):
    """Process ORCID search results with detailed debug logging."""
    if "result" not in search_data or not search_data["result"]:
        print(f"   ⚠️ No ORCID ID found")
        return None

    print(f"   ✓ Found {len(search_data['result'])} ORCID profile(s)")

    for res in search_data["result"]:
        try:
            orcid_id = res["orcid-identifier"]["path"]
            record_url = ORCID_RECORD_BASE + orcid_id
            print(f"\n   🔍 Fetching ORCID record for {orcid_id}")

            r_record = safe_get(record_url, headers=JSON_HEADERS)
            if not r_record:
                print(f"   ⚠️ Failed to fetch ORCID record for {orcid_id}")
                continue

            # Try parsing JSON
            try:
                record_data = r_record.json()
            except Exception as e:
                print(f"   ⚠️ JSON decode failed for {orcid_id}: {e}")
                print("   📦 Raw response:", r_record.text[:500])
                continue

            if not record_data or not isinstance(record_data, dict):
                print(f"   ⚠️ Invalid JSON structure for {orcid_id}")
                continue

            # Save for inspection
            json_path = os.path.join(JSON_OUTPUT_DIR, f"{orcid_id}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(record_data, f, indent=2, ensure_ascii=False)

            person = record_data.get("person")
            if person is None:
                print(f"   ⚠️ Missing 'person' block in ORCID {orcid_id}")
                continue

            name_data = person.get("name")
            if name_data is None:
                print(f"   ⚠️ Missing 'name' section in person for ORCID {orcid_id}")

            # Extract safely
            given_names_obj = (name_data or {}).get("given-names")
            family_name_obj = (name_data or {}).get("family-name")

            summary_list.append({
                "firstname": first,
                "lastname": last,
                "orcid_id": orcid_id,
                "orcid_url": f"https://orcid.org/{orcid_id}",
                "given_names": (given_names_obj or {}).get("value"),
                "family_name": (family_name_obj or {}).get("value"),
                "other_names": "; ".join(
                    [n.get("content", "") for n in (person.get("other-names", {}) or {}).get("other-name", []) if n]
                ),
            })

            return orcid_id  # Return the first ORCID id found

        except AttributeError as e:
            print(f"   ❌ AttributeError for ORCID {orcid_id}: {e}")
            print(f"   💡 Check: person, activities, or name might be None")
            print(f"   📁 JSON saved at: {json_path}")
            traceback.print_exc()
        except Exception as e:
            print(f"   ⚠️ General error for ORCID {orcid_id}: {e}")
            traceback.print_exc()

    return None

# ---------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------

def main():
    """Main execution function."""
    # Read input CSV
    print(f"📖 Reading input from: {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV)
    names = df.to_dict(orient="records")
    print(f"   ✓ Found {len(names)} names to process\n")

    # Process each person
    for person in names:
        first = str(person["firstname"]).strip()
        last = str(person["lastname"]).strip()
        query = f"given-names:{first} AND family-name:{last}"
        search_url = ORCID_SEARCH_BASE + urllib.parse.quote(query)

        print(f"🔍 Searching for: {first} {last}")

        r_search = safe_get(search_url, headers=JSON_HEADERS)
        if not r_search:
            continue

        try:
            search_data = r_search.json()
            orcid_id = orchid_finder(search_data, first, last)
            zbmath_id(first, last, orcid_id=orcid_id)
        except Exception as e:
            print(f"   ⚠️ ORCID error for {first} {last}: {e}")

    # Save results
    print(f"\n📊 Saving data to: {OUTPUT_EXCEL}")
    with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl") as writer:
        if summary_list:
            pd.DataFrame(summary_list).to_excel(writer, sheet_name="Summary", index=False)

    # Print summary
    print("✅ Finished! All data saved")
    print(f"   - ORCID profiles: {len(summary_list)}")
    zbmath_count = sum(1 for s in summary_list if "zbmath_author_id" in s)
    print(f"   - zbMath profiles: {zbmath_count}")


if __name__ == "__main__":
    main()
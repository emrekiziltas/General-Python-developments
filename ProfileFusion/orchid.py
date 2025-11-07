import requests
import urllib.parse

def find_orcid(first_name, last_name, affiliation=None):
    query = f'given-names:{first_name} AND family-name:{last_name}'
    if affiliation:
        query += f' AND affiliation-org-name:{affiliation}'
    query_encoded = urllib.parse.quote(query)

    url = f"https://pub.orcid.org/v3.0/expanded-search/?q={query_encoded}"
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)

    # Hata kontrolü ekliyoruz
    if response.status_code != 200:
        print(f"⚠️ API hatası: {response.status_code} - {response.text}")
        return []

    try:
        data = response.json()
    except ValueError:
        print("⚠️ JSON parse hatası — muhtemelen boş veya geçersiz cevap.")
        return []

    # Eğer JSON boşsa
    if not isinstance(data, dict) or "expanded-result" not in data:
        print("ℹ️ Hiç sonuç bulunamadı veya beklenmeyen cevap yapısı.")
        return []

    results = []
    for r in data.get("expanded-result", []):
        results.append({
            "name": f"{r.get('given-names')} {r.get('family-names')}",
            "orcid": r.get("orcid-id"),
            "institution": r.get("institution-name")
        })
    return results


# Test isimleri
authors = [
    ("Emre", "Telatar", "EPFL"),
    ("Emre", "Esenturk", "University of Oxford"),
    ("Emre", "Coskun", "Middle East Technical University"),
]

for first, last, aff in authors:
    matches = find_orcid(first, last, aff)
    print(f"\n🔹 {first} {last} ({aff}) için sonuçlar:")
    if matches:
        for m in matches:
            print(f"  👉 {m['orcid']} — {m['name']} ({m['institution']})")
    else:
        print("  🚫 Sonuç bulunamadı.")

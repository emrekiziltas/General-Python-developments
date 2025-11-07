# Gerekli kütüphaneler:
# pip install requests sentence-transformers pandas numpy

import requests
import urllib.parse
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# 1️⃣ BERT modelini yükle
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2️⃣ Yazar listesi
authors = [
    {"first": "Emre", "last": "Telatar", "affiliation": "EPFL"},
    {"first": "Emre", "last": "Esenturk", "affiliation": "University of Oxford"},
    {"first": "Emre", "last": "Coskun", "affiliation": "Middle East Technical University"},
]

# 3️⃣ ORCID API’den aday kayıtları çeken fonksiyon
def fetch_orcid_candidates(first_name, last_name, affiliation=None):
    query = f'given-names:{first_name} AND family-name:{last_name}'
    if affiliation:
        query += f' AND affiliation-org-name:{affiliation}'
    url = f"https://pub.orcid.org/v3.0/expanded-search/?q={urllib.parse.quote(query)}"
    headers = {"Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"⚠️ API hatası ({response.status_code})")
            return []

        try:
            data = response.json()
        except ValueError:
            print("⚠️ JSON parse hatası")
            return []

        results = []
        if data and "expanded-result" in data:
            for r in data["expanded-result"]:
                results.append({
                    "name": f"{r.get('given-names')} {r.get('family-names')}",
                    "orcid": r.get("orcid-id"),
                    "institution": r.get("institution-name")
                })
        else:
            print(f"ℹ️ '{first_name} {last_name}' için sonuç bulunamadı.")
        return results

    except Exception as e:
        print(f"⚠️ API isteği hatası: {e}")
        return []

# 4️⃣ Yazar listesi üzerinde BERT tabanlı eşleştirme
results = []

for author in authors:
    first = author["first"]
    last = author["last"]
    aff = author.get("affiliation")
    query_text = f"{first} {last} {aff}" if aff else f"{first} {last}"

    # ORCID adaylarını çek
    candidates = fetch_orcid_candidates(first, last, aff)
    if not candidates:
        results.append({"name": f"{first} {last}", "affiliation": aff, "orcid": None, "score": None})
        continue

    # BERT ile en iyi eşleşmeyi bul
    query_emb = model.encode(query_text, convert_to_tensor=True)
    best_score = -1
    best_orcid = None

    for c in candidates:
        candidate_text = f"{c['name']} {c['institution']}"
        candidate_emb = model.encode(candidate_text, convert_to_tensor=True)
        score = util.cos_sim(query_emb, candidate_emb).item()
        if score > best_score:
            best_score = score
            best_orcid = c["orcid"]

    results.append({
        "name": f"{first} {last}",
        "affiliation": aff,
        "orcid": best_orcid,
        "score": best_score
    })

# 5️⃣ Sonuçları CSV’ye yaz
df = pd.DataFrame(results)
df.to_csv("author_orcid_matches.csv", index=False)
print("✅ Eşleştirme tamamlandı. author_orcid_matches.csv dosyasına yazıldı.")
print(df)

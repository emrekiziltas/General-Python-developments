import difflib  # Required for sequence matching


def find_and_match_zbmath_author(
        firstname,
        lastname,
        orcid_id,
        size,
        summary_list,
        ZBMATH_SEARCH_URL,
        safe_get
):
    """
    Searches zbMath for an author, finds the best match, and updates
    a summary list with the author's zbMath ID and ORCID (if found).
    """

    # 1. Prepare and execute the search
    search_string = f"ln:{lastname} fn:{firstname}"
    params = {"search_string": search_string, "size": size}

    print(f"   🔎 Searching zbMath for: {search_string}")
    response = safe_get(ZBMATH_SEARCH_URL, params=params)
    if not response:
        print("   ⚠️ zbMath API request failed or returned no response")
        return []  # Return an empty list to indicate no results

    # 2. Parse the response
    try:
        data = response.json()
        results_list = data.get("result", [])
    except Exception as e:
        print(f"   ⚠️ Failed to parse zbMath JSON response: {e}")
        return []

    if not results_list:
        print("   ⚠️ No zbMath results found")
        return []

    print(f"   ✅ zbMath returned {len(results_list)} result(s):")
    for i, author in enumerate(results_list, 1):
        print(f"      {i}. {author.get('name')} (id={author.get('code')})")

    # 3. Find the best matching name using difflib
    orcid_fullname = f"{firstname} {lastname}".lower()
    best_author = None
    best_score = 0.0

    for author in results_list:
        zb_name = (author.get("name") or "").lower()
        # Compute similarity ratio between zbMath and (assumed) ORCID name
        score = difflib.SequenceMatcher(None, orcid_fullname, zb_name).ratio()

        if score > best_score:
            best_author = author
            best_score = score

    if not best_author:
        print("   ⚠️ No matching zbMath author found by name")
        return results_list  # Return all results if no good match

    # 4. Extract info from the best match (including external IDs)

    # Extract external IDs, specifically looking for ORCID
    orcid_from_zbmath = None
    external_ids_list = best_author.get("external_ids", [])  # Get list, default to []

    if external_ids_list:
        # Use next() to find the first dictionary with type "orcid"
        orcid_entry = next(
            (entry for entry in external_ids_list
             if isinstance(entry, dict) and entry.get("type") == "orcid"),
            None  # Default to None if not found
        )

        if orcid_entry:
            orcid_from_zbmath = orcid_entry.get("id")  # Get the ID from that dictionary

    zb_info = {
        "zbmath_author_id": best_author.get("code"),
        "zbmath_name": best_author.get("name"),
        "match_score": round(best_score, 3),
        "orcid_from_zbmath": orcid_from_zbmath,  # Now populated from the API
    }

    # 5. Find or create entry in summary_list
    matched_entry = next(
        (e for e in summary_list
         if e.get("firstname") == firstname and e.get("lastname") == lastname),
        None
    )

    if matched_entry:
        matched_entry.update(zb_info)
        print(f"   ✓ Matched zbMath author: {zb_info['zbmath_name']} (score={best_score:.2f})")
        if orcid_from_zbmath:
            print(f"      Found zbMath ORCID: {orcid_from_zbmath}")
    else:
        new_entry = {
            "firstname": firstname,
            "lastname": lastname,
            "orcid_id": orcid_id,  # This is the ORCID ID you searched with
            **zb_info
        }
        summary_list.append(new_entry)
        print(f"   ✓ Added zbMath author: {zb_info['zbmath_name']} (score={best_score:.2f})")
        if orcid_from_zbmath:
            print(f"      Found zbMath ORCID: {orcid_from_zbmath}")

    return results_list
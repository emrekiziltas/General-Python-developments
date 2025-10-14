# main.py
import asyncio
import pandas as pd
import logging
import time

from constants import API_ENDPOINTS
from fetchers import fetch_all_entities
from extractors import extract_character_info, extract_location_info, extract_episode_info, build_location_lookup
from db_helpers import get_db_connection, batch_insert, insert_characters_with_fk, insert_relations

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def main():
    start = time.perf_counter()

    logging.info("Fetching data from APIs...")
    characters_raw = await fetch_all_entities(API_ENDPOINTS["characters"])
    locations_raw = await fetch_all_entities(API_ENDPOINTS["locations"])
    episodes_raw = await fetch_all_entities(API_ENDPOINTS["episodes"])

    characters = [extract_character_info(c) for c in characters_raw]
    locations = [extract_location_info(l) for l in locations_raw]
    episodes = [extract_episode_info(e) for e in episodes_raw]

    conn = get_db_connection()

    # Insert locations & episodes
    batch_insert(conn, "locations", locations,
                 ["id","name","type","dimension","residents","url","created"])
    batch_insert(conn, "episodes", episodes,
                 ["id","name","air_date","episode","characters","url","created"])

    # Insert characters with FKs
    loc_lookup = build_location_lookup(locations)
    insert_characters_with_fk(conn, characters, loc_lookup)

    # Insert residents
    for loc in locations:
        insert_relations(
            conn,
            table="residents",
            parent_id=loc["id"],
            related_urls=loc.get("residents", "{}"),
            parent_col="location_id",
            child_col="character_id",
            url_col="resident_url"  # ✅ Correct column
        )
    logging.info("Residents inserted.")

    for ep in episodes:
        insert_relations(
            conn,
            table="episode_characters",
            parent_id=ep["id"],
            related_urls=ep.get("characters", []),
            parent_col="episode_id",
            child_col="character_id",
            url_col="character_url"  # ✅ Correct column
        )
    logging.info("Episode-characters inserted.")

    conn.close()

    # Save CSV backups
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    pd.DataFrame(characters).to_csv(f"../output/characters_{timestamp}.csv", index=False)
    pd.DataFrame(locations).to_csv(f"../output/locations_{timestamp}.csv", index=False)
    pd.DataFrame(episodes).to_csv(f"../output/episodes_{timestamp}.csv", index=False)

    end = time.perf_counter()
    logging.info(f"Execution finished in {end - start:.2f} seconds")

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    try:
        asyncio.run(main())
    except RuntimeError:
        # Already running loop (Spyder, Jupyter)
        asyncio.get_event_loop().run_until_complete(main())

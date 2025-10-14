# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 13:05:17 2025

@author: ek675
"""

# fetchers.py
import aiohttp
import asyncio
import logging
from typing import List, Dict

MAX_RETRIES = 5          # Maximum number of retries per request
BACKOFF_FACTOR = 1.5     # Exponential backoff factor (seconds)

async def fetch_page(session: aiohttp.ClientSession, base_url: str, page: int) -> List[Dict]:
    url = f"{base_url}?page={page}"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("results", [])
                else:
                    logging.warning(f"Attempt {attempt}: Failed to fetch {url} — Status {response.status}")
        except aiohttp.ClientError as e:
            logging.warning(f"Attempt {attempt}: ClientError fetching {url}: {e}")
        except asyncio.TimeoutError:
            logging.warning(f"Attempt {attempt}: Timeout fetching {url}")

        # Exponential backoff
        await asyncio.sleep(BACKOFF_FACTOR ** (attempt - 1))

    logging.error(f"❌ All {MAX_RETRIES} attempts failed for {url}")
    return []

async def get_total_pages(session: aiohttp.ClientSession, base_url: str) -> int:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with session.get(base_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["info"]["pages"]
                else:
                    logging.warning(f"Attempt {attempt}: Failed to fetch {base_url} — Status {response.status}")
        except aiohttp.ClientError as e:
            logging.warning(f"Attempt {attempt}: ClientError fetching {base_url}: {e}")
        except asyncio.TimeoutError:
            logging.warning(f"Attempt {attempt}: Timeout fetching {base_url}")

        await asyncio.sleep(BACKOFF_FACTOR ** (attempt - 1))

    logging.error(f"❌ All {MAX_RETRIES} attempts failed for {base_url}")
    return 0

async def fetch_all_entities(base_url: str) -> List[Dict]:
    async with aiohttp.ClientSession() as session:
        total_pages = await get_total_pages(session, base_url)
        if total_pages == 0:
            return []

        tasks = [fetch_page(session, base_url, page) for page in range(1, total_pages + 1)]
        pages = await asyncio.gather(*tasks)
        return [item for page in pages for item in page]

# fetchers.py
import aiohttp
import asyncio
import logging
from typing import List, Dict

async def fetch_page(session: aiohttp.ClientSession, base_url: str, page: int) -> List[Dict]:
    url = f"{base_url}?page={page}"
    async with session.get(url) as response:
        if response.status != 200:
            logging.error(f"Failed to fetch {base_url} page {page} — Status: {response.status}")
            return []
        data = await response.json()
        return data.get("results", [])

async def get_total_pages(session: aiohttp.ClientSession, base_url: str) -> int:
    async with session.get(base_url) as response:
        data = await response.json()
        return data["info"]["pages"]

async def fetch_all_entities(base_url: str) -> List[Dict]:
    async with aiohttp.ClientSession() as session:
        total_pages = await get_total_pages(session, base_url)
        tasks = [fetch_page(session, base_url, page) for page in range(1, total_pages + 1)]
        pages = await asyncio.gather(*tasks)
        return [item for page in pages for item in page]

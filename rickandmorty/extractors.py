# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 13:03:15 2025

@author: ek675
"""
from datetime import datetime
from typing import Dict, List

def extract_character_info(char: Dict) -> Dict:
    return {
        "id": char.get("id"),
        "name": char.get("name"),
        "status": char.get("status"),
        "species": char.get("species"),
        "gender": char.get("gender"),
        "origin": char.get("origin", {}).get("name"),
        "location": char.get("location", {}).get("name"),
        "image": char.get("image"),
        "created": char.get("created"),
        "created_by_ini": datetime.now().isoformat(sep=" ", timespec="seconds")
    }

def extract_location_info(loc: Dict) -> Dict:
    return {
        "id": loc.get("id"),
        "name": loc.get("name"),
        "type": loc.get("type"),
        "residents": loc.get("residents"),
        "dimension": loc.get("dimension"),
        "url": loc.get("url"),
        "created": datetime.now().isoformat(sep=" ", timespec="seconds")
    }

def extract_episode_info(ep: Dict) -> Dict:
    return {
        "id": ep.get("id"),
        "name": ep.get("name"),
        "air_date": ep.get("air_date"),
        "episode": ep.get("episode"),
        "characters": ep.get("characters"),
        "url": ep.get("url"),
        "created": datetime.now().isoformat()
    }

def build_location_lookup(locations: List[Dict]) -> Dict[str, int]:
    return {loc["name"]: loc["id"] for loc in locations}

def parse_pg_array(pg_array) -> List[str]:
    if isinstance(pg_array, list):
        return pg_array
    if isinstance(pg_array, str):
        return pg_array.strip('{}').split(',')
    return []

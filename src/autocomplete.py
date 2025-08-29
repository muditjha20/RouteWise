# src/autocomplete.py
"""
Minimal Home-address autocomplete using Geoapify.
We return a list of suggestions: each with (label, lat, lon).
"""

from typing import List, Tuple
import requests

def suggest_addresses_geoapify(query: str, api_key: str, limit: int = 5) -> List[Tuple[str, float, float]]:
    """
    Call Geoapify Address Autocomplete and return up to `limit` suggestions.
    Each item: (formatted_label, lat, lon).
    Raises requests.RequestException on network errors.
    """
    query = (query or "").strip()
    if not query:
        return []

    url = "https://api.geoapify.com/v1/geocode/autocomplete"
    params = {
        "text": query,
        "limit": str(limit),
        "format": "json",   # simplified JSON
        "apiKey": api_key,
    }

    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    # Format may contain 'results' with items having 'formatted', 'lat', 'lon'
    results = data.get("results", [])
    out: List[Tuple[str, float, float]] = []
    for item in results:
        label = item.get("formatted") or item.get("address_line1") or ""
        lat = item.get("lat")
        lon = item.get("lon")
        if label and lat is not None and lon is not None:
            out.append((label, float(lat), float(lon)))
    return out

# src/geo.py
import time
from typing import List, Tuple
import requests

USER_AGENT = "muditjha1404@gmail.com"

def parse_addresses(raw: str) -> List[str]:
    """Split into non-empty trimmed lines, preserving order."""
    lines = [ln.strip() for ln in (raw or "").splitlines()]
    return [ln for ln in lines if ln]

def geocode_one(address: str) -> Tuple[float, float, str]:
    """
    Use Nominatim (OpenStreetMap) to geocode one address.
    Returns (lat, lon, display_name). Raises ValueError on no result.
    """
    if not address or not address.strip():
        raise ValueError("Empty address provided.")
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "jsonv2", "limit": 1, "addressdetails": 0}
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError(f"No results for: {address}")
    top = data[0]
    return float(top["lat"]), float(top["lon"]), top.get("display_name", address)

def geocode_all(addresses: List[str]) -> Tuple[List[Tuple[float, float, str]], List[str]]:
    """
    Geocode all addresses sequentially. Respects ~1 req/sec.
    Returns (coords, failed). Each coord: (lat, lon, label).
    """
    coords: List[Tuple[float, float, str]] = []
    failed: List[str] = []
    progress = None
    try:
        progress = __import__("streamlit").st.progress(0, text="Geocoding addresses…")
    except Exception:
        progress = None
    total = len(addresses)
    for i, addr in enumerate(addresses, start=1):
        try:
            lat, lon, label = geocode_one(addr)
            coords.append((lat, lon, label))
        except Exception:
            failed.append(addr)
        if progress:
            progress.progress(i / total, text=f"Geocoding {i}/{total}…")
        time.sleep(1.0)  # Nominatim courtesy pacing
    if progress:
        progress.empty()
    return coords, failed

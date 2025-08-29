# src/osrm.py
from typing import List, Tuple
import requests

OSRM_BASE = "https://router.project-osrm.org"

def osrm_table(coords: List[Tuple[float, float, str]], profile: str = "driving") -> tuple[list[list[float]], list[list[float]]]:
    """
    Call OSRM /table to get pairwise travel times AND distances.
    Returns (durations_s, distances_m) as two NxN lists.
    """
    n = len(coords)
    if n <= 1:
        return [[0.0]], [[0.0]]

    # OSRM expects lon,lat
    loc_pairs = ["{:.6f},{:.6f}".format(lon, lat) for (lat, lon, _) in coords]
    coord_str = ";".join(loc_pairs)

    url = f"{OSRM_BASE}/table/v1/{profile}/{coord_str}"
    params = {"annotations": "duration,distance"}

    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    durations = data.get("durations")
    distances = data.get("distances")
    if not durations or not distances:
        raise ValueError("OSRM did not return durations/distances.")

    for mat in (durations, distances):
        for i in range(n):
            for j in range(n):
                if mat[i][j] is None:
                    mat[i][j] = float("inf")

    return durations, distances


def osrm_route_path(coords: List[Tuple[float, float, str]], route_idx: List[int], profile: str = "driving") -> List[Tuple[float, float]]:
    """
    Call OSRM /route to get the actual road polyline for the optimized order.
    Inputs:
        coords     : [(lat, lon, label), ...]
        route_idx  : indices including the final return to 0 (loop)
    Returns:
        road_path  : [(lat, lon), ...] along the road (geojson geometry)
    """
    if len(route_idx) < 2:
        return []

    # Build the ordered coordinate list in lon,lat for OSRM
    ordered_lonlat = []
    for idx in route_idx:
        lat, lon, _ = coords[idx]
        ordered_lonlat.append("{:.6f},{:.6f}".format(lon, lat))

    coord_str = ";".join(ordered_lonlat)
    url = f"{OSRM_BASE}/route/v1/{profile}/{coord_str}"
    params = {
        "overview": "full",
        "geometries": "geojson",  # get raw coords
        "steps": "false",
    }

    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    routes = data.get("routes", [])
    if not routes:
        raise ValueError("OSRM /route returned no routes.")

    geom = routes[0].get("geometry", {})
    coords_ll = geom.get("coordinates", [])  # list of [lon, lat]
    if not coords_ll:
        raise ValueError("OSRM /route missing geometry coordinates.")

    # Convert to (lat, lon)
    road_path = [(latlon[1], latlon[0]) for latlon in coords_ll]
    return road_path

# app.py

import time
from typing import List, Tuple

import numpy as np
import streamlit as st

from src.geo import parse_addresses, geocode_one
from src.algorithms import build_distance_matrix, held_karp_loop
from src.maps import render_route_map_osrm
from src.osrm import osrm_table, osrm_route_path


st.set_page_config(page_title="Multi-Stop Route Optimizer", page_icon=None, layout="wide")

MAX_STOPS = 15  # including Home on line 1

# ---------------- Session state defaults ----------------
if "run_optimize" not in st.session_state:
    st.session_state.run_optimize = False
if "last_coords" not in st.session_state:
    st.session_state.last_coords: List[Tuple[float, float, str]] = []
if "last_route" not in st.session_state:
    st.session_state.last_route: List[int] = []
if "last_total_seconds" not in st.session_state:
    st.session_state.last_total_seconds: float = 0.0
if "last_total_meters" not in st.session_state:
    st.session_state.last_total_meters: float = 0.0
if "used_fallback" not in st.session_state:
    st.session_state.used_fallback = False
if "has_results" not in st.session_state:
    st.session_state.has_results = False

# ---------------- UI Header ----------------
st.title("Multi-Stop Route Optimizer")
st.caption("Enter up to 15 addresses. First line is Home (start and end).")

with st.expander("Notes", expanded=False):
    st.markdown(
        """
- Paste **one address per line**. Line 1 is **Home** (start and end of the loop).
- Geocoding uses **OpenStreetMap Nominatim** (polite pacing ~1 req/sec). Be specific: include city/country.
- Costs use **OSRM road travel time** (seconds). We also fetch **distance** (meters) for display.
- Optimization uses **Held–Karp** (optimal for small N). Limit is **15** addresses total (including Home).
        """
    )

# ---------------- Inputs ----------------
left, right = st.columns([1.2, 1], gap="large")

with left:
    default_placeholder = (
        "University of the West Indies, St. Augustine, Trinidad and Tobago\n"
        "6 Victoria Avenue, Port of Spain\n"
        "Hyatt Regency Trinidad, Port of Spain, Trinidad and Tobago\n"
        "Trinidad Ornamental, Eastern Main Road, San Juan, Trinidad and Tobago"
    )
    raw_addresses = st.text_area(
        "Addresses (one per line)",
        value=default_placeholder,
        height=220,
        placeholder="Home address\nStop 1\nStop 2\n...",
        key="addresses_textarea",
    )

    c1, c2 = st.columns([1, 1])
    if c1.button("Optimize Route", type="primary"):
        st.session_state.run_optimize = True
        st.rerun()
    if c2.button("Reset"):
        st.session_state.clear()
        st.rerun()

with right:
    addresses = parse_addresses(raw_addresses)
    n = len(addresses)

    if n == 0:
        st.info("Enter at least 2 lines (Home + at least one stop).")
    else:
        if n == 1:
            st.warning("You only have Home. Add at least one stop.")
        if n > MAX_STOPS:
            st.error(f"Too many lines ({n}). Limit is {MAX_STOPS} including Home.")
        else:
            st.success(f"Parsed {n} address(es). First line will be treated as Home.")

    if n > 0:
        rows = [(i, "Home" if i == 0 else "Stop", a) for i, a in enumerate(addresses)]
        st.markdown("Parsed Order (before optimization):")
        st.dataframe(
            rows,
            hide_index=True,
            use_container_width=True,
            column_config={
                0: st.column_config.NumberColumn("#"),
                1: st.column_config.TextColumn("Type"),
                2: st.column_config.TextColumn("Address"),
            },
        )

st.divider()
st.subheader("Results")

# ---------------- Optimize pipeline ----------------
if st.session_state.run_optimize:
    try:
        if n < 2:
            st.warning("Add at least Home + 1 stop before optimizing.")
            st.session_state.run_optimize = False
        elif n > MAX_STOPS:
            st.warning(f"Reduce your list to ≤ {MAX_STOPS} lines.")
            st.session_state.run_optimize = False
        else:
            # Geocode (visible)
            st.write("Starting geocoding…")
            progress = st.progress(0.0, text="Geocoding addresses…")
            coords: List[Tuple[float, float, str]] = []
            failed: List[str] = []
            for i, addr in enumerate(addresses, start=1):
                st.write(f"- Resolving: {addr}")
                try:
                    lat, lon, label = geocode_one(addr)
                    coords.append((lat, lon, label))
                    st.write(f"  ↳ OK: {label}  ({lat:.6f}, {lon:.6f})")
                except Exception as e:
                    failed.append(addr)
                    st.write(f"  ↳ FAILED: {e}")
                time.sleep(1.0)
                progress.progress(i / n, text=f"Geocoding {i}/{n}…")
            progress.empty()

            if failed:
                st.error("The following addresses could not be resolved:\n\n- " + "\n- ".join(failed))
                st.session_state.run_optimize = False
                st.stop()

            # OSRM table: durations (s) + distances (m)
            st.write("Fetching road travel time & distance from OSRM…")
            used_fallback = False
            try:
                durations_s, distances_m = osrm_table(coords, profile="driving")
                cost_matrix = np.array(durations_s, dtype=float)  # minimize time
            except Exception as e:
                st.warning(f"OSRM failed ({e}). Falling back to straight-line distances only.")
                distances_m = build_distance_matrix(coords)  # meters
                cost_matrix = np.array(distances_m, dtype=float)  # minimize distance
                used_fallback = True

            # Optimize (Held–Karp)
            st.write("Running Held–Karp (optimal)…")
            route, total_cost = held_karp_loop(cost_matrix)

            # Compute total time and distance along the chosen route
            def sum_along_route(mat: list[list[float]], route_idx: list[int]) -> float:
                total = 0.0
                for a, b in zip(route_idx[:-1], route_idx[1:]):
                    total += mat[a][b]
                return total

            if used_fallback:
                total_seconds = None
                total_meters = sum_along_route(distances_m, route)
            else:
                total_seconds = sum_along_route(durations_s, route)
                total_meters = sum_along_route(distances_m, route)

                        # Try to fetch actual road path for the optimized order
            road_path = None
            try:
                road_path = osrm_route_path(coords, route, profile="driving")
            except Exception as e:
                st.warning(f"OSRM /route failed to fetch road path ({e}). Showing straight segments instead.")

            # Save to state
            st.session_state.last_coords = coords
            st.session_state.last_route = route
            st.session_state.last_total_seconds = total_seconds or 0.0
            st.session_state.last_total_meters = total_meters
            st.session_state.used_fallback = used_fallback
            st.session_state.last_road_path = road_path or []
            st.session_state.has_results = True

            st.session_state.run_optimize = False
            st.rerun()


    except Exception as e:
        st.session_state.run_optimize = False
        st.exception(e)

# ---------------- Render results ----------------
if st.session_state.has_results and st.session_state.last_coords and st.session_state.last_route:
    coords = st.session_state.last_coords
    route = st.session_state.last_route
    total_seconds = st.session_state.last_total_seconds
    total_meters = st.session_state.last_total_meters
    used_fallback = st.session_state.used_fallback

    # Geocoded table
    st.markdown("**Geocoded points (lat, lon, label):**")
    st.dataframe(
        [(i, lat, lon, label) for i, (lat, lon, label) in enumerate(coords)],
        hide_index=True,
        use_container_width=True,
        column_config={
            0: st.column_config.NumberColumn("#"),
            1: st.column_config.NumberColumn("Lat"),
            2: st.column_config.NumberColumn("Lon"),
            3: st.column_config.TextColumn("Label"),
        },
    )

    # Ordered loop
    st.success("Optimal loop computed.")
    st.markdown("**Ordered loop (start at Home, return to Home):**")
    for idx, node in enumerate(route):
        label = coords[node][2]
        if idx == 0:
            st.write(f"{idx}. Home — {label}")
        elif idx == len(route) - 1:
            st.write(f"{idx}. Return to Home")
        else:
            st.write(f"{idx}. Stop — {label}")

    # Totals
    if used_fallback:
        st.caption("OSRM was unavailable. Optimization minimized straight-line distance.")
        st.write(f"**Total distance:** {total_meters/1000.0:.2f} km")
    else:
        st.write(f"**Total drive time:** {total_seconds/60.0:.1f} minutes")
        st.write(f"**Total distance:** {total_meters/1000.0:.2f} km")

    # Map (prefer OSRM road path)
    st.markdown("**Map preview (road path when available):**")
    road_path = st.session_state.get("last_road_path", [])
    render_route_map_osrm(coords, route, road_path=road_path)

    # Google Maps deep link (ordered waypoints)
    from urllib.parse import quote_plus

    def google_maps_link(coords_list: List[Tuple[float, float, str]], route_idx: List[int]) -> str:
        """
        Build a Google Maps directions URL with ordered waypoints.
        Uses api=1 form: origin, destination, waypoints (lat,lon).
        """
        lat0, lon0, _ = coords_list[route_idx[0]]
        latN, lonN, _ = coords_list[route_idx[-1]]
        origin = f"{lat0:.6f},{lon0:.6f}"
        destination = f"{latN:.6f},{lonN:.6f}"
        if len(route_idx) > 2:
            wp = [f"{coords_list[i][0]:.6f},{coords_list[i][1]:.6f}" for i in route_idx[1:-1]]
            waypoints = quote_plus("|".join(wp))
            return f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&waypoints={waypoints}&travelmode=driving"
        else:
            return f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode=driving"

    gmaps_url = google_maps_link(coords, route)
    st.link_button("Open in Google Maps (optimized order)", gmaps_url)


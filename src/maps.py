# src/maps.py
from typing import List, Tuple, Optional
import folium
from streamlit_folium import st_folium

def render_route_map(
    coords: List[Tuple[float, float, str]],
    route: List[int],
    height: int = 480
) -> None:
    """
    Basic map: numbered markers + straight segments between visited points.
    """
    lats = [coords[i][0] for i in route]
    lons = [coords[i][1] for i in route]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)

    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=12, control_scale=True)

    for seq, idx in enumerate(route):
        lat, lon, label = coords[idx]
        folium.Marker(
            location=[lat, lon],
            tooltip=f"{seq}. {label}",
            popup=f"{seq}. {label}",
        ).add_to(fmap)

    folium.PolyLine(locations=list(zip(lats, lons)), weight=4).add_to(fmap)
    st_folium(fmap, width=None, height=height)


def render_route_map_osrm(
    coords: List[Tuple[float, float, str]],
    route: List[int],
    road_path: Optional[List[Tuple[float, float]]] = None,
    height: int = 480
) -> None:
    """
    Map with numbered markers; draw OSRM road_path if provided, else fall back to straight lines.
    """
    # Center
    if road_path and len(road_path) >= 2:
        center_lat = sum(lat for lat, _ in road_path) / len(road_path)
        center_lon = sum(lon for _, lon in road_path) / len(road_path)
    else:
        lats = [coords[i][0] for i in route]
        lons = [coords[i][1] for i in route]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)

    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=12, control_scale=True)

    # Markers
    for seq, idx in enumerate(route):
        lat, lon, label = coords[idx]
        folium.Marker(
            location=[lat, lon],
            tooltip=f"{seq}. {label}",
            popup=f"{seq}. {label}",
        ).add_to(fmap)

    # Path
    if road_path and len(road_path) >= 2:
        folium.PolyLine(locations=road_path, weight=5).add_to(fmap)
    else:
        # fallback straight segments
        lats = [coords[i][0] for i in route]
        lons = [coords[i][1] for i in route]
        folium.PolyLine(locations=list(zip(lats, lons)), weight=4).add_to(fmap)

    st_folium(fmap, width=None, height=height)

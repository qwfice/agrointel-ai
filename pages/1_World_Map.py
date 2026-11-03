"""World map — real Earth Engine crop-suitability layer, any country.

Country search is real: picking a country re-runs the suitability
computation for its actual boundary, nothing is precomputed/hardcoded
per country. Linking a map click to the detailed Streamlit comparison
page is a future step (see GOALS.md).
"""

from __future__ import annotations

import sys
from pathlib import Path

import ee
import folium
import streamlit as st
from streamlit_folium import st_folium

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.geo.gee import init
from src.geo.suitability import (
    COUNTRY_NAME,
    build_suitability_image,
    country_bounds_latlon,
    list_country_names,
)

st.set_page_config(page_title="AGROINTEL AI — World Map", layout="wide")

st.title("World Map — Crop Suitability")
st.caption(
    "A real Earth Engine computation, not a mockup — combines recent precipitation (GPM), "
    "terrain slope (SRTM), and soil moisture (SMAP) into a suitability layer, computed live "
    "for whichever country you pick below."
)
st.info(
    "This is an early, simplified suitability model (equal-weighted precipitation/slope/"
    "soil-moisture) — not yet the validated agronomic model from the main app. See GOALS.md "
    "for what's still missing (click-to-detail, more locations)."
)

init()


@st.cache_data(ttl=3600)
def _country_names() -> list[str]:
    return list_country_names()


country = st.selectbox("Country", options=_country_names(), index=_country_names().index(COUNTRY_NAME))


def _add_ee_layer(folium_map: folium.Map, ee_image: ee.Image, vis: dict, name: str) -> None:
    """Standard Earth Engine + folium pattern (geemap's wrapper has a
    version-incompatible dependency right now, so this talks to EE
    directly instead)."""
    map_id = ee.Image(ee_image).getMapId(vis)
    folium.raster_layers.TileLayer(
        tiles=map_id["tile_fetcher"].url_format,
        attr="Google Earth Engine",
        name=name,
        overlay=True,
        control=True,
    ).add_to(folium_map)


with st.spinner(f"Computing live suitability layer for {country} from Earth Engine..."):
    suitability_img, region = build_suitability_image(country_name=country)
    bounds = country_bounds_latlon(region)

    vis_params = {
        "min": 0,
        "max": 100,
        "palette": ["d73027", "fee08b", "1a9850"],  # red -> yellow -> green
    }

    m = folium.Map(tiles="OpenStreetMap")
    # max_zoom caps how far OUT fit_bounds can zoom for very large countries
    # (e.g. the US) — at extremely low zoom the suitability tiles can take
    # a moment to render; capping avoids starting at that zoom level.
    m.fit_bounds(bounds, max_zoom=5)
    _add_ee_layer(m, suitability_img, vis_params, "Crop suitability (0-100)")
    folium.GeoJson(
        region.getInfo(), name=f"{country} boundary", style_function=lambda _: {"color": "white", "fillOpacity": 0}
    ).add_to(m)
    folium.LayerControl().add_to(m)

st.caption(f"Pan and zoom the map below — this is {country}, live-computed, not a static image.")
st.caption("Legend: red = low suitability, yellow = medium, green = high (0-100 scale).")
st_folium(m, height=650, width=None, returned_objects=[])

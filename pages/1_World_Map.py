"""World map — real Earth Engine crop-suitability layer (proof of concept).

Malaysia only, for now (research plan Location 3: Cameron Highlands).
Country search and linking a map click to the detailed Streamlit
comparison page are future steps (see GOALS.md).
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.geo.gee import init
from src.geo.suitability import COUNTRY_NAME, build_suitability_image

st.set_page_config(page_title="AGROINTEL AI — World Map", layout="wide")

st.title("World Map — Crop Suitability")
st.caption(
    "Proof of concept: a real Earth Engine computation, not a mockup — combines recent "
    "precipitation (GPM), terrain slope (SRTM), and soil moisture (SMAP) into a suitability "
    "layer, computed live over the whole country."
)
st.info(
    "This is an early, simplified suitability model (equal-weighted precipitation/slope/"
    "soil-moisture) — not yet the validated agronomic model from the main app. It proves the "
    "Earth Engine approach works at country scale; see GOALS.md for what's still missing "
    "(country search, click-to-detail, more locations)."
)

with st.spinner(f"Computing live suitability layer for {COUNTRY_NAME} from Earth Engine..."):
    init()
    suitability_img, region = build_suitability_image()

    import ee
    import folium
    from streamlit_folium import st_folium

    vis_params = {
        "min": 0,
        "max": 100,
        "palette": ["d73027", "fee08b", "1a9850"],  # red -> yellow -> green
    }

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

    m = folium.Map(location=[4.2, 108.3], zoom_start=6, tiles="OpenStreetMap")
    _add_ee_layer(m, suitability_img, vis_params, "Crop suitability (0-100)")
    folium.GeoJson(
        region.getInfo(), name="Malaysia boundary", style_function=lambda _: {"color": "white", "fillOpacity": 0}
    ).add_to(m)
    folium.LayerControl().add_to(m)

st.caption(f"Pan and zoom the map below — this is {COUNTRY_NAME}, live-computed, not a static image.")
st.caption("Legend: red = low suitability, yellow = medium, green = high (0-100 scale).")
st_folium(m, height=650, width=None, returned_objects=[])

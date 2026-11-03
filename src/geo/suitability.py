"""Real Google Earth Engine crop-suitability layer, proof-of-concept scope:
Malaysia (research plan Location 3 — Cameron Highlands).

Combines three real GEE-hosted datasets into a 0-100 suitability score:
  - Precipitation (GPM IMERG monthly, recent period)
  - Terrain slope (derived from SRTM elevation — gentler land is easier
    and safer to farm)
  - Surface soil moisture (NASA/USDA SMAP 10km)

This is a deliberately simple first-pass model — a real agronomic
suitability model needs soil type, land cover, and crop-specific
requirements too (see GOALS.md). It exists to prove the real-time,
whole-country Earth Engine computation works, not as a finished
suitability product.
"""

from __future__ import annotations

import ee

COUNTRY_NAME = "Malaysia"

# Earth Engine datasets used:
GPM_COLLECTION = "NASA/GPM_L3/IMERG_MONTHLY_V07"
SRTM_IMAGE = "USGS/SRTMGL1_003"
SMAP_COLLECTION = "NASA/SMAP/SPL4SMGP/008"
COUNTRY_BOUNDARIES = "USDOS/LSIB_SIMPLE/2017"

# Recent period for precipitation/soil moisture — kept short so this
# reflects current conditions, not a multi-year average.
RECENT_MONTHS = 6


def country_boundary(country_name: str = COUNTRY_NAME) -> ee.Geometry:
    countries = ee.FeatureCollection(COUNTRY_BOUNDARIES)
    match = countries.filter(ee.Filter.eq("country_na", country_name))
    return match.geometry()


def _normalize(image: ee.Image, band: str, low: float, high: float) -> ee.Image:
    """Clamp then rescale a band to 0-1 over [low, high]."""
    clamped = image.select(band).clamp(low, high)
    return clamped.subtract(low).divide(high - low).rename(f"{band}_norm")


def build_suitability_image(region: ee.Geometry | None = None) -> tuple[ee.Image, ee.Geometry]:
    """Build the real suitability image for the given region (default: Malaysia).

    Returns:
        (suitability_image, region) — suitability_image has a single band
        "suitability" in [0, 100].
    """
    region = region or country_boundary()
    end = ee.Date(ee.Date(ee.Image(ee.ImageCollection(GPM_COLLECTION).sort("system:time_start", False).first()).get("system:time_start")))
    start = end.advance(-RECENT_MONTHS, "month")

    precip = (
        ee.ImageCollection(GPM_COLLECTION)
        .filterDate(start, end)
        .select("precipitation")
        .mean()
        .rename("precip")
    )
    # GPM IMERG monthly precip is in mm/hr; realistic range for a tropical
    # climate like Malaysia's is roughly 0-1 mm/hr monthly mean.
    precip_norm = _normalize(precip, "precip", 0, 1)

    slope = ee.Terrain.slope(ee.Image(SRTM_IMAGE)).rename("slope")
    # Gentler slope = more suitable, so invert: 0 degrees -> 1.0, 30+ -> 0.0
    slope_norm = _normalize(slope, "slope", 0, 30)
    slope_suitability = ee.Image(1).subtract(slope_norm).rename("slope_suit")

    # sm_surface_wetness is already a 0-1 relative-wetness band (same
    # concept as src/indicators/environmental.py's SMAP wetness indicator
    # for point locations) - no manual normalization needed.
    soil_norm = (
        ee.ImageCollection(SMAP_COLLECTION)
        .filterDate(start, end)
        .select("sm_surface_wetness")
        .mean()
        .rename("ssm_norm")
    )

    # Equal-weighted combination for this first pass — documented as a
    # simplification, not a validated agronomic weighting (see GOALS.md).
    suitability = (
        precip_norm.rename("s")
        .add(slope_suitability.rename("s"))
        .add(soil_norm.rename("s"))
        .divide(3)
        .multiply(100)
        .rename("suitability")
        .clip(region)
    )

    return suitability, region

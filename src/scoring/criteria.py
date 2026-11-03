"""Per-criterion scoring functions for the three vegetable rotation strategies
from the research plan (Section 5): conventional, legume-integrated, and
soil-conservation.

Two criteria (climate_resilience, erosion_reduction) are driven by the real
environmental indicators computed in src/indicators/environmental.py.

The other four (soil_health_potential, water_use_suitability,
pest_disease_interruption, economic_suitability) use static baseline scores
from general agronomic knowledge, since scoring them from real data would
need FAO crop-water-requirement data, local market prices, and local pest
records we haven't integrated yet (see GOALS.md). Each baseline is commented
with its rationale and should be treated as a starting point a local
agronomist would need to validate, not a scientific measurement.
"""

from __future__ import annotations

STRATEGIES = ("conventional", "legume", "soil_conservation")

# --- Static baselines (0-100), per strategy -------------------------------
# Rationale, per research plan Section 5:
#   conventional      = Tomato -> Cabbage -> Lettuce (baseline, no soil-building crop)
#   legume            = Tomato -> Beans -> Cabbage (nitrogen-fixing legume added)
#   soil_conservation = Tomato -> Cover Crop -> Leafy Vegetables (bare soil minimized)

SOIL_HEALTH_POTENTIAL_BASE = {
    # Legumes fix nitrogen; cover crops add the most organic residue and
    # minimize bare-soil periods. Conventional has no soil-building crop.
    "conventional": 30,
    "legume": 70,
    "soil_conservation": 85,
}

PEST_DISEASE_INTERRUPTION_BASE = {
    # More distinct plant families in the sequence disrupts pest/disease
    # cycles more. Cover crops (often grass/legume mixes) add the most
    # family diversity; legumes add one new family; conventional stays
    # within similar vegetable families.
    "conventional": 45,
    "legume": 70,
    "soil_conservation": 75,
}

WATER_USE_SUITABILITY_BASE = {
    # Tomato/cabbage/lettuce are all moderate-to-high water users grown
    # back-to-back. Beans have somewhat lower water demand. Cover crops
    # (e.g. drought-tolerant grasses/legumes) are typically the lowest.
    # NOTE: this starting point is a static assumption pending real FAO
    # crop-water-requirement data - but see water_use_suitability() below,
    # which adjusts it with the real NASA rainfall anomaly when available.
    "conventional": 40,
    "legume": 55,
    "soil_conservation": 65,
}

# How much each strategy's water-use score moves with real observed
# rainfall anomalies: a conventional rotation of moderate-to-high water
# users is modeled as most exposed to a dry or wet anomaly; a low-water
# cover-crop rotation is modeled as least exposed. This vulnerability
# scaling (not the rainfall data itself) is the agronomic assumption here.
_WATER_VULNERABILITY = {"conventional": 1.0, "legume": 0.7, "soil_conservation": 0.4}

ECONOMIC_SUITABILITY_BASE = {
    # Conventional vegetables have established markets and immediate sale
    # value every season. Legumes (beans) usually have a market too, just
    # smaller. A cover crop is typically not harvested/sold at all, so it
    # has the lowest direct economic return (though it may reduce future
    # input costs - not counted here).
    # NOTE: static assumption pending real local market price data.
    "conventional": 70,
    "legume": 55,
    "soil_conservation": 35,
}

# --- Data-driven criteria ---------------------------------------------------
# How much each strategy's resilience/erosion protection is eroded by harsher
# observed conditions, relative to its best-case baseline. Lower = more
# vulnerable to anomalies. These sensitivity factors (not the underlying
# climate data) are the agronomic assumption here: a cover crop buffers
# temperature/moisture extremes and physically protects soil, so it is
# modeled as least sensitive; a monoculture-style rotation with bare
# periods is modeled as most sensitive.
_CLIMATE_VULNERABILITY = {"conventional": 1.0, "legume": 0.6, "soil_conservation": 0.3}
_EROSION_VULNERABILITY = {"conventional": 1.0, "legume": 0.5, "soil_conservation": 0.15}

_CLIMATE_RESILIENCE_BASE = {"conventional": 40, "legume": 60, "soil_conservation": 80}
_EROSION_REDUCTION_BASE = {"conventional": 30, "legume": 55, "soil_conservation": 90}


def climate_resilience(strategy: str, indicators: dict) -> float:
    """Resilience score (0-100), penalized by real observed dry-spell length
    and temperature anomaly magnitude, scaled by the strategy's assumed
    vulnerability.
    """
    base = _CLIMATE_RESILIENCE_BASE[strategy]
    dry_spell_penalty = indicators["longest_dry_spell_days"] * 1.5
    temp_penalty = abs(indicators["temp_anomaly_mean_c"]) * 4
    penalty = (dry_spell_penalty + temp_penalty) * _CLIMATE_VULNERABILITY[strategy]
    return max(0.0, min(100.0, base - penalty))


def erosion_reduction(strategy: str, indicators: dict) -> float:
    """Erosion-reduction score (0-100), penalized by how many real extreme
    rainfall days occurred, scaled by the strategy's assumed vulnerability
    (bare-soil rotations lose more protection when rain is heavy).
    """
    base = _EROSION_REDUCTION_BASE[strategy]
    penalty = indicators["extreme_rainfall_days"] * 8 * _EROSION_VULNERABILITY[strategy]
    return max(0.0, min(100.0, base - penalty))


def water_use_suitability(strategy: str, indicators: dict) -> float:
    """Water-use suitability score (0-100).

    Starts from the static agronomic baseline above, then - when a real
    rainfall anomaly is available for this location - adjusts it: a drier-
    than-normal month penalizes higher-water strategies more, a wetter-than-
    normal month helps them somewhat, scaled by the strategy's assumed water
    demand. The adjustment is deliberately capped (smaller upside than
    downside) so one wet month can't inflate a score more than a real dry
    spell can depress it. Falls back to the pure baseline when no rainfall
    anomaly is available for this location/window (real SMAP/POWER gaps
    happen) - see `criteria_confidence()` for which case applied.
    """
    base = WATER_USE_SUITABILITY_BASE[strategy]
    rain_anom_pct = indicators.get("rainfall_anomaly_pct")
    if rain_anom_pct is None:
        return float(base)
    adjustment = rain_anom_pct * 0.3 * _WATER_VULNERABILITY[strategy]
    adjustment = max(-30.0, min(15.0, adjustment))
    return max(0.0, min(100.0, base + adjustment))


def criteria_confidence(indicators: dict) -> dict[str, str]:
    """Per-criterion provenance tag: 'real_data' only where the score above is
    actually computed from real NASA-derived numbers for this request,
    'expert_baseline' where it's a static documented agronomic assumption.
    Lets the website/chat show the user exactly what's measured vs. assumed,
    instead of presenting every number with the same implied confidence.
    """
    return {
        "soil_health_potential": "expert_baseline",
        "water_use_suitability": "real_data" if indicators.get("rainfall_anomaly_pct") is not None else "expert_baseline",
        "climate_resilience": "real_data",
        "pest_disease_interruption": "expert_baseline",
        "erosion_reduction": "real_data",
        "economic_suitability": "expert_baseline",
    }


def score_all_criteria(strategy: str, indicators: dict) -> dict[str, float]:
    """All six criterion scores (0-100) for one strategy."""
    return {
        "soil_health_potential": float(SOIL_HEALTH_POTENTIAL_BASE[strategy]),
        "water_use_suitability": water_use_suitability(strategy, indicators),
        "climate_resilience": climate_resilience(strategy, indicators),
        "pest_disease_interruption": float(PEST_DISEASE_INTERRUPTION_BASE[strategy]),
        "erosion_reduction": erosion_reduction(strategy, indicators),
        "economic_suitability": float(ECONOMIC_SUITABILITY_BASE[strategy]),
    }

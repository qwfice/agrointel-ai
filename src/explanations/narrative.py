"""Generates the evidence / benefits / information-gaps / risks text the
challenge requires for each rotation strategy comparison.

Every evidence statement is built from the actual numbers in `indicators`
and `criteria_scores` (produced by src/indicators and src/scoring) — nothing
here is phrased by a language model guessing. Benefits/gaps/risks are
static per-strategy agronomic text, written by hand, not computed.
"""

from __future__ import annotations

from src.scoring.criteria import _CLIMATE_VULNERABILITY, _EROSION_VULNERABILITY, criteria_confidence

_STRATEGY_LABELS = {
    "conventional": "Conventional (Tomato -> Cabbage -> Lettuce)",
    "legume": "Legume-Integrated (Tomato -> Beans -> Cabbage)",
    "soil_conservation": "Soil-Conservation (Tomato -> Cover Crop -> Leafy Vegetables)",
}

_BENEFITS = {
    "conventional": [
        "Familiar practice with established local market channels for every crop in the sequence.",
        "No new crop types or equipment needed.",
    ],
    "legume": [
        "Beans fix atmospheric nitrogen, potentially reducing synthetic nitrogen fertilizer needs for the following crop.",
        "Adds a distinct plant family to the rotation, helping disrupt pest and disease cycles tied to continuous vegetable cropping.",
        "Beans generally have a usable market value, unlike a pure cover crop.",
    ],
    "soil_conservation": [
        "Minimizes the number of bare-soil days in the rotation, reducing wind/water erosion exposure.",
        "Adds the most organic residue to the soil of the three strategies, supporting long-term organic matter buildup.",
        "Cover crop residue buffers soil temperature and moisture extremes, which real data shows matters this season (see evidence).",
    ],
}

_GAPS = {
    "conventional": [
        "Economic suitability (70/100) is a static agronomic assumption, not derived from actual local market prices.",
        "Pest/disease interruption (45/100) is a general assumption about family diversity, not based on local pest records.",
    ],
    "legume": [
        "Soil-health potential (70/100) assumes typical nitrogen fixation; actual nitrogen contribution depends on bean variety, biomass, and residue management not modeled here (the research plan flags this explicitly).",
        "Economic suitability score is a static assumption pending real local market data.",
    ],
    "soil_conservation": [
        "Economic suitability (35/100) assumes no direct harvest value for the cover crop; if it is grazed or sold as biomass locally, this score understates its value.",
    ],
}

_WATER_GAP_NO_DATA = (
    "Water-use suitability couldn't be adjusted with a real rainfall anomaly for this location/window "
    "(a real NASA data gap, not an error) - it's using its static agronomic starting-point assumption "
    "for now, pending real FAO crop-water-requirement data for a fuller picture."
)
_WATER_GAP_WITH_DATA = (
    "Water-use suitability's starting point is still a static agronomic assumption about this "
    "strategy's crops - the real rainfall anomaly only nudges it up or down for this season's actual "
    "conditions, it doesn't replace the underlying assumption. Real local FAO crop-water-requirement "
    "data would give a fuller picture."
)

_RISKS = {
    "conventional": [
        "Real computed data shows this strategy scored weakest on climate resilience (modeled as most vulnerable to the season's dry spell and temperature anomaly) and erosion reduction — a local agronomist should assess whether this specific field can tolerate that exposure.",
    ],
    "legume": [
        "If the bean variety or planting density is wrong for local conditions, the assumed nitrogen and water-use benefits may not materialize — needs local agronomic review before adoption.",
    ],
    "soil_conservation": [
        "Lowest economic suitability of the three strategies in this model — a farmer prioritizing near-term cash flow may find this unacceptable despite its soil/climate advantages; needs a local cost-benefit check, including any conservation incentive payments not modeled here.",
    ],
}


def evidence_for(strategy: str, criteria_scores: dict[str, float], indicators: dict) -> list[str]:
    """Build evidence statements that cite the actual computed numbers."""
    evidence = []

    dry_spell = indicators["longest_dry_spell_days"]
    temp_anom = indicators["temp_anomaly_mean_c"]
    climate_vuln = _CLIMATE_VULNERABILITY[strategy]
    evidence.append(
        f"Climate resilience scored {criteria_scores['climate_resilience']:.1f}/100. Real observed "
        f"conditions: an {dry_spell:.0f}-day dry spell and a {temp_anom:+.2f}C mean temperature anomaly "
        f"vs. the 5-year climatology. This strategy is modeled with a {climate_vuln:.1f}x vulnerability "
        f"factor to those anomalies (1.0 = most vulnerable, 0.3 = least)."
    )

    extreme_days = indicators["extreme_rainfall_days"]
    extreme_threshold = indicators.get("extreme_rainfall_threshold_mm")
    erosion_vuln = _EROSION_VULNERABILITY[strategy]
    threshold_clause = (
        f" ('extreme' here means over {extreme_threshold:.1f}mm/day, this location's own "
        f"historical 90th-percentile.)"
        if extreme_threshold is not None
        else ""
    )
    evidence.append(
        f"Erosion reduction scored {criteria_scores['erosion_reduction']:.1f}/100. Real observed "
        f"conditions included {extreme_days:.0f} day(s) exceeding the historical 90th-percentile "
        f"rainfall threshold.{threshold_clause} This strategy is modeled with a {erosion_vuln:.1f}x "
        f"erosion-protection vulnerability factor."
    )

    rain_anom = indicators.get("rainfall_anomaly_pct")
    if rain_anom is not None:
        direction = "wetter" if rain_anom >= 0 else "drier"
        evidence.append(
            f"Water-use suitability scored {criteria_scores['water_use_suitability']:.1f}/100, starting "
            f"from a static agronomic baseline and adjusted using the real observed rainfall for this "
            f"location: {abs(rain_anom):.1f}% {direction} than this calendar month's 5-year average."
        )
    else:
        evidence.append(
            "Water-use suitability couldn't be adjusted with a real rainfall anomaly for this "
            "location/window (a real NASA data coverage gap) - it's using its static agronomic "
            "baseline only, see information gaps."
        )

    wetness = indicators["soil_moisture_relative_wetness_mean"]
    if wetness is None:
        evidence.append(
            "Real SMAP soil moisture could not be retrieved for this location/date (a real "
            "coverage gap, not an error) — not factored into water-use scoring, which remains "
            "a static assumption regardless (see information gaps)."
        )
    else:
        evidence.append(
            f"For reference, real SMAP soil moisture at this location was a relative wetness of "
            f"{wetness:.2f} (0=driest SMAP can measure, 1=wettest) — not yet factored into "
            f"water-use scoring, which remains a static assumption (see information gaps)."
        )

    return evidence


def build_comparison(strategy: str, criteria_scores: dict[str, float], overall_score: float, indicators: dict) -> dict:
    """Full comparison entry for one strategy: label, score, evidence, benefits, gaps, risks."""
    water_gap = _WATER_GAP_WITH_DATA if indicators.get("rainfall_anomaly_pct") is not None else _WATER_GAP_NO_DATA
    return {
        "strategy": strategy,
        "label": _STRATEGY_LABELS[strategy],
        "overall_score": overall_score,
        "criteria_scores": criteria_scores,
        "criteria_confidence": criteria_confidence(indicators),
        "evidence": evidence_for(strategy, criteria_scores, indicators),
        "benefits": _BENEFITS[strategy],
        "information_gaps": _GAPS[strategy] + [water_gap],
        "risks": _RISKS[strategy],
    }

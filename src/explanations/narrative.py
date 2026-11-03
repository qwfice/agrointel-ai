"""Generates the evidence / benefits / information-gaps / risks text the
challenge requires for each rotation strategy comparison.

Every evidence statement is built from the actual numbers in `indicators`
and `criteria_scores` (produced by src/indicators and src/scoring) — nothing
here is phrased by a language model guessing. Benefits/gaps/risks are
static per-strategy agronomic text, written by hand, not computed.
"""

from __future__ import annotations

from src.scoring.criteria import _CLIMATE_VULNERABILITY, _EROSION_VULNERABILITY

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
        "Water-use suitability (40/100) and economic suitability (70/100) are static agronomic assumptions, not derived from local FAO crop-water data or actual market prices.",
        "Pest/disease interruption (45/100) is a general assumption about family diversity, not based on local pest records.",
    ],
    "legume": [
        "Soil-health potential (70/100) assumes typical nitrogen fixation; actual nitrogen contribution depends on bean variety, biomass, and residue management not modeled here (the research plan flags this explicitly).",
        "Water-use and economic suitability scores are static assumptions pending real local data.",
    ],
    "soil_conservation": [
        "Economic suitability (35/100) assumes no direct harvest value for the cover crop; if it is grazed or sold as biomass locally, this score understates its value.",
        "Water-use suitability assumes a low-water cover crop species; actual water use depends on which cover crop is planted, which is not specified here.",
    ],
}

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
    erosion_vuln = _EROSION_VULNERABILITY[strategy]
    evidence.append(
        f"Erosion reduction scored {criteria_scores['erosion_reduction']:.1f}/100. Real observed "
        f"conditions included {extreme_days:.0f} day(s) exceeding the historical 90th-percentile "
        f"rainfall threshold. This strategy is modeled with a {erosion_vuln:.1f}x erosion-protection "
        f"vulnerability factor."
    )

    wetness = indicators["soil_moisture_relative_wetness_mean"]
    evidence.append(
        f"For reference, real SMAP soil moisture during the evaluation window averaged a relative "
        f"wetness of {wetness:.2f} (0=driest SMAP can measure, 1=wettest) — not yet factored into "
        f"water-use scoring, which remains a static assumption (see information gaps)."
    )

    return evidence


def build_comparison(strategy: str, criteria_scores: dict[str, float], overall_score: float, indicators: dict) -> dict:
    """Full comparison entry for one strategy: label, score, evidence, benefits, gaps, risks."""
    return {
        "strategy": strategy,
        "label": _STRATEGY_LABELS[strategy],
        "overall_score": overall_score,
        "criteria_scores": criteria_scores,
        "evidence": evidence_for(strategy, criteria_scores, indicators),
        "benefits": _BENEFITS[strategy],
        "information_gaps": _GAPS[strategy],
        "risks": _RISKS[strategy],
    }

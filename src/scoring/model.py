"""The weighted multi-criteria rotation-scoring model from the research plan,
Section 7: S = sum(w_i * r_i) over the six evaluation criteria.

Weights are adjustable (this is how a farmer's stated priorities are meant
to change the recommendation - see GOALS.md goal 6).
"""

from __future__ import annotations

from src.scoring.criteria import STRATEGIES, score_all_criteria

# Default weights, from the research plan's "Initial research criteria" table.
# These are explicitly described there as a starting point, not a
# scientifically established universal weighting.
DEFAULT_WEIGHTS = {
    "soil_health_potential": 0.25,
    "water_use_suitability": 0.20,
    "climate_resilience": 0.20,
    "pest_disease_interruption": 0.15,
    "erosion_reduction": 0.10,
    "economic_suitability": 0.10,
}


def weighted_score(criterion_scores: dict[str, float], weights: dict[str, float] | None = None) -> float:
    """Combine per-criterion 0-100 scores into one overall 0-100 score."""
    weights = weights or DEFAULT_WEIGHTS
    total_weight = sum(weights.values())
    return sum(criterion_scores[c] * w for c, w in weights.items()) / total_weight


def rank_strategies(indicators: dict, weights: dict[str, float] | None = None) -> list[dict]:
    """Score and rank all three rotation strategies for one location.

    Args:
        indicators: the real computed environmental indicators for that
            location (see src/indicators/environmental.py and
            scripts/compute_indicators.py's summary output).
        weights: optional override of DEFAULT_WEIGHTS (e.g. from a farmer's
            stated priorities).

    Returns:
        List of {"strategy", "overall_score", "criteria"} dicts, sorted
        highest-scoring strategy first.
    """
    results = []
    for strategy in STRATEGIES:
        criteria = score_all_criteria(strategy, indicators)
        results.append(
            {
                "strategy": strategy,
                "overall_score": weighted_score(criteria, weights),
                "criteria": criteria,
            }
        )
    return sorted(results, key=lambda r: r["overall_score"], reverse=True)

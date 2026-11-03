"""Run the weighted rotation-scoring model for Kern County, CA using the
real indicators computed by scripts/compute_indicators.py (run that first).

Usage:
    python scripts/run_scoring.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.scoring.model import DEFAULT_WEIGHTS, rank_strategies

OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

STRATEGY_LABELS = {
    "conventional": "Conventional (Tomato -> Cabbage -> Lettuce)",
    "legume": "Legume-Integrated (Tomato -> Beans -> Cabbage)",
    "soil_conservation": "Soil-Conservation (Tomato -> Cover Crop -> Leafy Veg)",
}


def main() -> None:
    indicators_path = OUT_DIR / "kern_county_indicators.csv"
    if not indicators_path.exists():
        raise SystemExit("Missing outputs/kern_county_indicators.csv. Run scripts/compute_indicators.py first.")

    indicators_df = pd.read_csv(indicators_path)
    indicators = dict(zip(indicators_df["indicator"], indicators_df["value"]))

    print("=== Rotation scoring: Kern County, CA, June 2023 conditions ===\n")
    print("Weights used:", {k: f"{v:.0%}" for k, v in DEFAULT_WEIGHTS.items()}, "\n")

    ranked = rank_strategies(indicators)

    rows = []
    for rank, result in enumerate(ranked, start=1):
        label = STRATEGY_LABELS[result["strategy"]]
        print(f"#{rank}  {label}  ->  overall score: {result['overall_score']:.1f}/100")
        for criterion, score in result["criteria"].items():
            print(f"      {criterion:28s} {score:5.1f}")
        print()
        rows.append({"rank": rank, "strategy": result["strategy"], "overall_score": round(result["overall_score"], 1), **{k: round(v, 1) for k, v in result["criteria"].items()}})

    out_path = OUT_DIR / "kern_county_rotation_scores.csv"
    pd.DataFrame(rows).to_csv(out_path, index=False)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()

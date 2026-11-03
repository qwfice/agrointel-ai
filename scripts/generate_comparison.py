"""Generate the full rotation-strategy comparison report (score, evidence,
benefits, information gaps, risks) for Kern County, CA, and write it to
outputs/kern_county_comparison.md.

Requires scripts/compute_indicators.py to have been run first.

Usage:
    python scripts/generate_comparison.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.explanations.narrative import build_comparison
from src.scoring.model import DEFAULT_WEIGHTS, rank_strategies

OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def render_markdown(ranked_comparisons: list[dict], weights: dict[str, float]) -> str:
    lines = [
        "# Crop Rotation Strategy Comparison — Kern County, CA",
        "",
        "Evaluation window: June 2023 (real NASA POWER / SMAP / GPM data).",
        "",
        "Weights used: " + ", ".join(f"{k} {v:.0%}" for k, v in weights.items()),
        "",
        "> This is decision support, not a guarantee of crop outcomes. Static assumptions are "
        "called out explicitly below each strategy — a local agronomist or farmer's own "
        "knowledge should validate them before use.",
        "",
    ]

    for rank, comp in enumerate(ranked_comparisons, start=1):
        lines += [
            f"## #{rank}. {comp['label']} — {comp['overall_score']:.1f}/100",
            "",
            "**Criterion scores:**",
            "",
        ]
        for criterion, score in comp["criteria_scores"].items():
            lines.append(f"- {criterion.replace('_', ' ')}: {score:.1f}/100")
        lines += ["", "**Supporting evidence:**", ""]
        lines += [f"- {e}" for e in comp["evidence"]]
        lines += ["", "**Benefits:**", ""]
        lines += [f"- {b}" for b in comp["benefits"]]
        lines += ["", "**Information gaps:**", ""]
        lines += [f"- {g}" for g in comp["information_gaps"]]
        lines += ["", "**Risks / needs local review:**", ""]
        lines += [f"- {r}" for r in comp["risks"]]
        lines += ["", "---", ""]

    return "\n".join(lines)


def main() -> None:
    indicators_path = OUT_DIR / "kern_county_indicators.csv"
    if not indicators_path.exists():
        raise SystemExit("Missing outputs/kern_county_indicators.csv. Run scripts/compute_indicators.py first.")

    indicators_df = pd.read_csv(indicators_path)
    indicators = dict(zip(indicators_df["indicator"], indicators_df["value"]))

    ranked = rank_strategies(indicators)
    comparisons = [
        build_comparison(r["strategy"], r["criteria"], r["overall_score"], indicators) for r in ranked
    ]

    markdown = render_markdown(comparisons, DEFAULT_WEIGHTS)
    out_path = OUT_DIR / "kern_county_comparison.md"
    out_path.write_text(markdown)
    print(markdown)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()

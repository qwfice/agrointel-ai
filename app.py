"""AGROINTEL AI — minimal Streamlit interface (goal 5).

Shows the real computed indicators, the weighted rotation scores, and the
full evidence/benefits/gaps/risks comparison for Kern County, CA, reusing
the exact same code as scripts/compute_indicators.py, run_scoring.py, and
generate_comparison.py — no logic is duplicated here.

Single location, fixed weights for now (location picker and adjustable
weight sliders are goal 6).

Run with:
    streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.explanations.narrative import build_comparison
from src.scoring.model import DEFAULT_WEIGHTS, rank_strategies

OUT_DIR = Path(__file__).resolve().parent / "outputs"

st.set_page_config(page_title="AGROINTEL AI", layout="wide")

st.title("AGROINTEL AI")
st.caption("Explainable crop-rotation decision support — built on real NASA Earth observation data.")
st.info(
    "This is decision support, not a guarantee of crop outcomes. Scores combine real "
    "computed environmental indicators with documented agronomic assumptions — see each "
    "strategy's 'Information gaps' below before acting on this."
)

indicators_path = OUT_DIR / "kern_county_indicators.csv"
if not indicators_path.exists():
    st.error(
        "No indicators found. Run `python scripts/compute_indicators.py` first "
        "(after `explore_power_data.py` and `explore_smap_gpm_data.py`)."
    )
    st.stop()

indicators_df = pd.read_csv(indicators_path)
indicators = dict(zip(indicators_df["indicator"], indicators_df["value"]))

st.header("Kern County, CA — June 2023 conditions")
cols = st.columns(5)
cols[0].metric("Temp anomaly (mean)", f"{indicators['temp_anomaly_mean_c']:+.2f} C")
cols[1].metric("Temp anomaly (max)", f"{indicators['temp_anomaly_max_c']:+.2f} C")
cols[2].metric("Longest dry spell", f"{indicators['longest_dry_spell_days']:.0f} days")
cols[3].metric("Extreme rainfall days", f"{indicators['extreme_rainfall_days']:.0f}")
cols[4].metric("Soil moisture wetness", f"{indicators['soil_moisture_relative_wetness_mean']:.2f}")
st.caption("Temp/rainfall anomalies vs. 5-year NASA POWER climatology. Soil moisture from real SMAP data (0=driest, 1=wettest SMAP can measure).")

st.header("Rotation strategy comparison")
ranked = rank_strategies(indicators)
comparisons = [build_comparison(r["strategy"], r["criteria"], r["overall_score"], indicators) for r in ranked]

chart_df = pd.DataFrame(
    {"strategy": [c["label"] for c in comparisons], "overall_score": [c["overall_score"] for c in comparisons]}
).set_index("strategy")
st.bar_chart(chart_df)

with st.expander("Weights used"):
    st.write({k: f"{v:.0%}" for k, v in DEFAULT_WEIGHTS.items()})

for rank, comp in enumerate(comparisons, start=1):
    with st.expander(f"#{rank}  {comp['label']}  —  {comp['overall_score']:.1f}/100", expanded=(rank == 1)):
        st.subheader("Criterion scores")
        score_df = pd.DataFrame(
            {"criterion": list(comp["criteria_scores"].keys()), "score": list(comp["criteria_scores"].values())}
        ).set_index("criterion")
        st.bar_chart(score_df)

        st.subheader("Supporting evidence")
        for e in comp["evidence"]:
            st.markdown(f"- {e}")

        st.subheader("Benefits")
        for b in comp["benefits"]:
            st.markdown(f"- {b}")

        st.subheader("Information gaps")
        for g in comp["information_gaps"]:
            st.markdown(f"- {g}")

        st.subheader("Risks / needs local review")
        for r in comp["risks"]:
            st.markdown(f"- {r}")

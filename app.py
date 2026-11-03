"""AGROINTEL AI — minimal Streamlit interface, with adjustable farmer
priority weights (goals 5 and 6).

Shows the real computed indicators, the weighted rotation scores, and the
full evidence/benefits/gaps/risks comparison for Kern County, CA, reusing
the exact same code as scripts/compute_indicators.py, run_scoring.py, and
generate_comparison.py — no logic is duplicated here. The sidebar sliders
let a farmer re-weight the six criteria; the app re-runs the real scoring
model (src/scoring/model.py) with those weights, it does not fake the
update.

Single location for now (a location picker is a future step).

Run with:
    streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.chat.assistant import ask, build_context
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

st.sidebar.header("Your priorities")
st.sidebar.caption("Drag to say what matters more to you. Scores and rankings below update live.")
CRITERION_LABELS = {
    "soil_health_potential": "Soil health",
    "water_use_suitability": "Water use",
    "climate_resilience": "Climate resilience",
    "pest_disease_interruption": "Pest/disease cycle break",
    "erosion_reduction": "Erosion reduction",
    "economic_suitability": "Economic return",
}
def _reset_weights() -> None:
    for criterion in CRITERION_LABELS:
        st.session_state.pop(f"weight_{criterion}", None)


st.sidebar.button("Reset to research-plan defaults", on_click=_reset_weights)

weights = {}
for criterion, label in CRITERION_LABELS.items():
    default_pct = round(DEFAULT_WEIGHTS[criterion] * 100)
    weights[criterion] = (
        st.sidebar.slider(label, min_value=0, max_value=100, value=default_pct, step=5, key=f"weight_{criterion}")
        / 100
    )
if sum(weights.values()) == 0:
    st.sidebar.warning("All priorities are at 0 — using equal weighting instead.")
    weights = {c: 1.0 for c in CRITERION_LABELS}

st.header("Kern County, CA — June 2023 conditions")
cols = st.columns(5)
cols[0].metric("Temp anomaly (mean)", f"{indicators['temp_anomaly_mean_c']:+.2f} C")
cols[1].metric("Temp anomaly (max)", f"{indicators['temp_anomaly_max_c']:+.2f} C")
cols[2].metric("Longest dry spell", f"{indicators['longest_dry_spell_days']:.0f} days")
cols[3].metric("Extreme rainfall days", f"{indicators['extreme_rainfall_days']:.0f}")
cols[4].metric("Soil moisture wetness", f"{indicators['soil_moisture_relative_wetness_mean']:.2f}")
st.caption("Temp/rainfall anomalies vs. 5-year NASA POWER climatology. Soil moisture from real SMAP data (0=driest, 1=wettest SMAP can measure).")

st.header("Rotation strategy comparison")
ranked = rank_strategies(indicators, weights)
comparisons = [build_comparison(r["strategy"], r["criteria"], r["overall_score"], indicators) for r in ranked]

chart_df = pd.DataFrame(
    {"strategy": [c["label"] for c in comparisons], "overall_score": [c["overall_score"] for c in comparisons]}
).set_index("strategy")
st.bar_chart(chart_df)

total_weight = sum(weights.values())
with st.expander("Weights currently used"):
    st.write({CRITERION_LABELS[k]: f"{v / total_weight:.0%}" for k, v in weights.items()})

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

st.sidebar.divider()
st.sidebar.header("Ask the assistant")
st.sidebar.caption("Answers are grounded only in the real data shown on this page — not a trained model, just an existing AI reading our real numbers.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for role, text in st.session_state.chat_history:
    st.sidebar.chat_message(role).write(text)

user_question = st.sidebar.chat_input("Ask about this location...")
if user_question:
    st.session_state.chat_history.append(("user", user_question))
    try:
        context = build_context("Kern County, CA (June 2023)", indicators, comparisons)
        answer = ask(user_question, context)
    except Exception as e:
        answer = f"Couldn't reach the assistant: {e}"
    st.session_state.chat_history.append(("assistant", answer))
    st.rerun()

st.header("Model limitations")
st.caption("From the research plan's own stance on uncertainty (Section 12) — applies to every strategy above, not just the ones noted individually.")
for limitation in [
    "Satellite soil-moisture observations (SMAP) have much coarser resolution than many individual vegetable fields — a single reading represents a ~9km area, not this specific farm.",
    "NASA POWER meteorological data is modeled from satellite/reanalysis sources, not a direct measurement taken at this farm.",
    "Satellite observations cannot directly measure soil nitrogen, phosphorus, or organic matter content — soil-health scores are agronomic assumptions, not lab measurements.",
    "Crop rotation effects (soil health, erosion) typically take multiple growing seasons to become measurable — a single season's data is a starting signal, not proof a strategy worked.",
    "Economic suitability scores need real local market and price data to be reliable, which is not yet integrated.",
    "Pest and disease interruption scores need local pest/disease records to be reliable, which is not yet integrated.",
]:
    st.markdown(f"- {limitation}")
st.warning("AGROINTEL AI provides decision support, not guaranteed crop outcomes. A local agronomist or the farmer's own field knowledge should validate every recommendation above.")

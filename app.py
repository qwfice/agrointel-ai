"""AGROINTEL AI — minimal Streamlit interface, with adjustable farmer
priority weights (goals 5 and 6) and a live, any-location data pull.

Shows real computed indicators, the weighted rotation scores, and the full
evidence/benefits/gaps/risks comparison for whatever location you pick —
reusing the exact same code as scripts/compute_indicators.py, run_scoring.py,
and generate_comparison.py, no logic is duplicated here. The sidebar sliders
let a farmer re-weight the six criteria; the app re-runs the real scoring
model (src/scoring/model.py) with those weights, it does not fake the
update.

Location indicators are live-fetched from real NASA POWER (fast) and a
single recent day of SMAP (slower, ~30-60s) via src/indicators/live.py —
see that module's docstring for why SMAP is one day, not a 30-day average,
for arbitrary locations.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.chat.assistant import ask, build_context
from src.explanations.narrative import build_comparison
from src.indicators.live import fetch_and_compute_indicators
from src.scoring.model import DEFAULT_WEIGHTS, rank_strategies

st.set_page_config(page_title="AGROINTEL AI", layout="wide")

st.title("AGROINTEL AI")
st.caption("Explainable crop-rotation decision support — built on real NASA Earth observation data.")
st.info(
    "This is decision support, not a guarantee of crop outcomes. Scores combine real "
    "computed environmental indicators with documented agronomic assumptions — see each "
    "strategy's 'Information gaps' below before acting on this."
)

PRESET_LOCATIONS = {
    "Kern County, CA, USA": (35.3733, -119.0187),
    "Punjab, India": (30.9010, 75.8573),
    "Cameron Highlands, Malaysia": (4.4696, 101.3818),
    "Custom coordinates": None,
}

st.header("Pick a location")
preset = st.selectbox("Location", options=list(PRESET_LOCATIONS))
if preset == "Custom coordinates":
    coord_cols = st.columns(2)
    lat = coord_cols[0].number_input("Latitude", min_value=-90.0, max_value=90.0, value=35.3733, format="%.4f")
    lon = coord_cols[1].number_input("Longitude", min_value=-180.0, max_value=180.0, value=-119.0187, format="%.4f")
    location_label = f"Custom location ({lat:.4f}, {lon:.4f})"
else:
    lat, lon = PRESET_LOCATIONS[preset]
    location_label = preset

load_clicked = st.button("Load real NASA data for this location")


@st.cache_data(show_spinner=False, ttl=3600)
def _cached_fetch(lat: float, lon: float) -> dict:
    return fetch_and_compute_indicators(lat, lon)


# Only fetch on an explicit click, or on first load (nothing cached yet).
# Changing the preset/coordinate inputs alone does NOT trigger a re-fetch -
# that would re-run the slow SMAP pull on every widget interaction.
should_fetch = load_clicked or "current_indicators" not in st.session_state
if should_fetch:
    with st.spinner(f"Fetching real NASA POWER and SMAP data for {location_label}... (SMAP can take ~30-60s)"):
        try:
            st.session_state.current_indicators = _cached_fetch(lat, lon)
            st.session_state.current_location = (lat, lon)
            st.session_state.current_location_label = location_label
            st.session_state.chat_history = []  # reset chat when location changes
        except Exception as e:
            st.error(f"Couldn't fetch real data for this location: {e}")
            st.stop()

if "current_indicators" not in st.session_state:
    st.info("Pick a location above and click \"Load real NASA data\" to begin.")
    st.stop()

indicators = st.session_state.current_indicators
location_label = st.session_state.current_location_label

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

st.header(f"{location_label} — current conditions")
cols = st.columns(5)
cols[0].metric("Temp anomaly (mean)", f"{indicators['temp_anomaly_mean_c']:+.2f} C")
cols[1].metric("Temp anomaly (max)", f"{indicators['temp_anomaly_max_c']:+.2f} C")
cols[2].metric("Longest dry spell", f"{indicators['longest_dry_spell_days']:.0f} days")
cols[3].metric("Extreme rainfall days", f"{indicators['extreme_rainfall_days']:.0f}")
wetness = indicators["soil_moisture_relative_wetness_mean"]
cols[4].metric("Soil moisture wetness", f"{wetness:.2f}" if wetness is not None else "N/A")
st.caption(
    "Temp/rainfall anomalies vs. 5-year NASA POWER climatology, last 30 days. Soil moisture: most "
    "recent available real SMAP reading (0=driest, 1=wettest SMAP can measure) — a single-day "
    "snapshot for this location, N/A if SMAP had no coverage in the lookback window."
)

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
        context = build_context(location_label, indicators, comparisons)
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

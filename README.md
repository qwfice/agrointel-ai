# AGROINTEL AI

An explainable AI-powered crop-rotation and climate-resilience decision-support platform, built for the NASA Space Apps Challenge (Crop Rotation / Soil Health track).

AGROINTEL AI combines real NASA Earth observation data with local soil, crop, and farmer-priority information to compare vegetable crop-rotation strategies and explain the reasoning behind each recommendation. Currently integrated: NASA POWER (meteorology), SMAP (soil moisture), and GPM (precipitation). MODIS and Landsat are named in the original research plan as future data sources, not yet built.

Project origin: [`AGROINTEL AI — Research Plan`](docs/AGROINTEL_AI_Research_Plan.pdf), which sets out the background, objectives, datasets, methodology, and evaluation criteria this build follows.

**This is decision support, not a guarantee of crop outcomes.** Scores combine real computed environmental data with documented agronomic assumptions that still need local/expert validation — see [GOALS.md](GOALS.md) and the app's own "Model limitations" section for specifics.

## Status

7 of 7 goals done. See [GOALS.md](GOALS.md) for the gaps identified between the research plan and an actual working tool, and [PLAN.md](PLAN.md) for the running log of what's been proposed and built at each step.

## Running it

```bash
source .venv/bin/activate
pip install -r requirements.txt
python scripts/explore_power_data.py        # pulls NASA POWER data
python scripts/explore_smap_gpm_data.py     # pulls NASA SMAP + GPM data
python scripts/compute_indicators.py        # computes real environmental indicators
streamlit run app.py                        # the interactive app
```

# Goals

These are the gaps between the original research plan (`docs/AGROINTEL_AI_Research_Plan.pdf`) and an actual working decision-support tool, turned into concrete build goals. Each one will get its own written plan (see workflow below) before any code is changed.

- [x] **Pull real NASA data.** Nothing in the research plan has touched a real NASA dataset yet. Goal: working integrations with NASA POWER (meteorology) at minimum, then SMAP (soil moisture) and GPM (precipitation), for real coordinates — not just named as sources. *Done: `src/data/nasa_power.py`, `nasa_smap.py`, `nasa_gpm.py`, all proven against real Kern County, CA coordinates with saved outputs.*
- [x] **Compute real environmental indicators.** Turn raw pulled data into the anomaly/risk indicators the plan describes (temperature anomalies, rainfall anomalies, soil moisture anomalies, consecutive dry periods, etc.) for at least one real location. *Done: `src/indicators/environmental.py`, verified on Kern County, CA June 2023 (-3.78°C temp anomaly, +300% rain anomaly, 11-day dry spell, 2 extreme rainfall days). Soil moisture anomaly is a simplified relative-wetness measure, not a true multi-year anomaly — SMAP history pulled so far is too short for that; a longer SMAP pull is a future follow-up.*
- [x] **Build and run the scoring model.** Implement the weighted multi-criteria rotation-scoring model (Section 7 of the plan) and actually run it to produce scores for the three strategies (Conventional, Legume-Integrated, Soil-Conservation) rather than leaving it as an unrun formula. *Done: `src/scoring/`, run for Kern County June 2023 — Soil-Conservation 71.9, Legume 57.4, Conventional 32.3. Climate resilience and erosion reduction use real computed indicators; soil health, water use, pest/disease, and economic criteria use documented baseline assumptions pending real FAO/market data integration.*
- [x] **Produce real strategy comparisons with explanations.** For at least one test location, generate the comparison the challenge requires: score, supporting evidence, benefits, information gaps, and risks for each of the three rotation strategies. *Done: `src/explanations/narrative.py` + `scripts/generate_comparison.py`, producing `outputs/kern_county_comparison.md` — template-based, every evidence line cites real computed numbers.*
- [x] **Build a minimal interface.** Some way to see the output — even a simple table/chart to start — rather than only description of an intended "interactive dashboard." *Done: `app.py` (Streamlit) — real indicators, strategy-ranking chart, full comparison per strategy. Verified rendering in browser. Single location, fixed weights for now.*
- [x] **Make farmer priorities adjustable.** Let the weighting (soil health / water use / climate resilience / pest-cycle / erosion / economic) actually be changed, and show scores update (sensitivity). *Done: sidebar sliders in `app.py`, verified live in Chrome — scores and rankings recompute in real time, reset-to-defaults works.*
- [x] **Carry over the plan's honesty/limitations stance.** Keep the explicit uncertainty and "decision support, not guaranteed outcomes" framing from the research plan as the tool is built, not just as a document. *Done: `app.py` now has a consolidated "Model Limitations" section (from Section 12), verified rendering in Chrome; `README.md` corrected to stop implying MODIS/Landsat are already integrated.*

Check a box off only once the corresponding goal is actually working and verified in the repo — not when a plan for it is merely approved.

## Submission-readiness goals

Beyond the 7 core goals above, these are gaps between "a working tool for one location" and a full NASA Space Apps submission.

- [ ] **Test at a second and third location.** The research plan calls for 3 contrasting environments (California, Punjab India, Cameron Highlands Malaysia) to show the tool generalizes — right now everything has only been proven for Kern County, CA.
- [ ] **Add a location picker to the app.** Even with more locations' data pulled, there's currently no UI to switch between them.
- [ ] **Deploy the app somewhere public.** It only runs locally right now — needs a live URL (e.g. Streamlit Community Cloud) so it can actually be tried without someone's own dev environment.
- [ ] **Integrate real supporting agricultural data.** Water-use, pest/disease, and economic scores are still documented assumptions, not real FAO crop-water data, local pest records, or market prices.
- [ ] **Prepare submission materials.** A project pitch/demo summary, screenshots or a short video — a README alone isn't a hackathon submission.

## World map goals (Google Earth Engine)

A new, bigger feature: a world map where a farmer types a country and sees a live-highlighted suitability layer, using Google Earth Engine (GEE) for the map/compute layer and our existing Streamlit app as the detailed per-location view once a spot is picked. See [PLAN.md](PLAN.md) for the reasoning behind this architecture.

- [x] **Set up Google Earth Engine access.** Free account/project registered, Earth Engine API enabled, verified with a minimal working script. *Done: project `nasa-space-apps-513601`, registered for non-commercial use, verified with `ee.Initialize()` + a real `USGS/SRTMGL1_003` elevation image query.*
- [x] **Prove the suitability-layer concept for one country.** A GEE script/app that paints a real (not fake) crop-suitability layer onto the map for a single country, using real GEE-hosted datasets. *Done: `src/geo/suitability.py` + `pages/1_World_Map.py`, Malaysia (research plan Location 3), real interactive pan/zoom map verified in Chrome — suitability layer correctly boundaried to Malaysia's actual territory.*
- [x] **Build the world map interface.** Country search, GEE App (or embedded GEE layer) showing the suitability highlighting, matching the reference site's interaction pattern. *Done: real country picker (284 countries) in `pages/1_World_Map.py`, verified with Malaysia and the United States producing genuinely different, geographically sensible results.*
- [ ] **Link the map to the detailed comparison view.** Clicking/selecting a spot on the map hands off to our existing Streamlit scoring+explanation app for that location — nothing already built gets thrown away.
- [ ] **Expand beyond one country.** Once the pattern works for one country, confirm it holds for others before calling this "a world map."

## Workflow

- Every change to this project gets a written plan first (what's changing, why, files touched) for review and approval before implementation — logged in [PLAN.md](PLAN.md) so there's a record of what was proposed, independent of chat history.
- Approved work gets committed and pushed to [github.com/qwfice/agrointel-ai](https://github.com/qwfice/agrointel-ai) via git CLI, and the corresponding PLAN.md entry gets marked done.
- UI/display work and anything AI-model-related is demoed in the user's own Chrome browser (via the Chrome extension), not just the built-in browser pane.

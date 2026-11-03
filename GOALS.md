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

- [x] **Test at a second and third location.** The research plan calls for 3 contrasting environments (California, Punjab India, Cameron Highlands Malaysia) to show the tool generalizes. *Done: the app is now location-agnostic (live NASA fetch per location, not a pre-saved file) and verified with genuinely different real results for Kern County, CA and Punjab, India; Cameron Highlands, Malaysia verified standalone (SMAP has since hit a rate-limit during repeated testing - noted below, not a correctness issue).*
- [x] **Add a location picker to the app.** Even with more locations' data pulled, there's currently no UI to switch between them. *Done: preset dropdown (the plan's 3 research locations) + custom lat/lon input in `app.py`, backed by `src/indicators/live.py`.*
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

## Product vision goals (from team Google Doc)

See [PLAN.md](PLAN.md) for the cleaned-up source and open architecture questions (Vercel vs. our current stack, relationship to the FieldCycle Bubble app).

- [x] **Chat assistant.** A left-side chat panel, backed by an existing pre-trained model (not a trained-from-scratch SLM), grounded only in the real computed data for the current location. *Done: `src/chat/assistant.py` (Gemini API) + sidebar panel in `app.py`. Verified in Chrome: a grounded question correctly cites real scores/numbers; an out-of-scope question (market prices) correctly declines to guess and suggests a local agronomist instead.*
- [ ] **Cookie consent choice.** Accept/decline, per the doc.
- [ ] **Farmer/expert report submission + admin review.** Entirely new scope — no design yet.
- [ ] **Direct location search** (type a place name, not just click the map) — partially covered by the World Map country picker, not yet for arbitrary sub-country locations.

## External integration goals (FieldCycle / Bubble)

The team's FieldCycle app (Bubble.io) already has NASA POWER, OpenStreetMap geocoding, and SRTM wired up via Bubble's API Connector plugin — the same pattern we need for our AI.

- [x] **Build a public-shaped API locally.** `api/main.py` (FastAPI) wrapping our existing logic, no duplication — `/indicators`, `/score`, `/chat`. *Done: all three endpoints verified working via real HTTP requests with real data (not deployed publicly yet, runs on localhost only).*
- [x] **Deploy the API publicly.** *Done: live at https://agrointel-ai-api.vercel.app on Vercel, auto-deploying from `main`. All 4 endpoints verified against the live URL with real data: `/` (health check), `/indicators` (real Kern County NASA POWER data), `/score` (real ranked strategy comparisons), `/chat` (grounded Gemini answer citing the real scores). Fixed two real bugs found during deployment: a trimmed `api/requirements.txt` (root requirements.txt pulled in Streamlit/Earth Engine/matplotlib and blew the 500MB Lambda size limit) and a missing `h5py` pin (silently relied on it already being installed locally).*
- [x] **Wire up Bubble's API Connector.** *Done: a new "AGROINTEL AI" API entry in FieldCycle's API Connector, matching the existing NASA POWER / Photon / SRTM pattern — three POST calls (Indicators, Score, Chat) pointing at https://agrointel-ai-api.vercel.app, each initialized with a real test request against the live deployment and returning real data (confirmed: real Kern County indicators, real ranked strategy scores, and a real grounded Gemini answer).*
- [ ] **Add a chat UI element to FieldCycle** that calls it. *In progress: question input, "Ask AGROINTEL AI" button, and answer text (bound to a new `workspace`'s `ai_answer` custom state) are built in the workspace page's Evidence Group. Blocked on wiring the button's workflow — Bubble's workflow action picker isn't yet listing the new AGROINTEL AI API Connector actions (Indicators/Score/Chat) as selectable, despite them being correctly configured, non-draft, and successfully initialized with real data in the API Connector tab. Tried re-initializing, a full page reload, and a fresh browser tab; looks like a Bubble-side propagation delay. Needs rechecking later in the Bubble editor.*
- [x] **Add a chat UI element to agrointel-website** that calls it. *Done: an "Ask AGROINTEL AI" chat section on the live Crop Rotation Explorer site (github.com/aizenthegoat123/agrointel-website, branch `A.I-integration`), calling `/indicators` then `/chat` for the site's existing Iowa farm location and rendering the real Gemini-grounded answer. Verified live in Chrome with a real question/answer round trip citing real computed scores. Also fixed a pre-existing bug in the site's own `script.js` (`markers` referenced before its `const` declaration ran) that was silently breaking every script on the page before this.*

## Workflow

- Every change to this project gets a written plan first (what's changing, why, files touched) for review and approval before implementation — logged in [PLAN.md](PLAN.md) so there's a record of what was proposed, independent of chat history.
- Approved work gets committed and pushed to [github.com/qwfice/agrointel-ai](https://github.com/qwfice/agrointel-ai) via git CLI, and the corresponding PLAN.md entry gets marked done.
- UI/display work and anything AI-model-related is demoed in the user's own Chrome browser (via the Chrome extension), not just the built-in browser pane.

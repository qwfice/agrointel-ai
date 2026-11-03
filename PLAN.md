# Plan Log

A running log of every plan proposed for this project, newest first. Each entry is written **before** any code changes for that step, so you can review what's about to happen without digging through chat history. Entries get a status update once the work actually lands.

---

## Chat assistant (Gemini API), grounded in real computed data

**Status:** pending approval

**Brief:** add the left-side chat panel from the product vision doc, backed by the Gemini API — not a trained/fine-tuned model, just an existing pre-trained model called via API (see earlier chat discussion on why training isn't the right approach here).

1. `src/chat/assistant.py` — builds a prompt from the real computed data for the current location (indicators, scores, evidence/gaps/risks from `src/indicators`, `src/scoring`, `src/explanations`) plus the user's question, calls the Gemini API, and returns the answer. System prompt instructs it to answer only from the provided real data and say so plainly when something isn't covered by it, rather than inventing facts - consistent with the project's honesty stance (GOALS.md goal 7).
2. A Gemini API key is needed - the user gets this themselves from Google AI Studio (aistudio.google.com/apikey) and sets it as an environment variable; I won't handle the raw key in chat.
3. Add a chat panel to `app.py` (sidebar, matching the doc's "small vertical chat on the left").
4. Verify in Chrome: ask it a real question about Kern County's actual data (e.g. "why did Soil-Conservation score highest?") and confirm the answer is grounded in the real numbers, not invented.
5. Commit, push, add and check off a new GOALS.md item for this.

**Scope note:** building this into the current Streamlit app first (not the eventual Vercel/Next.js frontend, which is still an open architecture question from the product-vision plan) - the prompt-building and API-call logic is reusable regardless of what frontend eventually calls it.

---

## Product vision — from the team's "Nasa Space Apps" Google Doc (cleaned up)

**Status:** pending approval — open questions below need answers before this becomes buildable steps

**Source:** the team's `Nasa Space Apps` Google Doc, rough notes rewritten here for clarity. Original wording preserved in meaning, just organized.

### Website requirements

- No user accounts or login required — anyone can use it immediately.
- A user can type in a location directly (no need to click around a map first) to jump to it.
- A world map highlights areas with good soil, based on real NASA data (this is what our Earth Engine suitability layer already does — see GOALS.md).
- A small vertical chat panel on the left, backed by a small language model (SLM), so users can ask for help while using the site.
- A cookie-consent choice (accept or decline).
- Farmers and agricultural experts can submit reports/feedback through the site, which go to an admin for review.
- Users see an indicator that explains what type of soil condition exists at their chosen location, and why (tied to the real computed data, not a black box).
- The AI helps forecast likely future weather conditions for a location, based on the data it's been given.
- The map highlights: when fields are typically bare, seasons when current crops are more vulnerable, and opportunities for rotations that could interrupt pest cycles, reduce water demand, improve infiltration, or add supplemental income.
- The AI compares at least three rotation strategies (including the farmer's existing one). For each: why it was suggested, what evidence supports it, what benefits it may offer, where the information gaps are, and what risks need local review — this is exactly what `src/explanations/narrative.py` already produces for Kern County.

### "AI" in the product

- Trained/fed on datasets such as SMAP, ECOSTRESS, GPM, Landsat, MODIS, NASA POWER, GRACE/GRACE-FO, and SRTM (we currently use POWER, SMAP, GPM, and SRTM — ECOSTRESS, Landsat, MODIS, and GRACE/GRACE-FO are not yet integrated; see GOALS.md).
- Helps determine likely future crop health from the fed-in data, and helps the user figure out the best crop rotation and planting area next.

### Deployment target

- The team wants to launch the website on **Vercel**.

### Open questions I need answered before this is a real plan (not doubts to brush past — actual blockers)

1. **Vercel doesn't run Python/Streamlit apps or Google Earth Engine compute directly.** Vercel is built for frontend frameworks (Next.js, static sites) and lightweight serverless functions — not a full Streamlit app or long-running GEE calls like ours. To launch on Vercel, we'd need one of:
   - A new frontend (e.g. Next.js) on Vercel, calling our existing Python logic (scoring/indicators/explanations/GEE) through a separately-hosted API (e.g. a small FastAPI service on Render/Railway/Fly.io) — our Python code stays, just gets a new thin API wrapper and a new UI.
   - Or: this product is actually the Bubble.io "FieldCycle" app (same name appears in the doc) — in which case Vercel isn't the host at all, Bubble is, and "Vercel" might mean something else was meant. Needs clarifying.
2. **Is this the same product as FieldCycle, or a separate one?** The doc explicitly names "FieldCycle," which is the teammate's Bubble.io app we already reviewed. Are we building *one* combined product (our backend + a new Vercel frontend, replacing or complementing Bubble), or is this a third, separate build? This changes the whole plan.
3. **The SLM chat assistant and the admin report-review system are both entirely new scope** — nothing like either exists yet in our repo or (as far as I saw) in FieldCycle. These are real features needing their own design, not small additions.
4. **"User authentication not needed" is good news** — it keeps scope down, no login system needed.

---

## World map (GEE) — Build the world map interface (country search)

**Status:** done

**Brief:** added a real country search/picker to `pages/1_World_Map.py` (284 countries, from the real boundaries dataset) — selecting a country re-runs `src/geo/suitability.py`'s computation for that country's actual boundary and re-centers the map. Verified with two different countries: Malaysia (mean suitability 69.4) and United States (mean 51.4, with a real geographic pattern - lower in the arid West, higher toward the humid East/Midwest). Also fixed a minor UX issue where very large countries started at too low a zoom for the suitability layer to render visibly. Does not yet include clicking a spot on the map to jump into the detailed Streamlit comparison (that's the next goal after this).

---

## World map (GEE) — Prove the suitability-layer concept for one country (revised)

**Status:** done

**Revision:** changed from India to Malaysia (ties to research plan Location 3, Cameron Highlands), and changed from a static map image to a real interactive map (pan/zoom) right away, per user request.

**Brief:** built `src/geo/suitability.py` — pulls real Earth Engine data for Malaysia's boundary: precipitation (GPM), terrain slope (from SRTM elevation), and soil moisture (SMAP), combined into a simple 0-100 suitability score per pixel. Rendered as a real interactive map (`pages/1_World_Map.py`, standard Earth Engine + folium pattern — `geemap`'s wrapper turned out to have a broken dependency, so built it directly instead) embedded in Streamlit. Verified interactively in Chrome: real pan/zoom, suitability layer precisely boundaried to Malaysia's actual territory, correctly excluding Brunei. Does not yet include country search or linking to the Streamlit detail view by clicking a spot - that's next.

---

## World map (GEE) — Set up Google Earth Engine access

**Status:** done

**Brief:** registered a free Google Earth Engine project (`nasa-space-apps-513601`, non-commercial use), enabled the Earth Engine API, and verified access with `src/geo/gee.py` against a real `USGS/SRTMGL1_003` query. Hit and fixed two real blockers along the way: a local SSL certificate issue (python.org install missing certs — fixed via `certifi`) and the project needing explicit Earth Engine registration beyond just enabling the API. First step of a new, bigger feature: a world map where a farmer picks a country and sees a live-highlighted crop-suitability layer, with our existing Streamlit app as the detailed per-location view once a spot is selected (architecture decision: GEE for the map/compute layer, since it already solves the "analyze a whole country, live, without downloading huge raster files ourselves" problem our earlier SMAP/GPM pulls struggled with - see the reference app https://total-service-474209-k1.projects.earthengine.app/view/bagis this is modeled after). Nothing already built (scoring model, explanations, sliders) gets replaced - the map becomes the entry point into it.

---

## Goal 7 — Carry over the honesty/limitations stance

**Status:** done

**Brief:** added a consolidated "Model Limitations" section to `app.py`, sourced from the research plan's own Section 12 (scoped to what we've actually built — no MODIS/NDVI mentions yet). Also corrected `README.md`, which previously implied MODIS/Landsat were already integrated. Verified rendering in Chrome. All 7 goals are now done.

---

## Goal 6 — Adjustable farmer priorities

**Status:** done

**Brief:** add sidebar sliders to `app.py` for the six scoring weights, feeding the existing `src/scoring/model.py` formula so dragging a slider live-recomputes real scores. Verified in Chrome.

---

## Goal 5 — Minimal interface

**Status:** done

**Brief:** build a Streamlit app (`app.py`) showing real indicators, a strategy-ranking chart, and the full per-strategy comparison, reusing existing code with no duplicated logic. Verified rendering in the browser.

---

## Goal 4 — Strategy comparisons with explanations

**Status:** done

**Brief:** template-based (not LLM) generator (`src/explanations/narrative.py`) producing evidence/benefits/information-gaps/risks per strategy, with evidence citing actual computed numbers. Output written to `outputs/kern_county_comparison.md`.

---

## Goal 3 — Weighted scoring model

**Status:** done

**Brief:** implement Section 7's weighted formula (`src/scoring/`), mixing real computed indicators (climate resilience, erosion reduction) with documented baseline agronomic assumptions (soil health, water use, pest/disease, economic) where real data isn't integrated yet. Run for Kern County.

---

## Goal 2 — Real environmental indicators

**Status:** done

**Brief:** compute temperature/rainfall anomalies vs. 5-year POWER climatology, dry-spell length, extreme rainfall frequency, and a soil-moisture relative-wetness measure (`src/indicators/environmental.py`). Verified against real Kern County June 2023 numbers.

---

## Goal 1 — Real NASA data integrations

**Status:** done

**Brief:** build NASA POWER, SMAP, and GPM clients (`src/data/`) and prove each against real Kern County, CA coordinates.

---

## How this works

- Before implementing anything, a new entry goes at the top of this log with a brief description and `Status: pending approval`.
- Once you approve it in chat, work begins.
- Once it's actually built, verified, and pushed, the entry's status updates to `Status: done`.
- This file is committed alongside the code it describes.

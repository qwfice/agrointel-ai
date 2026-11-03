# Plan Log

A running log of every plan proposed for this project, newest first. Each entry is written **before** any code changes for that step, so you can review what's about to happen without digging through chat history. Entries get a status update once the work actually lands.

---

## World map (GEE) — Build the world map interface (country search)

**Status:** pending approval

**Brief:** currently `pages/1_World_Map.py` is hardcoded to Malaysia only. This step adds a real country search/picker to that page — typing or selecting a country re-runs the same `src/geo/suitability.py` computation for that country's actual boundary and re-centers/re-renders the map, instead of needing a code change per country. To prove this isn't hardcoded under the hood, I'll verify it works for at least 2 different countries (Malaysia plus one more, e.g. the USA or India), not just swap the one hardcoded value. Does not yet include clicking a spot on the map to jump into the detailed Streamlit comparison (that's the next goal after this).

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

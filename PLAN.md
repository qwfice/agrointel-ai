# Plan Log

A running log of every plan proposed for this project, newest first. Each entry is written **before** any code changes for that step, so you can review what's about to happen without digging through chat history. Entries get a status update once the work actually lands.

---

## Make the new landing-page's Suitability heatmap real (season/bare-field/crop-stress aware), fix the date timeline

**Status:** pending approval

**Context:** User shared a new, different site folder (`agrointel-website-main` from Downloads — a separate "AgroIntel AI Agronomy Landing Page" build, not the Crop Rotation Explorer site worked on earlier in this project; it isn't in a git repo). Its NASA Live section (`index.html` `#analysis`, logic in `script.js`) has a "Suitability Model" panel whose copy explicitly claims: *"Real, NASA-data-driven risk zones... interpolated from MODIS NDVI (250 m) and NASA POWER root-zone wetness."* That claim is currently false. User asked to fix the heatmap, explain what its color represents, make it reflect seasonal transitions / bare-field periods / crop stress, and fix the date timeline — plus optionally add a timeline, dataset-comparison overlays, or rainfall/temperature scenario sliders.

**What's actually there right now (`script.js` lines ~625-696):**
1. `MODELS` (erosion/drought/nitrogen/flood) has **hand-painted, fixed canvas gradient blobs** — same position, size, and color every time, for every date, regardless of anything. Nothing computed, nothing real.
2. The gradient positions (`spots: [[0.28, 0.28, 0.34, ...]]`) are arbitrary canvas fractions with **no relationship to the 5 real block marker locations** (`BLOCK_MARKERS`) shown on the same map.
3. Per-block risk labels (`risk: { A: "high", ... }`) are static text, same for every date.
4. The page already fetches a **real** NASA POWER daily record (731 days, 2023-2024, temp + precip + GWETROOT) for the climate charts, but that data is discarded after the charts render — never reused for the heatmap.
5. The `#nasaDate` input only drives the GIBS satellite-imagery layer. It has **zero effect on the suitability heatmap** — changing the date changes the picture underneath but the colored risk blobs never move. This is "the timeline doesn't work."

**Brief (real-data approach, consistent with this project's standing honesty rule — no fabricated per-pixel data, every number traced to something real or clearly labeled as a documented assumption):**
1. **Keep the real POWER record alive.** Store the already-fetched daily series (not just the chart aggregates) in a shared variable so the heatmap code can look up real temperature and GWETROOT values for any date.
2. **Add a documented crop-calendar table** (bare / establishing / growing / peak / senescence month ranges, and heat/drought sensitivity factors) for the 5 block crops (Tomato, Wheat, Cotton, Grapes, Paddy) — clearly labeled as a typical-calendar assumption, the same honest pattern used for the vulnerability factors in the main AGROINTEL AI scoring model, not presented as measured.
3. **Make the date input actually drive the heatmap.** For whichever date is selected, map it onto the real 2023-2024 POWER record by calendar day (honestly labeled "based on real NASA POWER conditions typical for this time of year," since POWER has no live data for future dates) to get a real temperature-anomaly and real root-zone-dryness reading, and combine that with the crop-calendar phase for each block.
4. **Compute real per-block scores instead of static labels:** erosion risk rises when a block is in a bare-field phase and real recent rainfall was heavy; drought/stress risk rises with real root-zone dryness scaled by each crop's documented drought sensitivity, and matters most during growing/peak phases, little while bare or dormant; nitrogen-loss risk rises with real heavy-rain events during establishing/growing phases. A new **"Crop Stress & Season"** model is added, combining real heat + moisture stress with the bare-field/season-phase signal directly, since that's what was asked for and doesn't cleanly fit the 4 existing categories.
5. **Fix the heatmap's geography:** position each gradient blob at its block's real lat/lon (converted into the image overlay's canvas fraction) instead of arbitrary fixed spots, so the colored zones actually sit over the real block markers.
6. **Explain the color honestly, in the UI:** rewrite the Suitability panel's copy and add a short legend so it accurately says what's real (POWER heat/moisture + real block locations) vs. documented assumption (crop calendar, sensitivity factors) — fixing the current false "MODIS NDVI 250m" claim rather than just leaving it.
7. **Optional add-ons:** (a) a simple month/season scrub control so the user can slide through a full year and watch bare-field/stress conditions evolve, without retyping dates — the most direct way to prove "the timeline works"; (b) rainfall/temperature scenario sliders (± over the real baseline) that recompute the heatmap live, clearly labeled "what-if," not a forecast. Skipping a full "dataset comparison overlay" (e.g., two heatmaps side by side) this round as a bigger, separate feature — can propose it afterward if wanted.
8. Demo in Chrome: change the date across seasons and confirm the heatmap visibly changes (not static); switch models and confirm the legend/notes explain the color; use the scrub control and scenario sliders and confirm both actually move the heatmap.
9. No git repo here to push to — ask the user where this should land (new repo, or copied back into the existing `agrointel-website` project) once implemented and verified.

---

## Sync the chatbot to the map, and add real per-search crop-suitability markers

**Status:** done — implemented and verified live in Chrome. "go to malaysia on the map" now geocodes correctly (previously failed). Asked "what's a good rotation strategy for Kenya?" with no prior "go to": map auto-panned to Kenya's real boundary first, then answered citing Kenya's real numbers (0 extreme-rainfall days, 6.88mm/day threshold, water-use 58.2/100) instead of Iowa's - confirming the chat is now genuinely synced to the map. The new per-search recommendation marker (a real `/indicators`+`/score` fetch for the searched point) opened on click showing Kenya's actual top-ranked strategy (Soil-Conservation, 71.5/100) and real conditions. Fixed one bug found during testing: the recommendation marker used `L.circleMarker` which sat behind the heatmap's invisible per-cell inspection markers and had its clicks swallowed - switched to a real `L.marker` (separate Leaflet pane) so it's reliably clickable. Pushed to `A.I-integration` (commit `a5236ee`, updates PR #1).

**Context:** User sent 3 screenshots. (1) Asked the chat "go to malaysia on the map" in the chat box — it failed with "Sorry, I could not find that place." (2) A follow-up question about Malaysia got answered with Iowa data ("The data provided is specifically for Central Iowa, USA... not Malaysia") — because the chat's indicators call is hardcoded to `FARM_LAT`/`FARM_LON` no matter what the map is actually showing. (3) A screenshot of the site's existing hardcoded "East Block – Diversification Candidate" marker/popup for the sample Iowa farm. User wants: the chatbot to actually show/sync the map to the area it's discussing while explaining it, and that same marker+popup pattern (real data, suitable-crop note) generated for *any* country/region/city/district the user searches, not just the 3 fixed Iowa points.

**Root causes found in `script.js`:**
1. `searchPlace()` sends the raw chat text (minus "go to ") straight to Nominatim. "malaysia on the map" fails to geocode because of the trailing "on the map" - Nominatim needs just the place name.
2. `getAgrointelIndicators()` is hardcoded to `FARM_LAT`/`FARM_LON`/`AGROINTEL_LOCATION_LABEL` and cached in one single global promise - so **every** chat question is answered from Iowa data forever, regardless of what place the map/search is currently showing. This explains screenshot 2 exactly.
3. The only existing crop-suitability markers (`fields` array, 3 hardcoded points) are static Iowa-only text, not generated from real data, and don't exist for any other location.

**Brief:**
1. **Fix the "go to" query bug:** strip trailing filler phrases ("on the map", "on earth", "please", etc.) from the chat's place query before geocoding.
2. **Make the chat genuinely location-aware:** replace the single hardcoded Iowa indicators cache with a per-location cache keyed by rounded lat/lon, sourced from `siLastLocation` (the map's current search/focus) instead of always `FARM_LAT`/`FARM_LON`. Every chat answer - and the context sent to Gemini - will then reflect whatever place is actually centered on the map.
3. **Let a free-form question move the map too:** lightly parse the raw question for an "in/for/at/near <Place>" pattern; if found, geocode it and pan/fit the map there (same as a "go to" command) *before* answering, so asking "what should I plant in Kenya?" directly shows Kenya while the AI explains it - not just after an explicit "go to" first. Falls back to whatever's already on the map if no place phrase is found or it doesn't geocode, so normal questions are unaffected.
4. **Real per-search recommendation marker:** after a successful search/navigation (via the search box, "go to", or the new in-question detection), fetch real `/indicators` + `/score` for that location's centroid and drop one marker there with a popup showing the real top-ranked rotation strategy, its real overall score, and a one-line real-data note (e.g. the dry-spell/rainfall anomaly driving it) - the same style as the existing Iowa "East Block" popup, but generated from real data for wherever was searched, not hand-written text. Replaces the previous search's marker on a new search; the 3 original Iowa field markers stay as-is for the default farm view only.
5. Demo in Chrome: ask "go to Malaysia" in chat (confirm it now finds it and the marker/popup appears with real Malaysia data), then ask a follow-up question and confirm the answer cites Malaysia's real numbers, not Iowa's; separately ask "what's a good rotation for Kenya?" with no prior "go to" and confirm the map pans there and answers with Kenya's real data.
6. Commit and push to `A.I-integration` (updates PR #1).

---

## Make the AI smarter and the scoring more trustworthy (real data + transparency, not inflated numbers)

**Status:** done — implemented, tested locally against live NASA POWER data, verified live in the website's chat UI (asked "make my score higher"; AI refused to inflate it and cited the real -26.1% rainfall anomaly, +1.78°C anomaly, 12-day dry spell instead), and confirmed live in production on Vercel (`/indicators`, `/score` both returning the new fields/tags at `https://agrointel-ai-api.vercel.app` as of commit `f97121d`). Pushed to `main` in `agrointel-ai` and `A.I-integration` in `agrointel-website` (commit `dc83485`).

**Context:** User asked if we can make the AI "more intelligent" and make the score "higher" and "more trustable." Per this project's whole design principle so far (refusing fake heat-wave/GRACE data, refusing to mislabel assumption-based criteria as real, "decision support not guarantee" framing), this plan does NOT inflate numbers. Right now only 2 of 6 scoring criteria (`climate_resilience`, `erosion_reduction`) are driven by real NASA data — the other 4 (`soil_health_potential`, `water_use_suitability`, `pest_disease_interruption`, `economic_suitability`) are static expert-baseline guesses (`src/scoring/criteria.py`). I found one real computed indicator, `rainfall_anomaly_pct` (`src/indicators/environmental.py`), that's already implemented and imported in `src/indicators/live.py` but never actually used — it's dead weight. Wiring it in is a genuine, honest way to raise real-data coverage and make scores move for real reasons. Trustworthiness goes up through transparency (showing the user what's measured vs. assumed), not bigger numbers.

**Audit update (user asked to confirm the AI is fed ALL computed data, not some):** traced the full chain end to end (`environmental.py` → `live.py` → `api/main.py` `/indicators` → website → `/score`/`/chat`). Confirmed `rainfall_anomaly_pct` is computed but never called inside `fetch_and_compute_indicators()`, so it never reaches `/indicators`, `/score`, or the chat context — matches the finding above. Also found a second, smaller gap: `extreme_rainfall_days()` computes both a count and the mm/day threshold that defines "extreme" for that location, but `live.py` only keeps the count and discards the threshold — so the AI currently can't say what "extreme" actually means numerically for that spot. Folding the fix for both into step 1 below, so every real number the backend computes actually reaches the AI; nothing computed gets silently dropped.

**Brief:**
1. **Backend — use the unused real indicators:** wire `rainfall_anomaly_pct` into `fetch_and_compute_indicators()` in `src/indicators/live.py` so it's actually returned by `/indicators`; also keep the extreme-rainfall mm/day threshold (currently discarded) alongside the count.
2. **Backend — make `water_use_suitability` partially data-driven:** in `src/scoring/criteria.py`, adjust its static baseline up/down based on the real rainfall anomaly (same pattern already used for `climate_resilience`/`erosion_reduction`: a vulnerability-scaled penalty/bonus off a baseline) — e.g. a strategy with higher water demand gets penalized more when real rainfall is anomalously dry, and a small bonus when it's anomalously wet. This moves `water_use_suitability` from fully-assumed to 3rd real-data-driven criterion (2/6 → 3/6).
3. **Backend — honest provenance tags:** have `score_all_criteria`/`/score` return a `confidence` tag per criterion (`"real_data"` vs `"expert_baseline"`) so nothing downstream can present a guess as a measurement.
4. **Chat — richer, more honest grounding:** extend `build_context()` in `src/chat/assistant.py` to include the new rainfall indicator and each criterion's confidence tag, and tighten `SYSTEM_INSTRUCTION` so Gemini must say explicitly when a number it's citing is real-data-driven vs an expert starting-point assumption, and must cite the specific real indicator value behind any claim it makes. This is what "more intelligent" means here — better-grounded, more precise answers, not more creative freedom.
5. **Website — show the provenance tags:** in the Suitability sidebar panel (and wherever criterion scores are shown), add a small "NASA data" vs "Expert baseline" badge per criterion so a farmer can see at a glance what's measured vs. a documented starting assumption.
6. **Explicitly out of scope / left honest:** `soil_health_potential`, `pest_disease_interruption`, `economic_suitability` stay expert baselines — there's no real NASA-derived signal for soil organic matter, pest pressure, or market prices integrated yet (tracked as future goals in GOALS.md). No change here pretends otherwise.
7. Demo in Chrome: pick a location, confirm `/indicators` now returns the rainfall anomaly, confirm `water_use_suitability` differs between a dry and a wet example location, confirm the badges render, and confirm asking the AI "how reliable is this score?" gets an honest, specific answer citing real numbers.
8. Commit and push to `A.I-integration` (website) and the relevant branch in `agrointel-ai` (backend); update GOALS.md's real-data-coverage tracking afterward.

---

## Investigate date/opacity controls; remove Update button, auto-apply instead

**Status:** done — small, low-risk change, verified live.

**Findings (date & opacity accuracy check requested by user):**
- Opacity slider was already live (applies instantly via an 'input' listener) — working correctly, no change needed.
- Date and NASA Layer dropdown previously only took effect on clicking "Update". Verified the date itself IS accurate/functioning: GIBS's `best` WMTS endpoint returns real imagery (HTTP 200) for the requested date, auto-falling back to the nearest available day when the exact date isn't processed yet (confirmed with a date one day before "today"); for a date with no satellite data available yet (weeks out), it correctly returns 503 and the site gracefully falls back to the clean Esri basemap (no broken-image artifacts) via the existing `errorTileUrl`.

**Brief:**
1. Remove the "Update" button.
2. Wire `change` listeners on the NASA Layer select and Date input straight to `updateGibsLayer()`, matching how opacity already behaved — every control now applies immediately.
3. Demo in Chrome: confirm changing layer/date updates the map instantly with no button, verified via both visual change and real network requests.
4. Commit and push to `A.I-integration` (updates PR #1).

---

## Heatmap: accurate real-shape outlining (not just a rectangle)

**Status:** done — verified live in Chrome with Malaysia (multi-part: Peninsular + Borneo, confirmed real colored coverage on both parts, zero color in Thailand/Indonesia/ocean) and Kenya (single polygon, no regression). Fixed a real gap found during testing: gridding one box over a multi-part country's whole combined bounding box left almost every sample point in open ocean between the parts (Malaysia initially came back with only 2 fetched points) — fixed by gridding each landmass part separately (`siBuildGridForGeometry`, capped to the 4 largest parts by area) instead of one grid over the full extent.

**Context:** Screenshot showed a Malaysia search painting a small blob that didn't reach Peninsular Malaysia's coast and entirely missed East Malaysia (Borneo) — because the heatmap is sampled over the map's rectangular viewport, not the country's real (and in Malaysia's case, split/multi-part) shape. User wants the color to actually follow real borders/coastlines.

**Brief:**
1. Request real boundary geometry from Nominatim (already used for search) by adding `polygon_geojson=1&polygon_threshold=0.01` to the existing search request — the threshold keeps geometry reasonably light so a detailed coastline doesn't bog down the browser.
2. On search, fit the map to the real shape's full extent (`L.geoJSON(geometry).getBounds()` + `map.fitBounds`) instead of a fixed zoom level, and draw a thin real boundary outline on the map so there's a visible, accurate border — not just inferred from the heat color.
3. Filter the SI sample grid to only points whose coordinates fall **inside** the real polygon (a point-in-polygon test, handling multi-part countries like Malaysia), before fetching — ocean and neighboring-country points are skipped entirely, never fetched, never colored.
4. Scope note, said plainly: this won't be a pixel-perfect clip exactly at the coastline (the heat blur still softly feathers a little past sampled points near the edge) — true hard-edge clipping to an arbitrary, possibly very detailed multi-island coastline is a much heavier technique (canvas/SVG masking) with real performance risk for complex country shapes, and isn't worth the fragility here. The combination of inside-only sampling + a real boundary outline gets the accuracy that matters (no color in the wrong country/ocean, full real coverage of multi-part countries) without that risk.
5. Default farm view (no search) is unaffected — no geometry, same bare-point behavior as before.
6. Demo in Chrome: re-search Malaysia and confirm both the peninsula and Borneo get real sampled/colored coverage, with no color in the ocean or Thailand; also test a simple single-polygon country (e.g. Kenya) to confirm no regression.
7. Commit and push to `A.I-integration` (updates PR #1).

---

## Heatmap: smoother blending, full-viewport coverage, enable/disable toggle

**Status:** done — verified live in Chrome (Iowa default view and a Kenya search), toggle confirmed on/off/back-on with cache reuse. Hit and fixed a real bug along the way: `map.getBounds()` was read before Leaflet had the container's final size (classic stale-size issue), so the heatmap covered only a fraction of the visible map — fixed with `map.invalidateSize()` right before reading bounds.

**Context:** The SI heatmap currently samples a small box around the searched point/place's boundingbox, which can leave most of the visible map uncolored, and the blend radius is tight enough to show some blob-like separation between sample points. User wants it smoother and covering the whole visible map, plus a way to turn it off.

**Brief:**
1. Switch grid sampling from "a box around the search result" to **the current map viewport** (`map.getBounds()`, read right after the view is set) — so the sampled area always matches what's actually on screen, literally covering "the whole map" without needing to track pan/zoom continuously or refetch outside of a search.
2. Increase grid density slightly (25 points, 5×5, still capped) and increase the heat layer's radius/blur multipliers so points blend into fully continuous coverage with no visible gaps or blob edges.
3. Add a **"Show Suitability Heatmap" checkbox** next to the Map Model dropdown, defaulting on. Unchecking removes the heat/marker layer from the map (cheap, no refetch); re-checking restores it from cache, or fetches if there's nothing cached yet for the current view.
4. Demo in Chrome: confirm the heat now covers the full visible map area after a search, confirm it reads as smooth/continuous, and confirm the toggle cleanly shows/hides it.
5. Commit and push to `A.I-integration` (updates PR #1).

---

## Fix black "teeth" artifact on the map at low zoom

**Status:** done — verified live in Chrome. `minZoom: 4` still showed the gaps at that exact zoom, bumped to `minZoom: 5`; confirmed clean full-world Esri view below zoom 5 and correct NASA imagery (clouds, heatmap) reappearing at zoom 5+, both zooming out and back in.

**Context:** User reported jagged black triangular gaps on the map when zoomed far out. Diagnosed: `createGibsLayer` (`script.js:33`) loads NASA's single-day MODIS/VIIRS "Corrected Reflectance" imagery, which has real satellite-orbit swath gaps — visible whenever the view is wide enough (country-scale, which the new place-search/SI grid feature naturally encourages). Pre-existing in the original site code, not introduced by recent changes, but now more likely to be hit.

**Brief:**
1. Add `minZoom` to the GIBS tile layer options so it stops rendering below a zoom level where swath gaps become visually prominent, leaving the always-complete Esri satellite basemap visible underneath at wide zoom (no blank/broken area — a real fallback, not a gap).
2. Demo in Chrome: zoom out past the threshold and confirm the basemap stays clean (no teeth), then zoom back in and confirm the NASA layer reappears normally.
3. Commit and push to `A.I-integration` (updates PR #1).

---

## SI grid: 2 more real models + smooth heatmap visual (instead of hard grid boxes)

**Status:** done — verified live in Chrome. All 5 models (Erosion Risk, Water Stress, Temperature Anomaly, Climate Resilience, Overall Suitability) confirmed working with correct legends (red-high for risk models, green-high for Climate Resilience/Overall Suitability) and zero new network requests when switching. Heatmap renders as smooth continuous coverage (Leaflet.heat, radius/blur sized from on-screen point spacing, re-rendered on zoom) instead of hard-edged boxes.

**Context:** User shared a landslide-susceptibility-mapping reference image (continuous painted terrain, not discrete boxes) and asked why there are only 3 map models when the data could support more. Checked `src/scoring/model.py`: of the 6 `criteria_scores` from `/score`, only `climate_resilience` and `erosion_reduction` are computed from real NASA data — `soil_health_potential`, `water_use_suitability`, `pest_disease_interruption`, `economic_suitability` use documented baseline assumptions (per existing GOALS.md honesty notes), so those won't be added as "real" map models. User also asked for long-term soil moisture, heat waves, and water-storage decline. Decided with the user:
- Soil moisture: **skip for now** — a single SMAP call already timed out past 60s in earlier testing; fetching it per grid point would make searches unusably slow.
- Heat waves (true consecutive-extreme-heat-day detection) and water-storage decline (GRACE/GRACE-FO, an entirely uningested NASA dataset) are **real backend work**, not a website tweak — deferred to a separate future task, logged in `GOALS.md` rather than built now.

**Brief:**
1. Add 2 more real map models to the dropdown, reusing data already fetched per grid cell (no new API calls): **Temperature Anomaly** (`temp_anomaly_mean_c`) and **Climate Resilience** (`criteria_scores.climate_resilience` from `/score`, captured alongside the existing `overall_score` pull).
2. Replace the hard-edged grid rectangles with a smooth interpolated heatmap (Leaflet.heat, loaded from CDN) built from the same real sampled grid points, colored with a gradient matching the existing 5-class legend per model (red=high for risk models, green=high for suitability/resilience). This is visual interpolation between real sampled points, not a true per-pixel satellite-derived raster like the reference image's landslide study — the legend/copy will stay honest about that.
3. Tune heatmap radius/blur so the sampled points blend into continuous coverage across the current grid's bounding box, recalculated on zoom change.
4. Demo in Chrome: Iowa farm and a new search, switching through all 5 models, confirming the heatmap looks continuous and the legend/values stay accurate.
5. Commit and push to `A.I-integration` (updates PR #1). Add a note to `GOALS.md` under External/future goals for the deferred heat-wave and GRACE water-storage backend work.

---

## Real, per-location Suitability Index overlay on the website map (expanded: grid heatmap + model selector)

**Status:** done — verified live in Chrome with the default Iowa farm (uniform real data at that scale, correctly so — small area, similar climate) and a Punjab, India search (real boundingBox-derived grid with real variation). Confirmed switching models re-renders instantly with zero new network requests (reuses already-fetched data). Reduced grid size to 16 points (4×4, capped) to keep per-search API calls reasonable; increased rectangle fill opacity + white borders after the first pass rendered but was visually invisible against the satellite basemap. Dropped the stale `toggleOverlay`/checkbox-based chat commands (referenced removed DOM elements) in favor of `setSuitabilityModel`.

Expanded after the user shared a reference image (a landslide-susceptibility-mapping paper figure: multiple model panels, each a full color-graded raster over terrain, 5-class legend Very High→Very Low). User wanted the same idea here: a painted suitability/risk layer across the searched area, switchable between different real "models" (weather-condition views), not just point circles.

**Context:** The map's "Vulnerability Overlays" (erosion risk, water-stress hotspots, frost-prone areas — `script.js:163-191`) are hardcoded fixed-coordinate shapes drawn only around the sample Iowa farm; illustrative placeholders, not real data. Decided with the user: build on real point-data from our own API (not Google Earth Engine — that's a much bigger separate effort), but sample a **grid of points** across the searched area instead of a single point, so it reads as a painted layer like the reference image.

**Brief:**
1. Remove the 3 hardcoded static zones and their checkboxes. Replace with: a **"Map Model" dropdown** (Erosion Risk / Water Stress / Overall Suitability) and a fixed 5-class legend (Very High/High/Moderate/Low/Very Low), styled like the reference image.
2. On initial load (Iowa farm) and every successful place search, build a small bounding box around the location — Nominatim's search result includes a real `boundingbox` for places/countries; fall back to a fixed ±1° box around a bare point (e.g. the default farm). Sample an adaptive grid of points inside it, capped at ~36 points total to keep it fast and within NASA POWER's rate limits.
3. Fetch `/indicators` (POWER-only, `include_soil_moisture: false`) for every grid point in parallel. Store each point's real `temp_anomaly_mean_c`, `extreme_rainfall_days`, `longest_dry_spell_days`. This is one batch of real calls per search — never precomputed for anywhere the user hasn't searched.
4. Derive 3 real "models" from that same fetched data (no extra calls needed to switch models client-side):
   - **Erosion Risk** — from `extreme_rainfall_days`.
   - **Water Stress** — from `longest_dry_spell_days` + `temp_anomaly_mean_c`.
   - **Overall Suitability** — top-ranked strategy's real `overall_score` from one `/score` call per grid point (reusing the already-fetched indicators).
5. Classify each grid cell into the 5 legend classes (quantile-based thresholds over the current grid's own values) and paint it as a semi-transparent colored rectangle covering that cell — switching the dropdown just recolors the existing grid instantly, no refetch.
6. Frost is dropped from the model list (no real frost/min-temp field in our API) rather than faking it — consistent with the project's honesty-about-data-limits stance.
7. Show a "Computing real data for [place]…" loading state while the grid fetches; cache the grid per search so re-searching the same place doesn't refetch.
8. Demo in Chrome: confirm the default Iowa grid paints real values, switch between all 3 models and confirm colors change, then search a different place (e.g. Punjab, India) and confirm a new real grid renders there — checked via the Network tab, not just visually.
9. Commit and push to the same `A.I-integration` branch (updates PR #1). Update `GOALS.md`.

## Wire real AGROINTEL AI into the updated agrointel-website chatbot (v2 site)

**Status:** done — verified live in Chrome. Along the way: fixed the same `markers` TDZ bug as before, fixed the `.chat-panel { display: flex }` CSS rule that was silently defeating the native `[hidden]` attribute so the minimize/expand toggle did nothing, narrowed the keyword-command matching (only applies to short non-question phrases, ≤4 words and no "?") so real questions like "what's the best rotation strategy here?" fall through to the real AI instead of just scrolling the page, and switched the markdown formatter from paragraph-block-based to line-based so a bullet list right under a heading (no blank line between them) still renders as a real `<ul>` instead of literal `* ` text.

**Context:** User supplied a newer version of the site (`~/Downloads/crop-rotation-tool 2`), building on the one already merged into `A.I-integration`. Diffed against the previous version: it adds a place-search box (Nominatim) and, notably, a full floating chatbot widget ("CropRot Assistant": `#chatbot` toggle button + `#chat-panel`) that's already built but is **rule-based, not AI** — `handleChatCommand()` pattern-matches keywords to control the map (go to a place, switch GIBS layers, toggle risk overlays, scroll to sections) and has 3 hardcoded canned answers (cover crops, SCN/pests, organic matter) plus a generic fallback for anything else. It does not call any real backend. Same pre-existing `markers`-before-declaration bug as before is present in this copy too.

**Brief:**
1. Keep every existing command behavior as-is (place search, layer switching, overlay toggles, section scrolling) — those are useful, deterministic, and don't need AI.
2. Replace just the knowledge-answer path with the real AGROINTEL AI: the 3 hardcoded canned snippets (cover crop / SCN / organic matter) and the final generic fallback get replaced by a real call to `https://agrointel-ai-api.vercel.app` — `/indicators` (POWER-only, `include_soil_moisture: false`, same lesson learned from the first integration about SMAP timeouts) for the farm's `FARM_LAT`/`FARM_LON`, then `/chat` with the real indicators and the user's actual message, rendering the real Gemini-grounded answer as a bot message. Show "Thinking…" while waiting; on failure, show a plain error message instead of crashing.
3. Fix the same `markers`-before-declaration TDZ bug as in the previous round (move the `const markers = []` earlier).
4. Demo in the user's real Chrome: test both a command ("show NDVI") and a real question ("is a diversified rotation worth it here?") to confirm commands still work locally and open-ended questions now get real grounded AI answers.
5. Commit and push to the same `A.I-integration` branch on `aizenthegoat123/agrointel-website` (adds to the already-open PR #1, doesn't need a new branch/PR).
6. Update `GOALS.md` to reflect the upgraded integration.

## Wire the live AGROINTEL AI API into agrointel-website

**Status:** done — chat section built, wired to the live API, tested live in Chrome with a real grounded answer for the Iowa farm location (fixed a pre-existing `markers`-before-declaration bug along the way that was breaking all page scripts). Committed and pushed to branch `A.I-integration` on https://github.com/aizenthegoat123/agrointel-website (branch named with a hyphen, not a space — git doesn't allow spaces in branch names). Push initially failed with a 403 (qwfice lacked write access); resolved once the teammate granted collaborator write access.

**Context:** `agrointel-website` (github.com/aizenthegoat123/agrointel-website, teammate added us as collaborator) is the team's official site repo. The user sent the real, current site code (a `crop-rotation-tool` folder: `index.html`, `script.js`, `styles.css`) which is a full "Crop Rotation Explorer" static site for a sample Iowa farm (42.0308°N, -93.6319°W) — hero section, farmer-priorities quiz, Leaflet/NASA-GIBS interactive map, NASA POWER climate charts (fetched client-side directly from power.larc.nasa.gov), a 3-strategy comparison with tabs, and a comparison table. **It has no chat/AI element anywhere** — the repo's previous bare chat-stub scaffold is superseded by this. User's explicit instruction stands: get the AI functionally working first, defer visual polish to later. User also asked for this work to go on a new branch, "A.I integration", in `agrointel-website`, not `main`.

**Brief:**
1. Replace the local working copy of `agrointel-website` with the user's supplied `index.html`/`script.js`/`styles.css` (from `~/Downloads/crop-rotation-tool`), on a new branch `A.I integration` created off `main`.
2. Add a minimal AI assistant chat section to `index.html`, placed after the hero/nav (own `<section id="ai-assistant">`), styled plainly with the site's existing dark/green CSS variables/theme already in `styles.css` — a header, a scrollable message list, a text input + send button. No redesign beyond matching existing colors/fonts.
3. Implement the chat logic in `script.js`:
   - On send: show the user's message, then call the deployed API at `https://agrointel-ai-api.vercel.app`: `POST /indicators` using the site's own existing `FARM_LAT`/`FARM_LON` constants (42.0308, -93.6319 — the same Iowa location the rest of the page already uses, so the AI's answers are grounded in the same place the user is looking at), then `POST /chat` with those real indicators, a location label ("Central Iowa, USA (Ames area)"), and the user's question. Render the real Gemini-grounded answer as a bot message.
   - Show a plain "Thinking…" bot message while waiting, replaced by the real answer.
   - On failure (network/API error), show "Something went wrong talking to AGROINTEL AI" rather than crashing silently.
4. No backend changes needed — `api/main.py` already has `CORSMiddleware(allow_origins=["*"])`.
5. Demo in the user's real Chrome (via the Chrome extension): open the page, ask a real question, confirm a real grounded answer referencing the Iowa indicators comes back, and confirm the rest of the page (map, charts, priorities, tabs) still works unmodified.
6. Commit and push to the `A.I integration` branch on `agrointel-website` (not `main`, not `agrointel-ai`). Update this repo's `GOALS.md` to note the website now has a working chat integration, linking the branch.
7. Explicitly out of scope for this step: the image panel concept from the old scaffold (dropped — this new site doesn't have one), a location picker, and any visual redesign beyond what's needed to fit the chat section into the existing page — those are "later."

---

## Deploy the API to Render

**Status:** abandoned — Render's one-click Blueprint deploy required payment card info even on the free tier. User declined ("I don't want to pay"). Superseded by the Vercel plan below, which also matches the team's originally-stated deployment target.

---

## Deploy the API to Vercel (replaces the Render plan above)

**Status:** done — live at https://agrointel-ai-api.vercel.app, all 4 endpoints verified with real data and a real Gemini answer. Along the way: fixed a GitHub App repo-access permission (Vercel couldn't see the repo until authorized), a Lambda-size overrun from the unscoped root requirements.txt (fixed with a trimmed `api/requirements.txt`), and a missing `h5py` pin that crashed every request.

**Brief:** get `api/main.py` running on a public URL via Vercel instead of Render - no payment card required for the Hobby tier, and it's the host the team originally said they'd use for the website anyway. Using the Vercel MCP tools directly (no browser automation needed):

1. Resolve the Vercel team scope (`list_teams`) so the project isn't created in the wrong account.
2. Link a new Vercel project to the existing `qwfice/agrointel-ai` GitHub repo (`create_git_project`), targeting `api/main.py` as a FastAPI app (`framework: "fastapi"`), which triggers an automatic first deploy.
3. **Credentials stay the user's to enter, not mine:** after the project exists, the user sets `GEMINI_API_KEY`, `EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD` directly in the Vercel dashboard's project settings (Environment Variables) - I won't see or type the values in, consistent with how every other credential in this project has been handled.
4. Once deployed (and env vars set), verify the live public URL actually responds correctly: `/`, `/indicators` (POWER-only fast path first, since SMAP may still be rate-limited), `/score`, `/chat`.
5. Remove the now-unused `render.yaml`. Commit, push, update GOALS.md. Wiring up Bubble's API Connector to this URL is the next step after this one, not part of this step.

---

## Build a public API so FieldCycle (Bubble) can call our AI

**Status:** done (local only — deployment is a separate follow-up step)

**Brief:** FieldCycle's Bubble app already has the API Connector plugin installed with 3 working integrations (NASA POWER, Photon OpenStreetMap geocoding, SRTM via OpenTopoData) - the exact same pattern we need, just no entry for our AI yet. This step builds what that entry would point to:

1. A small FastAPI app (`api/main.py` or similar) wrapping existing logic, no duplicated code:
   - `POST /indicators` - {lat, lon} -> real computed indicators (reuses `src/indicators/live.py`)
   - `POST /score` - {indicators, weights?} -> ranked strategy comparisons (reuses `src/scoring`, `src/explanations`)
   - `POST /chat` - {question, location_label, indicators, comparisons} -> grounded answer (reuses `src/chat/assistant.py`)
2. Test it locally (not yet connected to Bubble) to confirm each endpoint works via real requests.
3. Once locally verified, a separate follow-up step covers actually deploying it publicly and wiring up the Bubble API Connector entry - that needs a hosting decision from the user first.

**Note on timing:** SMAP appears to be rate-limited for us right now (confirmed hang both in the app and standalone) - the `/indicators` endpoint will be built and tested with that in mind (POWER-driven indicators, which aren't rate-limited, verified first; SMAP re-verified once it's no longer throttled).

---

## Make the main app location-agnostic (any latitude/longitude, not just Kern County)

**Status:** done — verified with Kern County CA and Punjab India producing genuinely different real results; found and fixed a real SMAP login bug and a missing-timeout bug along the way

**Brief:** our NASA data clients (`src/data/nasa_power.py`, `nasa_smap.py`, `nasa_gpm.py`) are already global - they take any lat/lon. The gap is that `app.py` only ever loads Kern County's pre-saved CSV, so the scores and chat assistant only ever "know" that one place. This fixes that:

1. Add a location input (latitude/longitude) to `app.py`, replacing the hardcoded Kern County CSV load.
2. On submit, live-fetch real NASA POWER data for that point (fast, proven - seconds for 5 years at Kern County) and compute real indicators from it (temp/rainfall anomalies, dry spell, extreme rainfall) - these alone drive most of the scoring already.
3. For soil moisture: fetch one recent day of SMAP for that point (not a 30-day average) - slower (~30-60s, spinner shown), but a real current-conditions snapshot for that specific place instead of reusing Kern County's number.
4. Run the real scoring model + chat assistant on this live-pulled data, so both are genuinely location-specific.
5. Verify with two different real locations (not Kern County again) to prove it's not another hardcoded swap.
6. Commit, push, update GOALS.md/PLAN.md.

---

## Chat assistant (Gemini API), grounded in real computed data

**Status:** done — grounded (real data) and ungrounded (off-scope) questions both tested and behaved correctly

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

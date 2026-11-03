# Goals

These are the gaps between the original research plan (`docs/AGROINTEL_AI_Research_Plan.pdf`) and an actual working decision-support tool, turned into concrete build goals. Each one will get its own written plan (see workflow below) before any code is changed.

- [x] **Pull real NASA data.** Nothing in the research plan has touched a real NASA dataset yet. Goal: working integrations with NASA POWER (meteorology) at minimum, then SMAP (soil moisture) and GPM (precipitation), for real coordinates — not just named as sources. *Done: `src/data/nasa_power.py`, `nasa_smap.py`, `nasa_gpm.py`, all proven against real Kern County, CA coordinates with saved outputs.*
- [x] **Compute real environmental indicators.** Turn raw pulled data into the anomaly/risk indicators the plan describes (temperature anomalies, rainfall anomalies, soil moisture anomalies, consecutive dry periods, etc.) for at least one real location. *Done: `src/indicators/environmental.py`, verified on Kern County, CA June 2023 (-3.78°C temp anomaly, +300% rain anomaly, 11-day dry spell, 2 extreme rainfall days). Soil moisture anomaly is a simplified relative-wetness measure, not a true multi-year anomaly — SMAP history pulled so far is too short for that; a longer SMAP pull is a future follow-up.*
- [x] **Build and run the scoring model.** Implement the weighted multi-criteria rotation-scoring model (Section 7 of the plan) and actually run it to produce scores for the three strategies (Conventional, Legume-Integrated, Soil-Conservation) rather than leaving it as an unrun formula. *Done: `src/scoring/`, run for Kern County June 2023 — Soil-Conservation 71.9, Legume 57.4, Conventional 32.3. Climate resilience and erosion reduction use real computed indicators; soil health, water use, pest/disease, and economic criteria use documented baseline assumptions pending real FAO/market data integration.*
- [x] **Produce real strategy comparisons with explanations.** For at least one test location, generate the comparison the challenge requires: score, supporting evidence, benefits, information gaps, and risks for each of the three rotation strategies. *Done: `src/explanations/narrative.py` + `scripts/generate_comparison.py`, producing `outputs/kern_county_comparison.md` — template-based, every evidence line cites real computed numbers.*
- [ ] **Build a minimal interface.** Some way to see the output — even a simple table/chart to start — rather than only description of an intended "interactive dashboard."
- [ ] **Make farmer priorities adjustable.** Let the weighting (soil health / water use / climate resilience / pest-cycle / erosion / economic) actually be changed, and show scores update (sensitivity).
- [ ] **Carry over the plan's honesty/limitations stance.** Keep the explicit uncertainty and "decision support, not guaranteed outcomes" framing from the research plan as the tool is built, not just as a document.

Check a box off only once the corresponding goal is actually working and verified in the repo — not when a plan for it is merely approved.

## Workflow

- Every change to this project gets a written plan first (what's changing, why, files touched) for review and approval before implementation.
- Approved work gets committed and pushed to [github.com/qwfice/agrointel-ai](https://github.com/qwfice/agrointel-ai) via git CLI.

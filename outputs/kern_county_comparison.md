# Crop Rotation Strategy Comparison — Kern County, CA

Evaluation window: June 2023 (real NASA POWER / SMAP / GPM data).

Weights used: soil_health_potential 25%, water_use_suitability 20%, climate_resilience 20%, pest_disease_interruption 15%, erosion_reduction 10%, economic_suitability 10%

> This is decision support, not a guarantee of crop outcomes. Static assumptions are called out explicitly below each strategy — a local agronomist or farmer's own knowledge should validate them before use.

## #1. Soil-Conservation (Tomato -> Cover Crop -> Leafy Vegetables) — 71.9/100

**Criterion scores:**

- soil health potential: 85.0/100
- water use suitability: 65.0/100
- climate resilience: 70.5/100
- pest disease interruption: 75.0/100
- erosion reduction: 87.6/100
- economic suitability: 35.0/100

**Supporting evidence:**

- Climate resilience scored 70.5/100. Real observed conditions: an 11-day dry spell and a -3.78C mean temperature anomaly vs. the 5-year climatology. This strategy is modeled with a 0.3x vulnerability factor to those anomalies (1.0 = most vulnerable, 0.3 = least).
- Erosion reduction scored 87.6/100. Real observed conditions included 2 day(s) exceeding the historical 90th-percentile rainfall threshold. This strategy is modeled with a 0.1x erosion-protection vulnerability factor.
- For reference, real SMAP soil moisture during the evaluation window averaged a relative wetness of 0.16 (0=driest SMAP can measure, 1=wettest) — not yet factored into water-use scoring, which remains a static assumption (see information gaps).

**Benefits:**

- Minimizes the number of bare-soil days in the rotation, reducing wind/water erosion exposure.
- Adds the most organic residue to the soil of the three strategies, supporting long-term organic matter buildup.
- Cover crop residue buffers soil temperature and moisture extremes, which real data shows matters this season (see evidence).

**Information gaps:**

- Economic suitability (35/100) assumes no direct harvest value for the cover crop; if it is grazed or sold as biomass locally, this score understates its value.
- Water-use suitability assumes a low-water cover crop species; actual water use depends on which cover crop is planted, which is not specified here.

**Risks / needs local review:**

- Lowest economic suitability of the three strategies in this model — a farmer prioritizing near-term cash flow may find this unacceptable despite its soil/climate advantages; needs a local cost-benefit check, including any conservation incentive payments not modeled here.

---

## #2. Legume-Integrated (Tomato -> Beans -> Cabbage) — 57.4/100

**Criterion scores:**

- soil health potential: 70.0/100
- water use suitability: 55.0/100
- climate resilience: 41.0/100
- pest disease interruption: 70.0/100
- erosion reduction: 47.0/100
- economic suitability: 55.0/100

**Supporting evidence:**

- Climate resilience scored 41.0/100. Real observed conditions: an 11-day dry spell and a -3.78C mean temperature anomaly vs. the 5-year climatology. This strategy is modeled with a 0.6x vulnerability factor to those anomalies (1.0 = most vulnerable, 0.3 = least).
- Erosion reduction scored 47.0/100. Real observed conditions included 2 day(s) exceeding the historical 90th-percentile rainfall threshold. This strategy is modeled with a 0.5x erosion-protection vulnerability factor.
- For reference, real SMAP soil moisture during the evaluation window averaged a relative wetness of 0.16 (0=driest SMAP can measure, 1=wettest) — not yet factored into water-use scoring, which remains a static assumption (see information gaps).

**Benefits:**

- Beans fix atmospheric nitrogen, potentially reducing synthetic nitrogen fertilizer needs for the following crop.
- Adds a distinct plant family to the rotation, helping disrupt pest and disease cycles tied to continuous vegetable cropping.
- Beans generally have a usable market value, unlike a pure cover crop.

**Information gaps:**

- Soil-health potential (70/100) assumes typical nitrogen fixation; actual nitrogen contribution depends on bean variety, biomass, and residue management not modeled here (the research plan flags this explicitly).
- Water-use and economic suitability scores are static assumptions pending real local data.

**Risks / needs local review:**

- If the bean variety or planting density is wrong for local conditions, the assumed nitrogen and water-use benefits may not materialize — needs local agronomic review before adoption.

---

## #3. Conventional (Tomato -> Cabbage -> Lettuce) — 32.3/100

**Criterion scores:**

- soil health potential: 30.0/100
- water use suitability: 40.0/100
- climate resilience: 8.4/100
- pest disease interruption: 45.0/100
- erosion reduction: 14.0/100
- economic suitability: 70.0/100

**Supporting evidence:**

- Climate resilience scored 8.4/100. Real observed conditions: an 11-day dry spell and a -3.78C mean temperature anomaly vs. the 5-year climatology. This strategy is modeled with a 1.0x vulnerability factor to those anomalies (1.0 = most vulnerable, 0.3 = least).
- Erosion reduction scored 14.0/100. Real observed conditions included 2 day(s) exceeding the historical 90th-percentile rainfall threshold. This strategy is modeled with a 1.0x erosion-protection vulnerability factor.
- For reference, real SMAP soil moisture during the evaluation window averaged a relative wetness of 0.16 (0=driest SMAP can measure, 1=wettest) — not yet factored into water-use scoring, which remains a static assumption (see information gaps).

**Benefits:**

- Familiar practice with established local market channels for every crop in the sequence.
- No new crop types or equipment needed.

**Information gaps:**

- Water-use suitability (40/100) and economic suitability (70/100) are static agronomic assumptions, not derived from local FAO crop-water data or actual market prices.
- Pest/disease interruption (45/100) is a general assumption about family diversity, not based on local pest records.

**Risks / needs local review:**

- Real computed data shows this strategy scored weakest on climate resilience (modeled as most vulnerable to the season's dry spell and temperature anomaly) and erosion reduction — a local agronomist should assess whether this specific field can tolerate that exposure.

---

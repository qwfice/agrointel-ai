"""Compute real environmental risk indicators for Kern County, CA from the
NASA POWER and SMAP data already pulled by explore_power_data.py and
explore_smap_gpm_data.py (run those first if outputs/ is empty).

Usage:
    python scripts/compute_indicators.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.indicators.environmental import (
    extreme_rainfall_days,
    longest_dry_spell,
    rainfall_anomaly_pct,
    soil_moisture_relative_wetness,
    temperature_anomaly,
)

OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

# Evaluate the most recent full month in the POWER record as the "current
# conditions" window, against the rest of the 5-year record as climatology.
EVAL_START, EVAL_END = "2023-06-01", "2023-06-30"


def main() -> None:
    power_path = OUT_DIR / "kern_county_power_daily.csv"
    smap_gpm_path = OUT_DIR / "kern_county_smap_gpm.csv"
    if not power_path.exists() or not smap_gpm_path.exists():
        raise SystemExit(
            "Missing input data. Run scripts/explore_power_data.py and "
            "scripts/explore_smap_gpm_data.py first."
        )

    power = pd.read_csv(power_path, index_col="date", parse_dates=True)
    smap_gpm = pd.read_csv(smap_gpm_path, index_col="date", parse_dates=True)

    print(f"=== Environmental indicators: Kern County, CA, {EVAL_START} to {EVAL_END} ===\n")

    temp_anom = temperature_anomaly(power, EVAL_START, EVAL_END)
    print("Temperature anomaly vs. 5-year day-of-year climatology (°C):")
    print(f"  mean: {temp_anom.mean():+.2f}   max: {temp_anom.max():+.2f}   min: {temp_anom.min():+.2f}\n")

    rain_anom = rainfall_anomaly_pct(power, EVAL_START, EVAL_END)
    print("Rainfall anomaly vs. 5-year monthly climatology (%):")
    for month, pct in rain_anom.items():
        print(f"  {month.strftime('%Y-%m')}: {pct:+.1f}%")
    print()

    dry_spell = longest_dry_spell(power, EVAL_START, EVAL_END)
    print(f"Longest dry spell (<=1mm/day) in window: {dry_spell} days\n")

    extreme_count, threshold = extreme_rainfall_days(power, EVAL_START, EVAL_END)
    print(f"Extreme rainfall days (>{threshold:.1f}mm, the 90th percentile of rainy days historically): {extreme_count}\n")

    wetness = soil_moisture_relative_wetness(smap_gpm["soil_moisture_m3m3"])
    print("Soil moisture relative wetness (0=driest SMAP can read, 1=wettest), June 2023:")
    print(f"  mean: {wetness.mean():.2f}   max: {wetness.max():.2f}   min: {wetness.min():.2f}")
    print("  (NOT a historical anomaly — not enough SMAP history pulled yet; see GOALS.md)\n")

    summary = pd.DataFrame(
        {
            "indicator": [
                "temp_anomaly_mean_c",
                "temp_anomaly_max_c",
                "longest_dry_spell_days",
                "extreme_rainfall_days",
                "soil_moisture_relative_wetness_mean",
            ],
            "value": [
                round(float(temp_anom.mean()), 2),
                round(float(temp_anom.max()), 2),
                dry_spell,
                extreme_count,
                round(float(wetness.mean()), 3),
            ],
        }
    )
    csv_path = OUT_DIR / "kern_county_indicators.csv"
    summary.to_csv(csv_path, index=False)
    print(f"Saved summary to {csv_path}")


if __name__ == "__main__":
    main()

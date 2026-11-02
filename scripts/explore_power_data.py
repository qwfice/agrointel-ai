"""Pull real NASA POWER data for Kern County, CA (research-plan Location 1)
and plot temperature / precipitation trends, to prove the data pull works.

Usage:
    python scripts/explore_power_data.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.nasa_power import fetch_daily

# Kern County, CA (Central Valley) — research plan Location 1.
LAT, LON = 35.3733, -119.0187
START, END = "20190101", "20231231"

OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def main() -> None:
    print(f"Fetching NASA POWER daily data for ({LAT}, {LON}), {START}-{END}...")
    df = fetch_daily(LAT, LON, START, END)
    print(df.describe())

    OUT_DIR.mkdir(exist_ok=True)
    csv_path = OUT_DIR / "kern_county_power_daily.csv"
    df.to_csv(csv_path)
    print(f"Saved raw data to {csv_path}")

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

    axes[0].plot(df.index, df["temp_mean_c"], label="Mean temp (°C)", color="tab:red")
    axes[0].plot(df.index, df["temp_max_c"], label="Max temp (°C)", alpha=0.4, color="tab:orange")
    axes[0].set_ylabel("Temperature (°C)")
    axes[0].set_title("Kern County, CA — NASA POWER daily temperature")
    axes[0].legend()

    monthly_precip = df["precip_mm"].resample("MS").sum()
    axes[1].bar(monthly_precip.index, monthly_precip.values, width=20, color="tab:blue")
    axes[1].set_ylabel("Monthly precipitation (mm)")
    axes[1].set_title("Kern County, CA — NASA POWER monthly precipitation total")

    fig.tight_layout()
    png_path = OUT_DIR / "kern_county_power_trends.png"
    fig.savefig(png_path, dpi=150)
    print(f"Saved plot to {png_path}")


if __name__ == "__main__":
    main()

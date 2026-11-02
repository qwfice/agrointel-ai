"""Pull real NASA SMAP soil-moisture and GPM precipitation data for Kern
County, CA and plot them together, to prove both integrations work.

Scoped to a 30-day window (not years, like the POWER pull) because each
SMAP granule is a ~600+ MB global file — see src/data/nasa_smap.py.
Downloads happen concurrently (6 workers) to keep this reasonably fast.

Requires:
  - ~/.netrc with your NASA Earthdata credentials
  - Earthdata account has approved the "NASA GESDISC DATA ARCHIVE" app
    (https://urs.earthdata.nasa.gov/profile -> Applications)

Usage:
    python scripts/explore_smap_gpm_data.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import earthaccess
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.nasa_gpm import fetch_daily_point as fetch_gpm
from src.data.nasa_smap import fetch_daily_point as fetch_smap

# Kern County, CA (Central Valley) — research plan Location 1.
LAT, LON = 35.3733, -119.0187
START, END = "2023-06-01", "2023-06-30"

OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def main() -> None:
    earthaccess.login(strategy="netrc")

    print(f"Fetching SMAP soil moisture for ({LAT}, {LON}), {START} to {END}...")
    soil_moisture = fetch_smap(LAT, LON, START, END)
    print(soil_moisture.describe())

    print(f"Fetching GPM precipitation for ({LAT}, {LON}), {START} to {END}...")
    precip = fetch_gpm(LAT, LON, START, END)
    print(precip.describe())

    OUT_DIR.mkdir(exist_ok=True)
    combined = soil_moisture.to_frame().join(precip, how="outer")
    csv_path = OUT_DIR / "kern_county_smap_gpm.csv"
    combined.to_csv(csv_path)
    print(f"Saved combined series to {csv_path}")

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

    axes[0].plot(soil_moisture.index, soil_moisture.values, marker="o", color="tab:brown")
    axes[0].set_ylabel("Soil moisture (cm³/cm³)")
    axes[0].set_title("Kern County, CA — NASA SMAP surface soil moisture (AM overpass)")

    axes[1].bar(precip.index, precip.values, color="tab:blue")
    axes[1].set_ylabel("Precipitation (mm/day)")
    axes[1].set_title("Kern County, CA — NASA GPM IMERG daily precipitation")

    fig.tight_layout()
    png_path = OUT_DIR / "kern_county_smap_gpm.png"
    fig.savefig(png_path, dpi=150)
    print(f"Saved plot to {png_path}")


if __name__ == "__main__":
    main()

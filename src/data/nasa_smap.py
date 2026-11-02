"""Client for NASA SMAP L3 Enhanced soil moisture (SPL3SMP_E) via earthaccess.

Each daily granule is a global ~9km EASE-grid HDF5 file (~600+ MB), so this
downloads one granule at a time, extracts the value at the grid cell nearest
the requested point, then deletes the file — it never keeps raw granules on
disk for more than one iteration.

Requires a NASA Earthdata login configured in ~/.netrc.
Docs: https://nsidc.org/data/spl3smp_e
"""

from __future__ import annotations

import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import earthaccess
import h5py
import numpy as np
import pandas as pd

SHORT_NAME = "SPL3SMP_E"
FILL_VALUE = -9999.0


def _nearest_value(lat_grid: np.ndarray, lon_grid: np.ndarray, data: np.ndarray, lat: float, lon: float) -> float:
    valid = (lat_grid > -9990) & (lon_grid > -9990)
    dist = np.where(valid, (lat_grid - lat) ** 2 + (lon_grid - lon) ** 2, np.inf)
    idx = np.unravel_index(np.argmin(dist), dist.shape)
    value = data[idx]
    return float("nan") if value == FILL_VALUE else float(value)


def _extract_day(h5_path: Path, lat: float, lon: float, overpass: str = "AM") -> float:
    group_name = f"Soil_Moisture_Retrieval_Data_{overpass}"
    with h5py.File(h5_path, "r") as f:
        if group_name not in f:
            return float("nan")
        grp = f[group_name]
        return _nearest_value(grp["latitude"][:], grp["longitude"][:], grp["soil_moisture"][:], lat, lon)


def _download_and_extract(granule, lat: float, lon: float, overpass: str, tmp_dir: str) -> tuple[pd.Timestamp, float]:
    date_str = granule["umm"]["TemporalExtent"]["RangeDateTime"]["BeginningDateTime"][:10]
    date = pd.Timestamp(date_str)
    # Each worker downloads into its own subdirectory so concurrent granules
    # (which can share a filename pattern) never collide or get deleted
    # out from under another in-flight worker.
    worker_dir = Path(tmp_dir) / date_str
    worker_dir.mkdir(exist_ok=True)
    paths = earthaccess.download([granule], str(worker_dir))
    h5_path = Path(paths[0])
    try:
        return date, _extract_day(h5_path, lat, lon, overpass)
    finally:
        h5_path.unlink(missing_ok=True)


def fetch_daily_point(
    lat: float, lon: float, start: str, end: str, overpass: str = "AM", max_workers: int = 6
) -> pd.Series:
    """Fetch a daily surface soil-moisture time series at a point.

    Args:
        lat, lon: location in decimal degrees.
        start, end: dates as "YYYY-MM-DD".
        overpass: "AM" (descending) or "PM" (ascending) SMAP overpass.
        max_workers: number of granules to download concurrently. Each
            granule is ~600+ MB, so this trades bandwidth/memory for speed.

    Returns:
        pandas Series indexed by date, soil moisture in cm^3/cm^3 (NaN where
        no granule exists or the point has no valid retrieval that day).
    """
    results = earthaccess.search_data(
        short_name=SHORT_NAME,
        temporal=(start, end),
        bounding_box=(lon - 0.5, lat - 0.5, lon + 0.5, lat + 0.5),
    )

    values: dict[pd.Timestamp, float] = {}
    with tempfile.TemporaryDirectory() as tmp_dir, ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(_download_and_extract, g, lat, lon, overpass, tmp_dir) for g in results]
        for future in as_completed(futures):
            date, value = future.result()
            values[date] = value

    series = pd.Series(values, name="soil_moisture_m3m3").sort_index()
    series.index.name = "date"
    return series

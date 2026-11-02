"""Client for NASA GPM IMERG Final daily precipitation (GPM_3IMERGDF) via earthaccess.

Daily granules are global, 0.1-degree grids (~30 MB each). Downloads one
granule at a time, extracts the value nearest the requested point, then
deletes the file.

Requires a NASA Earthdata login configured in ~/.netrc, and requires the
Earthdata account to have approved the "NASA GESDISC DATA ARCHIVE"
application at least once (https://urs.earthdata.nasa.gov/profile).
Docs: https://gpm.nasa.gov/data/directory
"""

from __future__ import annotations

import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import earthaccess
import pandas as pd
import xarray as xr

SHORT_NAME = "GPM_3IMERGDF"


def _download_and_extract(granule, lat: float, lon: float, tmp_dir: str) -> tuple[pd.Timestamp, float]:
    date_str = granule["umm"]["TemporalExtent"]["RangeDateTime"]["BeginningDateTime"][:10]
    date = pd.Timestamp(date_str)
    worker_dir = Path(tmp_dir) / date_str
    worker_dir.mkdir(exist_ok=True)
    paths = earthaccess.download([granule], str(worker_dir))
    nc_path = Path(paths[0])
    try:
        with xr.open_dataset(nc_path) as ds:
            point = ds["precipitation"].sel(lon=lon, lat=lat, method="nearest")
            return date, float(point.isel(time=0).values)
    finally:
        nc_path.unlink(missing_ok=True)


def fetch_daily_point(lat: float, lon: float, start: str, end: str, max_workers: int = 6) -> pd.Series:
    """Fetch a daily precipitation time series at a point.

    Args:
        lat, lon: location in decimal degrees.
        start, end: dates as "YYYY-MM-DD".
        max_workers: number of granules to download concurrently.

    Returns:
        pandas Series indexed by date, precipitation in mm/day.
    """
    results = earthaccess.search_data(
        short_name=SHORT_NAME,
        temporal=(start, end),
        bounding_box=(lon - 0.5, lat - 0.5, lon + 0.5, lat + 0.5),
    )

    values: dict[pd.Timestamp, float] = {}
    with tempfile.TemporaryDirectory() as tmp_dir, ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(_download_and_extract, g, lat, lon, tmp_dir) for g in results]
        for future in as_completed(futures):
            date, value = future.result()
            values[date] = value

    series = pd.Series(values, name="precip_mm").sort_index()
    series.index.name = "date"
    return series

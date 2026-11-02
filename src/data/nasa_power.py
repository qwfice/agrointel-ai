"""Client for the NASA POWER Daily Point API (no API key required).

Docs: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
"""

from __future__ import annotations

import pandas as pd
import requests

POWER_DAILY_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

# NASA POWER parameter codes we care about for crop-rotation analysis.
PARAMETERS = {
    "T2M": "temp_mean_c",
    "T2M_MAX": "temp_max_c",
    "T2M_MIN": "temp_min_c",
    "PRECTOTCORR": "precip_mm",
    "ALLSKY_SFC_SW_DWN": "solar_radiation_kwh_m2",
    "WS2M": "wind_speed_m_s",
}


def fetch_daily(
    lat: float,
    lon: float,
    start: str,
    end: str,
    parameters: dict[str, str] | None = None,
    community: str = "AG",
) -> pd.DataFrame:
    """Fetch daily meteorological data from NASA POWER for a point location.

    Args:
        lat, lon: location in decimal degrees.
        start, end: dates as "YYYYMMDD".
        parameters: mapping of POWER parameter code -> output column name.
            Defaults to PARAMETERS above.
        community: POWER user community ("AG" = agroclimatology).

    Returns:
        DataFrame indexed by date, one column per requested parameter.
        NASA POWER uses -999 as a fill value for missing observations;
        these are converted to NaN.
    """
    params = parameters or PARAMETERS
    response = requests.get(
        POWER_DAILY_URL,
        params={
            "parameters": ",".join(params.keys()),
            "community": community,
            "longitude": lon,
            "latitude": lat,
            "start": start,
            "end": end,
            "format": "JSON",
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()

    raw = payload["properties"]["parameter"]
    df = pd.DataFrame({params[code]: values for code, values in raw.items()})
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df.index.name = "date"
    df = df.replace(-999, pd.NA).apply(pd.to_numeric)
    return df

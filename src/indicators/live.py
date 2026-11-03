"""Live, location-agnostic version of what compute_indicators.py does for
Kern County: pull real NASA data for any lat/lon and compute the real
indicators from it, on demand.

POWER is fast (seconds, proven) and drives most of the scoring - the
5-year history plus a recent 30-day evaluation window. SMAP is slow (one
granule is ~600+ MB), so this only fetches ONE recent day for a current
soil-moisture snapshot, not a multi-day average - a real reading for that
spot, just a single-day one rather than a 30-day one. If even that fails
or returns nothing (SMAP has real coverage gaps), soil moisture is
reported as unavailable rather than silently reused from elsewhere.
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import date, timedelta

import earthaccess
import pandas as pd

from src.data.nasa_power import fetch_daily as fetch_power
from src.data.nasa_smap import fetch_daily_point as fetch_smap
from src.indicators.environmental import (
    extreme_rainfall_days,
    longest_dry_spell,
    rainfall_anomaly_pct,
    soil_moisture_relative_wetness,
    temperature_anomaly,
)

POWER_HISTORY_YEARS = 5
EVAL_WINDOW_DAYS = 30
SMAP_LOOKBACK_DAYS = 10  # search this far back for the most recent available SMAP day
SMAP_TIMEOUT_SECONDS = 90  # hard cap - NASA's SMAP service can silently stall under load

_earthaccess_logged_in = False


def _ensure_earthaccess_login() -> None:
    """Log in to Earthdata once per process (needed before any SMAP fetch).

    Prefers EARTHDATA_USERNAME/EARTHDATA_PASSWORD environment variables
    (what a deployed server like Render would have set) and falls back to
    ~/.netrc (local dev machines) when those aren't set.
    """
    global _earthaccess_logged_in
    if _earthaccess_logged_in:
        return
    if os.environ.get("EARTHDATA_USERNAME") and os.environ.get("EARTHDATA_PASSWORD"):
        earthaccess.login(strategy="environment")
    else:
        earthaccess.login(strategy="netrc")
    _earthaccess_logged_in = True


def fetch_and_compute_indicators(lat: float, lon: float, include_soil_moisture: bool = True) -> dict:
    """Live-fetch real NASA data for (lat, lon) and compute real indicators.

    Args:
        lat, lon: location.
        include_soil_moisture: set False to skip the SMAP fetch entirely
            (POWER-driven indicators only) - useful when SMAP is known to
            be slow/rate-limited and callers need a fast, reliable response.

    Returns a dict with the same keys compute_indicators.py's CSV output
    uses, so it's a drop-in replacement for the pre-saved Kern County data.
    """
    today = date.today()
    power_start = (today - timedelta(days=365 * POWER_HISTORY_YEARS)).strftime("%Y%m%d")
    power_end = today.strftime("%Y%m%d")

    power = fetch_power(lat, lon, power_start, power_end)
    power = power.dropna(subset=["temp_mean_c", "precip_mm"])
    if power.empty:
        raise RuntimeError("NASA POWER returned no usable data for this location.")

    eval_end = power.index.max()
    eval_start = eval_end - pd.Timedelta(days=EVAL_WINDOW_DAYS - 1)

    temp_anom = temperature_anomaly(power, str(eval_start.date()), str(eval_end.date()))
    dry_spell = longest_dry_spell(power, str(eval_start.date()), str(eval_end.date()))
    extreme_count, _ = extreme_rainfall_days(power, str(eval_start.date()), str(eval_end.date()))

    indicators = {
        "temp_anomaly_mean_c": round(float(temp_anom.mean()), 2),
        "temp_anomaly_max_c": round(float(temp_anom.max()), 2),
        "longest_dry_spell_days": dry_spell,
        "extreme_rainfall_days": extreme_count,
    }

    if not include_soil_moisture:
        indicators["soil_moisture_relative_wetness_mean"] = None
        return indicators

    smap_start = (eval_end.date() - timedelta(days=SMAP_LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    smap_end = eval_end.date().strftime("%Y-%m-%d")
    try:
        _ensure_earthaccess_login()
        # SMAP's service can silently stall under load rather than erroring -
        # run it in a worker thread with a hard timeout so this function
        # always returns in bounded time, which matters a lot once this is
        # behind an API that other callers (e.g. FieldCycle) depend on.
        # NOT using `with` here: ThreadPoolExecutor.__exit__ calls
        # shutdown(wait=True), which would block on the stuck thread anyway -
        # shutdown(wait=False) lets this function return on time even if the
        # background download never finishes.
        pool = ThreadPoolExecutor(max_workers=1)
        try:
            future = pool.submit(fetch_smap, lat, lon, smap_start, smap_end)
            smap_series = future.result(timeout=SMAP_TIMEOUT_SECONDS).dropna()
        finally:
            pool.shutdown(wait=False)
        if smap_series.empty:
            indicators["soil_moisture_relative_wetness_mean"] = None
        else:
            latest_value = smap_series.iloc[-1]
            wetness = soil_moisture_relative_wetness(pd.Series([latest_value])).iloc[0]
            indicators["soil_moisture_relative_wetness_mean"] = round(float(wetness), 3)
    except FutureTimeoutError:
        indicators["soil_moisture_relative_wetness_mean"] = None
    except Exception:
        indicators["soil_moisture_relative_wetness_mean"] = None

    return indicators

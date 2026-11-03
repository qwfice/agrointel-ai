"""Environmental risk indicators computed from real pulled NASA data.

These implement the indicators the research plan's Stage 3 ("Environmental
risk analysis") describes: anomalies relative to historical climatology,
dry-spell length, and extreme-event frequency. All of them operate on data
already fetched by src/data/*.py — they do no network I/O themselves.
"""

from __future__ import annotations

import pandas as pd

# SMAP's documented physically valid range for surface soil moisture.
# https://nsidc.org/data/spl3smp_e (valid_min / valid_max attributes)
SMAP_VALID_MIN = 0.02
SMAP_VALID_MAX = 0.50


def temperature_anomaly(history: pd.DataFrame, period_start: str, period_end: str) -> pd.Series:
    """Daily mean-temperature anomaly vs. the day-of-year climatology.

    Args:
        history: DataFrame with a "temp_mean_c" column and a datetime index,
            covering enough years to form a meaningful climatology.
        period_start, period_end: the window to compute anomalies for
            (can be inside or outside `history`'s own range).

    Returns:
        Series of (actual - climatological mean) in degrees C, indexed by date.
    """
    climatology = history["temp_mean_c"].groupby(history.index.dayofyear).mean()
    period = history.loc[period_start:period_end, "temp_mean_c"]
    expected = period.index.dayofyear.to_series(index=period.index).map(climatology)
    anomaly = (period - expected).rename("temp_anomaly_c")
    return anomaly


def rainfall_anomaly_pct(history: pd.DataFrame, period_start: str, period_end: str) -> pd.Series:
    """Monthly precipitation totals vs. the historical monthly average, as % difference.

    Args:
        history: DataFrame with a "precip_mm" column and a datetime index.
        period_start, period_end: window to evaluate.

    Returns:
        Series indexed by month-start timestamp: % difference from that
        calendar month's historical average total (e.g. +40.0 = 40% wetter
        than normal, -100.0 = a month with no rain at all where some is normal).
    """
    monthly_totals = history["precip_mm"].resample("MS").sum()
    monthly_climatology = monthly_totals.groupby(monthly_totals.index.month).mean()

    period_monthly = history.loc[period_start:period_end, "precip_mm"].resample("MS").sum()
    expected = period_monthly.index.month.map(monthly_climatology)
    pct_diff = (period_monthly - expected) / expected.replace(0, float("nan")) * 100
    pct_diff.name = "rainfall_anomaly_pct"
    return pct_diff


def longest_dry_spell(df: pd.DataFrame, period_start: str, period_end: str, dry_threshold_mm: float = 1.0) -> int:
    """Longest run of consecutive days with precipitation below `dry_threshold_mm`.

    Args:
        df: DataFrame with a "precip_mm" column and a datetime index.
        period_start, period_end: window to evaluate.
        dry_threshold_mm: a day counts as "dry" if precip is at or below this.

    Returns:
        Length, in days, of the longest consecutive dry spell in the window.
    """
    precip = df.loc[period_start:period_end, "precip_mm"]
    is_dry = precip <= dry_threshold_mm
    # Each dry run gets a stable group id; count the largest group's size.
    run_id = (~is_dry).cumsum()
    run_lengths = is_dry.groupby(run_id).sum()
    return int(run_lengths.max()) if not run_lengths.empty else 0


def extreme_rainfall_days(
    history: pd.DataFrame, period_start: str, period_end: str, percentile: float = 90.0
) -> tuple[int, float]:
    """Count of days in the period whose rainfall exceeds a historical extreme threshold.

    Args:
        history: DataFrame with a "precip_mm" column and a datetime index,
            used to establish what counts as "extreme" from the full record.
        period_start, period_end: window to evaluate.
        percentile: the percentile (over days with any rain) that defines "extreme".

    Returns:
        (count of extreme days in the period, the mm/day threshold used).
    """
    rainy_days = history.loc[history["precip_mm"] > 0, "precip_mm"]
    threshold = float(rainy_days.quantile(percentile / 100))
    period = history.loc[period_start:period_end, "precip_mm"]
    return int((period > threshold).sum()), threshold


def soil_moisture_relative_wetness(soil_moisture: pd.Series) -> pd.Series:
    """Express soil moisture as a 0-1 position within SMAP's valid physical range.

    This is NOT a historical anomaly (we don't yet have enough years of SMAP
    data pulled to build one — see GOALS.md) — it's a simpler "how wet is
    this relative to what the sensor can even read" indicator: 0 = driest
    SMAP can measure, 1 = wettest.

    Args:
        soil_moisture: Series of soil moisture in cm^3/cm^3.

    Returns:
        Series of the same shape, values in [0, 1] (NaN preserved).
    """
    clipped = soil_moisture.clip(SMAP_VALID_MIN, SMAP_VALID_MAX)
    return (clipped - SMAP_VALID_MIN) / (SMAP_VALID_MAX - SMAP_VALID_MIN)

"""Data cleaning and return calculation helpers."""

from __future__ import annotations

import pandas as pd


def clean_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise the index, remove duplicates, and drop empty rows."""
    cleaned = df.copy()
    cleaned.index = pd.to_datetime(cleaned.index)
    cleaned = cleaned[~cleaned.index.duplicated(keep="first")]
    cleaned = cleaned.sort_index()
    cleaned = cleaned.dropna(how="all")
    return cleaned


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Preserve the current dashboard behaviour while removing fully empty rows."""
    cleaned = df.copy()
    cleaned = cleaned.dropna(how="all")
    return cleaned


def add_daily_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily percentage returns from the Close column."""
    if "Close" not in df.columns:
        raise ValueError("The dataset must contain a Close column.")

    enriched = df.copy()
    enriched["Daily_Return"] = enriched["Close"].pct_change() * 100
    return enriched


def prepare_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """Run the standard preprocessing pipeline for the dashboard."""
    return add_daily_returns(handle_missing_values(clean_stock_data(df)))

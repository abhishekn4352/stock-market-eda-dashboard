"""Shared helper utilities for formatting, validation, and downloads."""

from __future__ import annotations

import re
from datetime import date

import pandas as pd


def format_currency(value: float | int | None, currency: str = "USD") -> str:
    """Format a numeric value with a currency code."""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{currency} {value:,.2f}" if currency else f"{value:,.2f}"


def format_percentage(value: float | int | None, decimals: int = 2) -> str:
    """Format a numeric value as a percentage string."""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}%"


def dataframe_to_csv(df: pd.DataFrame, include_index: bool = True) -> str:
    """Convert a DataFrame into a CSV string for Streamlit downloads."""
    return df.to_csv(index=include_index)


def validate_tickers(raw_tickers: str | list[str]) -> list[str]:
    """Validate and normalise ticker symbols entered by the user."""
    if isinstance(raw_tickers, str):
        candidates = raw_tickers.split(",")
    else:
        candidates = list(raw_tickers)

    tickers = [candidate.strip().upper() for candidate in candidates if candidate and candidate.strip()]
    if not tickers:
        raise ValueError("Please enter at least one ticker symbol.")

    invalid = [ticker for ticker in tickers if not re.fullmatch(r"[A-Z0-9.\-=^]+", ticker)]
    if invalid:
        raise ValueError(f"Invalid ticker symbol(s): {', '.join(invalid)}")

    return tickers


def validate_date_range(start_date: date, end_date: date) -> None:
    """Ensure the selected date range is valid."""
    if start_date >= end_date:
        raise ValueError("Start date must be before end date.")

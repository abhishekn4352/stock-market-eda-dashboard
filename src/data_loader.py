"""Yahoo Finance data access helpers."""

from __future__ import annotations

import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Fetch historical OHLCV data for a ticker symbol.

    Raises:
        ValueError: If the ticker is empty or no rows are returned.
        RuntimeError: If Yahoo Finance raises an unexpected error.
    """
    symbol = ticker.strip().upper()
    if not symbol:
        raise ValueError("Ticker symbol cannot be empty.")

    try:
        data = yf.download(symbol, start=start, end=end, progress=False, auto_adjust=True)
    except Exception as exc:  # pragma: no cover - surfaced in the UI
        raise RuntimeError(f"Error fetching data for {symbol}: {exc}") from exc

    if data.empty:
        raise ValueError(f"No data found for {symbol} in the selected date range.")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data.index = pd.to_datetime(data.index)
    data = data.dropna(how="all")

    if data.empty:
        raise ValueError(f"No usable data found for {symbol} after cleaning.")

    return data


@st.cache_data(ttl=300, show_spinner=False)
def fetch_company_info(ticker: str) -> dict:
    """Fetch company metadata from Yahoo Finance."""
    symbol = ticker.strip().upper()
    if not symbol:
        return {}

    try:
        info = yf.Ticker(symbol).info
    except Exception:  # pragma: no cover - surfaced as empty metadata in the UI
        return {}

    return info or {}

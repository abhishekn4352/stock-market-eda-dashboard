"""
data_loader.py
---------------
Handles all communication with Yahoo Finance via the `yfinance` library.

Responsibilities:
    - Fetch OHLCV data for a single ticker
    - Fetch OHLCV data (Close prices) for multiple tickers (for comparison)
    - Validate tickers and handle empty/invalid responses gracefully
    - Clean and standardize the resulting DataFrame
    - Cache results using Streamlit's caching to avoid repeated API calls

All functions return a tuple of (DataFrame, error_message). If error_message
is not None, the DataFrame will be empty and the caller should show a
friendly warning instead of crashing.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
import yfinance as yf


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Newer versions of yfinance sometimes return MultiIndex columns
    (e.g. ('Close', 'AAPL')) even for a single ticker. This flattens
    them back down to simple column names like 'Close'.
    """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def _clean_single_ticker_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize a raw yfinance DataFrame for a single ticker:
        - Flatten MultiIndex columns if present
        - Reset index so 'Date' becomes a normal column
        - Rename columns to a clean, consistent naming scheme
        - Drop rows with missing Close prices
        - Sort chronologically
    """
    df = _flatten_columns(df.copy())
    df = df.reset_index()

    # yfinance may name the date column 'Date' or 'Datetime' depending on interval
    date_col = "Date" if "Date" in df.columns else "Datetime"
    if date_col not in df.columns:
        # Fallback: assume first column is the date column
        date_col = df.columns[0]

    rename_map = {
        date_col: "Date",
        "Open": "Open",
        "High": "High",
        "Low": "Low",
        "Close": "Close",
        "Adj Close": "Adj Close",
        "Volume": "Volume",
    }
    df = df.rename(columns=rename_map)

    # Keep only the columns we actually use, in a predictable order
    expected_cols = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
    available_cols = [c for c in expected_cols if c in df.columns]
    df = df[available_cols]

    # If "Adj Close" wasn't returned (auto_adjust=True case), create it from Close
    if "Adj Close" not in df.columns and "Close" in df.columns:
        df["Adj Close"] = df["Close"]

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.dropna(subset=["Close"])
    df = df.sort_values("Date").reset_index(drop=True)

    # Forward-fill any remaining small gaps in OHLCV columns (e.g. occasional NaNs)
    numeric_cols = [c for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if c in df.columns]
    df[numeric_cols] = df[numeric_cols].ffill().bfill()

    return df


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
) -> tuple[pd.DataFrame, str | None]:
    """
    Fetch historical OHLCV data for a single ticker from Yahoo Finance.

    Parameters
    ----------
    ticker : str       e.g. "AAPL" or "RELIANCE.NS"
    start_date : str   "YYYY-MM-DD"
    end_date : str      "YYYY-MM-DD"
    interval : str      "1d", "1wk", or "1mo"

    Returns
    -------
    (DataFrame, error_message)
        error_message is None on success, otherwise a friendly string explaining
        what went wrong (invalid ticker, no data, network error, etc.)
    """
    ticker = (ticker or "").strip().upper()
    if not ticker:
        return pd.DataFrame(), "Please enter a stock ticker symbol."

    try:
        raw_df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False,
            auto_adjust=False,
            threads=False,
        )
    except Exception as exc:  # noqa: BLE001 - we want to catch ANY yfinance/network failure
        return pd.DataFrame(), f"Could not fetch data for '{ticker}'. Reason: {exc}"

    if raw_df is None or raw_df.empty:
        return (
            pd.DataFrame(),
            f"No data found for ticker '{ticker}'. Please check the symbol "
            f"(e.g. use 'RELIANCE.NS' for NSE stocks or 'AAPL' for US stocks) "
            f"or try a different date range.",
        )

    try:
        clean_df = _clean_single_ticker_df(raw_df)
    except Exception as exc:  # noqa: BLE001
        return pd.DataFrame(), f"Data for '{ticker}' was received but could not be processed: {exc}"

    if clean_df.empty:
        return pd.DataFrame(), f"No usable rows remained for '{ticker}' after cleaning."

    return clean_df, None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_multiple_close_prices(
    tickers: tuple[str, ...],
    start_date: str,
    end_date: str,
    interval: str = "1d",
) -> tuple[pd.DataFrame, list[str]]:
    """
    Fetch Close prices for several tickers and combine them into a single
    wide DataFrame indexed by Date, one column per ticker.

    Returns
    -------
    (combined_df, failed_tickers)
        combined_df has columns = valid tickers only.
        failed_tickers lists tickers that returned no data (so the UI can warn about them).
    """
    combined = {}
    failed = []

    for ticker in tickers:
        df, err = fetch_stock_data(ticker, start_date, end_date, interval)
        if err or df.empty:
            failed.append(ticker)
            continue
        series = df.set_index("Date")["Close"]
        combined[ticker] = series

    if not combined:
        return pd.DataFrame(), failed

    combined_df = pd.DataFrame(combined)
    combined_df = combined_df.sort_index()
    combined_df = combined_df.ffill().dropna(how="any")
    combined_df = combined_df.reset_index().rename(columns={"index": "Date"})

    return combined_df, failed

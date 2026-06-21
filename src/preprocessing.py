"""
preprocessing.py
-----------------
Data preprocessing & feature engineering applied to a clean OHLCV DataFrame
(as produced by data_loader.fetch_stock_data).

Adds derived columns used throughout the dashboard:
    - Daily Return (%)
    - Log Return
    - Cumulative Return (%)
    - Rolling Volatility (annualized %)
    - Percentage Change (Close vs previous Close)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def add_return_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add daily return, log return and cumulative return columns to the DataFrame.
    Assumes df is sorted ascending by Date and contains a 'Close' column.
    """
    df = df.copy()

    # Daily simple return, expressed as a percentage
    df["Daily Return"] = df["Close"].pct_change() * 100

    # Log return (useful for volatility & many quant calculations)
    df["Log Return"] = np.log(df["Close"] / df["Close"].shift(1))

    # Cumulative return relative to the first day in the selected period (%)
    first_close = df["Close"].iloc[0]
    df["Cumulative Return"] = (df["Close"] / first_close - 1) * 100

    # Plain percentage change column (kept separate/explicit per requirements)
    df["Pct Change"] = df["Close"].pct_change() * 100

    return df


def add_rolling_volatility(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Add an annualized rolling volatility column based on log returns.
    Volatility = std(log returns over window) * sqrt(trading days per year) * 100 (%)
    """
    df = df.copy()
    if "Log Return" not in df.columns:
        df = add_return_columns(df)

    col_name = f"Volatility ({window}d)"
    df[col_name] = (
        df["Log Return"].rolling(window=window).std() * np.sqrt(TRADING_DAYS_PER_YEAR) * 100
    )
    return df


def preprocess_stock_data(df: pd.DataFrame, volatility_window: int = 20) -> pd.DataFrame:
    """
    Convenience wrapper that runs the full preprocessing pipeline:
        1. Ensure Date is datetime
        2. Handle any remaining missing values
        3. Add return columns (daily, log, cumulative, pct change)
        4. Add rolling volatility
    """
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    numeric_cols = [c for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if c in df.columns]
    df[numeric_cols] = df[numeric_cols].ffill().bfill()

    df = add_return_columns(df)
    df = add_rolling_volatility(df, window=volatility_window)

    return df


def get_missing_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a small summary table of missing values per column (count & %)."""
    missing_count = df.isna().sum()
    missing_pct = (missing_count / len(df) * 100) if len(df) > 0 else missing_count * 0
    summary = pd.DataFrame(
        {
            "Column": missing_count.index,
            "Missing Count": missing_count.values,
            "Missing %": missing_pct.round(2).values,
        }
    )
    return summary.sort_values("Missing Count", ascending=False).reset_index(drop=True)

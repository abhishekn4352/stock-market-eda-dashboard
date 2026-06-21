"""
comparison.py
--------------
Helper functions for the "Compare Stocks" and "Risk & Returns" tabs:
    - Normalizing multiple price series to a common base (100)
    - Building a correlation matrix of daily returns
    - Building a summary table (return, volatility, Sharpe-like ratio) per ticker
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.kpi import compute_sharpe_like_ratio

TRADING_DAYS_PER_YEAR = 252


def normalize_prices(price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize each ticker's price series to a base of 100 on the first day,
    so multiple stocks (even at very different price levels) can be compared
    on the same chart.

    price_df: DataFrame with 'Date' column + one column per ticker (raw close prices)
    """
    normalized = price_df.copy()
    ticker_cols = [c for c in price_df.columns if c != "Date"]
    for col in ticker_cols:
        base_value = price_df[col].iloc[0]
        normalized[col] = (price_df[col] / base_value) * 100
    return normalized


def compute_returns_matrix(price_df: pd.DataFrame) -> pd.DataFrame:
    """Compute a DataFrame of daily % returns for each ticker column."""
    ticker_cols = [c for c in price_df.columns if c != "Date"]
    returns = price_df[ticker_cols].pct_change().dropna(how="all") * 100
    return returns


def compute_correlation_matrix(price_df: pd.DataFrame) -> pd.DataFrame:
    """Correlation matrix of daily returns between tickers (-1 to 1)."""
    returns = compute_returns_matrix(price_df)
    return returns.corr()


def build_comparison_summary(price_df: pd.DataFrame, risk_free_rate_pct: float = 0.0) -> pd.DataFrame:
    """
    Build a per-ticker summary table with:
        - Total Return (%)
        - Annualized Volatility (%)
        - Sharpe-like Ratio (simplified)

    Used for the comparison summary table and the risk-return scatter plot.
    """
    ticker_cols = [c for c in price_df.columns if c != "Date"]
    rows = []

    for ticker in ticker_cols:
        series = price_df[ticker].dropna()
        if len(series) < 2:
            continue

        total_return_pct = (series.iloc[-1] / series.iloc[0] - 1) * 100
        log_returns = np.log(series / series.shift(1)).dropna()
        annual_vol_pct = log_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR) * 100
        sharpe_like = compute_sharpe_like_ratio(total_return_pct, annual_vol_pct, risk_free_rate_pct)

        rows.append(
            {
                "Ticker": ticker,
                "Return (%)": round(total_return_pct, 2),
                "Volatility (%)": round(annual_vol_pct, 2),
                "Sharpe-like Ratio": round(sharpe_like, 3) if not np.isnan(sharpe_like) else np.nan,
            }
        )

    return pd.DataFrame(rows)

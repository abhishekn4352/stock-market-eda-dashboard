"""
kpi.py
------
Calculates the headline KPI numbers shown as cards at the top of the
Overview tab: latest price, total return, volatility, risk level, etc.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.indicators import relative_strength_index
from src.utils import risk_level_from_volatility, rsi_signal_from_value

TRADING_DAYS_PER_YEAR = 252


def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Compute all KPI values from a preprocessed OHLCV DataFrame.

    Expects df to already contain (or be able to derive):
        Close, Volume, Daily Return / Log Return columns are derived here
        if not already present, so this function works even on a "raw" clean df.

    Returns a dictionary of ready-to-display KPI values.
    """
    if df is None or df.empty:
        return {}

    close = df["Close"]

    # Compute log returns locally in case the caller passed a non-preprocessed df
    log_returns = np.log(close / close.shift(1)).dropna()
    daily_returns_pct = close.pct_change().dropna() * 100

    latest_close = float(close.iloc[-1])
    first_close = float(close.iloc[0])
    total_return_pct = (latest_close / first_close - 1) * 100 if first_close else float("nan")

    avg_daily_return_pct = float(daily_returns_pct.mean()) if not daily_returns_pct.empty else float("nan")

    annualized_volatility_pct = (
        float(log_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR) * 100) if not log_returns.empty else float("nan")
    )

    highest_price = float(close.max())
    lowest_price = float(close.min())

    total_volume = float(df["Volume"].sum()) if "Volume" in df.columns else float("nan")
    avg_volume = float(df["Volume"].mean()) if "Volume" in df.columns else float("nan")

    rsi_series = relative_strength_index(close)
    latest_rsi = float(rsi_series.iloc[-1]) if not rsi_series.empty else float("nan")

    return {
        "latest_close": latest_close,
        "total_return_pct": total_return_pct,
        "avg_daily_return_pct": avg_daily_return_pct,
        "annualized_volatility_pct": annualized_volatility_pct,
        "highest_price": highest_price,
        "lowest_price": lowest_price,
        "total_volume": total_volume,
        "avg_volume": avg_volume,
        "latest_rsi": latest_rsi,
        "risk_level": risk_level_from_volatility(annualized_volatility_pct),
        "rsi_signal": rsi_signal_from_value(latest_rsi),
    }


def compute_sharpe_like_ratio(annual_return_pct: float, annual_volatility_pct: float, risk_free_rate_pct: float = 0.0) -> float:
    """
    A simplified Sharpe-like ratio = (Annual Return - Risk Free Rate) / Annual Volatility.
    This is a teaching approximation (true Sharpe uses daily excess returns), useful for
    comparing risk-adjusted performance across stocks in the Compare/Risk tabs.
    """
    if annual_volatility_pct in (0, None) or pd.isna(annual_volatility_pct):
        return float("nan")
    return (annual_return_pct - risk_free_rate_pct) / annual_volatility_pct

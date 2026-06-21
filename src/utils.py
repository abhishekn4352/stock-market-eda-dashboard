"""
utils.py
--------
Small, reusable helper functions shared across the dashboard.
Keeping these in one place avoids duplicated code in app.py and other modules.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def format_currency(value: float, symbol: str = "$") -> str:
    """Format a number as a currency string, e.g. $1,234.56."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    return f"{symbol}{value:,.2f}"


def format_percent(value: float, decimals: int = 2) -> str:
    """Format a fraction or percentage-like float as a percentage string."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    return f"{value:.{decimals}f}%"


def detect_currency_symbol(ticker: str) -> str:
    """
    Pick a sensible currency symbol based on the ticker suffix.
    Indian tickers (NSE/BSE) end in .NS / .BO and are quoted in INR.
    Everything else defaults to USD ($).
    """
    ticker = ticker.upper().strip()
    if ticker.endswith(".NS") or ticker.endswith(".BO"):
        return "\u20b9"  # Rupee symbol
    return "$"


def risk_level_from_volatility(annual_volatility_pct: float) -> str:
    """
    Classify annualized volatility (%) into a simple risk bucket.
    These thresholds are a reasonable rule-of-thumb for educational use,
    not formal financial advice.
    """
    if annual_volatility_pct is None or np.isnan(annual_volatility_pct):
        return "Unknown"
    if annual_volatility_pct < 20:
        return "Low Risk"
    elif annual_volatility_pct < 35:
        return "Moderate Risk"
    elif annual_volatility_pct < 50:
        return "High Risk"
    else:
        return "Very High Risk"


def rsi_signal_from_value(rsi_value: float) -> str:
    """Translate the latest RSI value into a human readable signal."""
    if rsi_value is None or np.isnan(rsi_value):
        return "Unknown"
    if rsi_value >= 70:
        return "Overbought"
    elif rsi_value <= 30:
        return "Oversold"
    else:
        return "Neutral"


def safe_pct(numerator: float, denominator: float) -> float:
    """Safely compute a percentage, returning NaN instead of raising on /0."""
    try:
        if denominator in (0, None) or pd.isna(denominator):
            return float("nan")
        return (numerator / denominator) * 100
    except (TypeError, ZeroDivisionError):
        return float("nan")


def clean_ticker_list(raw_text: str) -> list[str]:
    """
    Turn a comma separated string like 'aapl, msft , TSLA' into a clean,
    de-duplicated, upper-cased list: ['AAPL', 'MSFT', 'TSLA'].
    """
    if not raw_text:
        return []
    tickers = [t.strip().upper() for t in raw_text.split(",") if t.strip()]
    # De-duplicate while preserving order
    seen = set()
    unique_tickers = []
    for t in tickers:
        if t not in seen:
            seen.add(t)
            unique_tickers.append(t)
    return unique_tickers


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to UTF-8 encoded CSV bytes for st.download_button."""
    return df.to_csv(index=False).encode("utf-8")


SAMPLE_TICKERS_INDIA = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "SBIN.NS"]
SAMPLE_TICKERS_US = ["AAPL", "MSFT", "TSLA", "NVDA", "GOOGL"]

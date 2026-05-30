"""Technical indicators, KPIs, and comparative analysis helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add moving averages, volatility, Bollinger Bands, and RSI columns."""
    enriched = df.copy()
    close = enriched["Close"]

    for window in (20, 50, 100):
        enriched[f"MA{window}"] = close.rolling(window=window).mean()

    enriched["Volatility"] = enriched["Daily_Return"].rolling(21).std() * np.sqrt(252)

    rolling_mean = close.rolling(20).mean()
    rolling_std = close.rolling(20).std()
    enriched["BB_Upper"] = rolling_mean + 2 * rolling_std
    enriched["BB_Lower"] = rolling_mean - 2 * rolling_std
    enriched["BB_Mid"] = rolling_mean

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    enriched["RSI"] = 100 - (100 / (1 + rs))

    return enriched


def generate_signal(df: pd.DataFrame) -> str:
    """Generate a simple MA20/MA50 crossover signal."""
    if "MA20" not in df.columns or "MA50" not in df.columns:
        return "HOLD"

    valid_rows = df.dropna(subset=["MA20", "MA50"])
    if valid_rows.empty:
        return "HOLD"

    last_row = valid_rows.iloc[-1]
    if last_row["MA20"] > last_row["MA50"]:
        return "BUY"
    if last_row["MA20"] < last_row["MA50"]:
        return "SELL"
    return "HOLD"


def calculate_stock_kpis(df: pd.DataFrame) -> dict:
    """Calculate the headline metrics shown at the top of each stock section."""
    first_close = float(df["Close"].iloc[0])
    last_close = float(df["Close"].iloc[-1])
    total_return = ((last_close - first_close) / first_close) * 100

    return {
        "current_price": last_close,
        "period_high": float(df["High"].max()),
        "period_low": float(df["Low"].min()),
        "average_volume": float(df["Volume"].mean()),
        "total_return": float(total_return),
    }


def calculate_statistical_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a numeric statistical summary for the EDA view."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return pd.DataFrame()
    summary = numeric_df.describe().T.round(4)
    summary.index.name = "Column"
    return summary


def calculate_risk_return_statistics(data_by_ticker: dict[str, pd.DataFrame], risk_free_rate: float = 0.05) -> pd.DataFrame:
    """Calculate return, risk, and Sharpe ratio for multiple tickers."""
    records: list[dict] = []

    for ticker, df in data_by_ticker.items():
        returns = df["Daily_Return"].dropna()
        if returns.empty:
            continue

        total_return = ((df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1) * 100
        annual_risk = returns.std() * np.sqrt(252)
        sharpe_ratio = (
            (returns.mean() * 252 - risk_free_rate) / (returns.std() * np.sqrt(252))
            if returns.std() != 0
            else 0
        )

        records.append(
            {
                "Ticker": ticker,
                "Total_Return": round(float(total_return), 2),
                "Annual_Risk": round(float(annual_risk), 2),
                "Sharpe": round(float(sharpe_ratio), 2),
            }
        )

    return pd.DataFrame(records)


def calculate_correlation(returns_df: pd.DataFrame) -> pd.DataFrame:
    """Return the Pearson correlation matrix for stock returns."""
    return returns_df.corr()

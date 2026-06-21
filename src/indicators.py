"""
indicators.py
--------------
Technical indicator calculations used in the Technical Analysis tab.

Implemented indicators:
    - SMA   (Simple Moving Average)
    - EMA   (Exponential Moving Average)
    - Bollinger Bands
    - RSI   (Relative Strength Index)
    - MACD  (Moving Average Convergence Divergence)
    - Drawdown (peak-to-trough decline)

All functions take/return pandas Series or DataFrames and avoid mutating
the caller's original DataFrame unless explicitly returning a copy with
new columns added.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def simple_moving_average(series: pd.Series, window: int) -> pd.Series:
    """SMA = rolling mean of the price over `window` periods."""
    return series.rolling(window=window, min_periods=1).mean()


def exponential_moving_average(series: pd.Series, window: int) -> pd.Series:
    """EMA = exponentially weighted moving average, more weight on recent prices."""
    return series.ewm(span=window, adjust=False).mean()


def add_moving_averages(df: pd.DataFrame, short_window: int = 20, long_window: int = 50) -> pd.DataFrame:
    """
    Add SMA & EMA columns for both a short and long window onto the Close price.
    Column names are dynamic so the sidebar sliders are reflected directly in the UI.
    """
    df = df.copy()
    df[f"SMA_{short_window}"] = simple_moving_average(df["Close"], short_window)
    df[f"SMA_{long_window}"] = simple_moving_average(df["Close"], long_window)
    df[f"EMA_{short_window}"] = exponential_moving_average(df["Close"], short_window)
    df[f"EMA_{long_window}"] = exponential_moving_average(df["Close"], long_window)
    return df


def bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    """
    Add Bollinger Bands: a moving average band plus/minus `num_std` standard deviations.
    Adds columns: BB_Mid, BB_Upper, BB_Lower
    """
    df = df.copy()
    mid = df["Close"].rolling(window=window, min_periods=1).mean()
    std = df["Close"].rolling(window=window, min_periods=1).std()
    df["BB_Mid"] = mid
    df["BB_Upper"] = mid + num_std * std
    df["BB_Lower"] = mid - num_std * std
    return df


def relative_strength_index(series: pd.Series, window: int = 14) -> pd.Series:
    """
    Classic RSI calculation using Wilder's smoothing (exponential moving average
    of gains/losses). Returns a Series of RSI values between 0 and 100.
    """
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    # Where avg_loss is 0 (no losses at all), RSI should be 100
    rsi = rsi.fillna(100)
    return rsi


def add_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Add an 'RSI' column to the DataFrame."""
    df = df.copy()
    df["RSI"] = relative_strength_index(df["Close"], window=window)
    return df


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    MACD = EMA(fast) - EMA(slow)
    Signal line = EMA(signal) of MACD
    Histogram = MACD - Signal line

    Returns a DataFrame with columns: MACD, Signal, Histogram
    """
    ema_fast = exponential_moving_average(series, fast)
    ema_slow = exponential_moving_average(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = exponential_moving_average(macd_line, signal)
    histogram = macd_line - signal_line

    return pd.DataFrame(
        {
            "MACD": macd_line,
            "Signal": signal_line,
            "Histogram": histogram,
        }
    )


def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Add MACD, Signal and Histogram columns to the DataFrame."""
    df = df.copy()
    macd_df = macd(df["Close"], fast=fast, slow=slow, signal=signal)
    df["MACD"] = macd_df["MACD"]
    df["Signal"] = macd_df["Signal"]
    df["Histogram"] = macd_df["Histogram"]
    return df


def calculate_drawdown(series: pd.Series) -> pd.Series:
    """
    Drawdown = % decline from the running maximum (peak) of the price series.
    A value of -15 means the price is currently 15% below its highest point so far.
    """
    running_max = series.cummax()
    drawdown = (series - running_max) / running_max * 100
    return drawdown


def add_drawdown(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 'Drawdown' column (%) to the DataFrame."""
    df = df.copy()
    df["Drawdown"] = calculate_drawdown(df["Close"])
    return df


def add_all_indicators(
    df: pd.DataFrame,
    short_window: int = 20,
    long_window: int = 50,
    rsi_window: int = 14,
) -> pd.DataFrame:
    """
    Convenience function: applies every indicator in one call.
    Used by app.py to keep the Technical Analysis tab code short and readable.
    """
    df = add_moving_averages(df, short_window=short_window, long_window=long_window)
    df = bollinger_bands(df, window=short_window)
    df = add_rsi(df, window=rsi_window)
    df = add_macd(df)
    df = add_drawdown(df)
    return df

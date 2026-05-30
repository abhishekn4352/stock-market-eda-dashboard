"""Plotly charts used by the stock dashboard."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


ACCENT = "#00d4ff"
GREEN = "#00e676"
RED = "#ff1744"
YELLOW = "#ffd600"
PURPLE = "#7c3aed"
PALETTE = [ACCENT, PURPLE, GREEN, YELLOW, "#ff6b35", "#e91e8c"]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#111827",
    plot_bgcolor="#0a0e1a",
    font=dict(color="#e2e8f0", family="IBM Plex Mono"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1),
    margin=dict(l=40, r=20, t=50, b=40),
    hovermode="x unified",
)


def _apply_layout(fig: go.Figure, title: str, height: int, x_title: str | None = None, y_title: str | None = None) -> go.Figure:
    """Apply the shared dashboard theme to a Plotly figure."""
    fig.update_layout(**PLOTLY_LAYOUT, title=title, height=height)
    if x_title is not None:
        fig.update_xaxes(title_text=x_title)
    if y_title is not None:
        fig.update_yaxes(title_text=y_title)
    return fig


def chart_closing_price(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Simple closing price line chart."""
    fig = go.Figure(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            name="Close",
            line=dict(color=ACCENT, width=2),
        )
    )
    return _apply_layout(fig, f"{ticker} — Closing Price", 380, y_title="Price")


def chart_moving_averages(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Closing price with MA20, MA50, and MA100 overlays."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close", line=dict(color="rgba(255,255,255,0.35)", width=1)))

    for ma, color in [("MA20", ACCENT), ("MA50", YELLOW), ("MA100", PURPLE)]:
        if ma in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[ma], name=ma, line=dict(color=color, width=2)))

    if "MA20" in df.columns and "MA50" in df.columns:
        bullish_zone = df["MA20"] > df["MA50"]
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Close"].where(bullish_zone),
                fill="tozeroy",
                fillcolor="rgba(0,230,118,0.06)",
                line=dict(width=0),
                name="Bullish Zone",
                showlegend=True,
            )
        )

    return _apply_layout(fig, f"{ticker} — Moving Averages", 460)


def chart_candlestick(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Candlestick chart with moving averages and a volume subplot."""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            increasing_line_color=GREEN,
            decreasing_line_color=RED,
            name="OHLC",
        ),
        row=1,
        col=1,
    )

    for ma, color in [("MA20", ACCENT), ("MA50", YELLOW), ("MA100", PURPLE)]:
        if ma in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df[ma], name=ma, line=dict(color=color, width=1.5, dash="dot"), opacity=0.85),
                row=1,
                col=1,
            )

    if "BB_Upper" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_Upper"],
                name="BB Upper",
                line=dict(color="rgba(124,58,237,0.5)", width=1),
                showlegend=False,
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_Lower"],
                name="BB Lower",
                line=dict(color="rgba(124,58,237,0.5)", width=1),
                fill="tonexty",
                fillcolor="rgba(124,58,237,0.05)",
                showlegend=False,
            ),
            row=1,
            col=1,
        )

    colors = [GREEN if change >= 0 else RED for change in df["Close"].pct_change().fillna(0)]
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume", marker_color=colors, opacity=0.6), row=2, col=1)

    fig.update_layout(**PLOTLY_LAYOUT, title=f"{ticker} — Candlestick & Volume", height=600, showlegend=True)
    fig.update_xaxes(rangeslider_visible=False)
    return fig


def chart_volume(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Trading volume with a 20-day moving average overlay."""
    colors = [GREEN if change >= 0 else RED for change in df["Close"].pct_change().fillna(0)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], marker_color=colors, name="Volume", opacity=0.7))
    fig.add_trace(go.Scatter(x=df.index, y=df["Volume"].rolling(20).mean(), line=dict(color=YELLOW, width=2), name="Vol MA20"))
    return _apply_layout(fig, f"{ticker} — Trading Volume", 380)


def chart_daily_returns_bar(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Bar chart showing daily percentage returns."""
    returns = df["Daily_Return"].dropna()
    colors = [GREEN if value >= 0 else RED for value in returns]
    fig = go.Figure(go.Bar(x=returns.index, y=returns.values, marker_color=colors, name="Daily Return"))
    return _apply_layout(fig, f"{ticker} — Daily Returns (%)", 380, y_title="Return (%)")


def chart_daily_returns_histogram(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Histogram of daily returns with a normal curve overlay."""
    returns = df["Daily_Return"].dropna()
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=returns, nbinsx=60, marker_color=ACCENT, opacity=0.75, name="Return Distribution"))

    if len(returns) > 1:
        mu = returns.mean()
        sigma = returns.std()
        if sigma and not np.isnan(sigma):
            x_range = np.linspace(returns.min(), returns.max(), 300)
            normal_y = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_range - mu) / sigma) ** 2)
            normal_y_scaled = normal_y * len(returns) * (returns.max() - returns.min()) / 60
            fig.add_trace(go.Scatter(x=x_range, y=normal_y_scaled, line=dict(color=YELLOW, width=2.5), name="Normal Fit"))

    return _apply_layout(fig, f"{ticker} — Return Distribution", 380)


def chart_volatility(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Rolling annualised volatility chart."""
    volatility = df["Volatility"].dropna()
    fig = go.Figure(
        go.Scatter(
            x=volatility.index,
            y=volatility,
            fill="tozeroy",
            fillcolor="rgba(255,23,68,0.12)",
            line=dict(color=RED, width=2),
            name="Volatility",
        )
    )
    return _apply_layout(fig, f"{ticker} — Annualised Volatility (21-Day Rolling)", 380, y_title="Annualised Volatility (%)")


def chart_rsi(df: pd.DataFrame, ticker: str) -> go.Figure:
    """RSI chart with overbought and oversold guide bands."""
    rsi = df["RSI"].dropna()
    fig = go.Figure()
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,23,68,0.08)", line_width=0)
    fig.add_hrect(y0=0, y1=30, fillcolor="rgba(0,230,118,0.08)", line_width=0)
    fig.add_hline(y=70, line_dash="dash", line_color=RED, opacity=0.5)
    fig.add_hline(y=30, line_dash="dash", line_color=GREEN, opacity=0.5)
    fig.add_trace(go.Scatter(x=rsi.index, y=rsi, line=dict(color=PURPLE, width=2), name="RSI(14)"))
    return _apply_layout(fig, f"{ticker} — RSI (14-Period)", 320, y_title="RSI")


def chart_correlation_heatmap(returns_df: pd.DataFrame) -> go.Figure:
    """Correlation heatmap for multi-stock return series."""
    corr = returns_df.corr()
    fig = go.Figure(
        go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale="RdBu",
            zmid=0,
            text=np.round(corr.values, 2),
            texttemplate="%{text}",
            colorbar=dict(title="Correlation"),
            hovertemplate="x: %{x}<br>y: %{y}<br>corr: %{z:.3f}<extra></extra>",
        )
    )
    return _apply_layout(fig, "Stock Return Correlation Heatmap", 460)


def chart_risk_return_scatter(stats_df: pd.DataFrame) -> go.Figure:
    """Scatter plot comparing annual risk against cumulative return."""
    fig = go.Figure(
        go.Scatter(
            x=stats_df["Annual_Risk"],
            y=stats_df["Total_Return"],
            mode="markers+text",
            text=stats_df["Ticker"],
            textposition="top center",
            marker=dict(
                color=stats_df["Sharpe"],
                colorscale="Viridis",
                size=14,
                showscale=True,
                colorbar=dict(title="Sharpe"),
            ),
            hovertemplate="<b>%{text}</b><br>Risk: %{x:.1f}%<br>Return: %{y:.1f}%<extra></extra>",
        )
    )
    return _apply_layout(fig, "Risk vs Return (colour = Sharpe Ratio)", 420, x_title="Annual Risk (%)", y_title="Total Return (%)")


def chart_normalised_comparison(dfs: dict[str, pd.DataFrame]) -> go.Figure:
    """Normalised base-100 price comparison across multiple stocks."""
    fig = go.Figure()
    for index, (ticker, df) in enumerate(dfs.items()):
        normalised = df["Close"] / df["Close"].iloc[0] * 100
        fig.add_trace(go.Scatter(x=df.index, y=normalised, name=ticker, line=dict(color=PALETTE[index % len(PALETTE)], width=2)))

    fig.add_hline(y=100, line_dash="dot", line_color="rgba(255,255,255,0.2)")
    return _apply_layout(fig, "Normalised Price Comparison (Base = 100)", 420, y_title="Indexed Price")

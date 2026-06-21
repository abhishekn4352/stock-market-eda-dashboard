"""
charts.py
----------
All Plotly chart builders for the dashboard. Every chart:
    - Uses the 'plotly_dark' template for visual consistency
    - Has a clear title, axis labels, hover tooltips and legend
    - Returns a `go.Figure` object that app.py renders with st.plotly_chart

Keeping all chart construction here keeps app.py focused on layout/flow only.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

DARK_TEMPLATE = "plotly_dark"
ACCENT_COLOR = "#00d4ff"
SECONDARY_COLOR = "#ff6b6b"
PAPER_BG = "rgba(0,0,0,0)"
PLOT_BG = "rgba(0,0,0,0)"


def _apply_dark_layout(fig: go.Figure, title: str, height: int = 420) -> go.Figure:
    """Apply consistent dark styling to any figure."""
    fig.update_layout(
        template=DARK_TEMPLATE,
        title=dict(text=title, x=0.02, font=dict(size=18)),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        height=height,
        margin=dict(l=40, r=20, t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    return fig


def candlestick_chart(df: pd.DataFrame, ma_columns: list[str] | None = None, ticker: str = "") -> go.Figure:
    """Candlestick OHLC chart with optional moving-average overlay lines."""
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=df["Date"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price",
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
        )
    )

    if ma_columns:
        colors = ["#ffd166", "#00d4ff", "#ff6b6b", "#c77dff"]
        for i, col in enumerate(ma_columns):
            if col in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df["Date"],
                        y=df[col],
                        mode="lines",
                        name=col,
                        line=dict(width=1.5, color=colors[i % len(colors)]),
                    )
                )

    fig.update_xaxes(title_text="Date", rangeslider_visible=False)
    fig.update_yaxes(title_text="Price")
    return _apply_dark_layout(fig, f"Candlestick Chart {('- ' + ticker) if ticker else ''}", height=480)


def volume_chart(df: pd.DataFrame, ticker: str = "") -> go.Figure:
    """Bar chart of trading volume, colored by up/down day."""
    colors = [
        "#26a69a" if c >= o else "#ef5350"
        for c, o in zip(df["Close"], df["Open"])
    ]
    fig = go.Figure(
        go.Bar(x=df["Date"], y=df["Volume"], marker_color=colors, name="Volume")
    )
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Volume")
    return _apply_dark_layout(fig, f"Trading Volume {('- ' + ticker) if ticker else ''}", height=300)


def line_chart(df: pd.DataFrame, y_col: str, title: str, y_label: str, color: str = ACCENT_COLOR) -> go.Figure:
    """Generic line chart used for closing price trend, cumulative returns, drawdown, etc."""
    fig = go.Figure(
        go.Scatter(x=df["Date"], y=df[y_col], mode="lines", name=y_label, line=dict(color=color, width=2))
    )
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text=y_label)
    return _apply_dark_layout(fig, title)


def daily_returns_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of daily returns (%), colored green/red for up/down days."""
    colors = ["#26a69a" if v >= 0 else "#ef5350" for v in df["Daily Return"].fillna(0)]
    fig = go.Figure(go.Bar(x=df["Date"], y=df["Daily Return"], marker_color=colors, name="Daily Return %"))
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Daily Return (%)")
    return _apply_dark_layout(fig, "Daily Returns (%)", height=320)


def bollinger_chart(df: pd.DataFrame, ticker: str = "") -> go.Figure:
    """Close price with Bollinger upper/mid/lower bands and a shaded band area."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Upper"], line=dict(color="rgba(0,212,255,0.4)", width=1), name="Upper Band"))
    fig.add_trace(
        go.Scatter(
            x=df["Date"], y=df["BB_Lower"],
            line=dict(color="rgba(0,212,255,0.4)", width=1),
            name="Lower Band", fill="tonexty", fillcolor="rgba(0,212,255,0.08)",
        )
    )
    fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Mid"], line=dict(color="#ffd166", width=1, dash="dash"), name="Middle (SMA)"))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], line=dict(color="#ffffff", width=2), name="Close"))

    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Price")
    return _apply_dark_layout(fig, f"Bollinger Bands {('- ' + ticker) if ticker else ''}", height=420)


def rsi_chart(df: pd.DataFrame) -> go.Figure:
    """RSI line chart with shaded 30/70 overbought-oversold reference lines."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], line=dict(color=ACCENT_COLOR, width=2), name="RSI"))
    fig.add_hline(y=70, line_dash="dash", line_color="#ef5350", annotation_text="Overbought (70)", annotation_position="top right")
    fig.add_hline(y=30, line_dash="dash", line_color="#26a69a", annotation_text="Oversold (30)", annotation_position="bottom right")
    fig.update_yaxes(title_text="RSI", range=[0, 100])
    fig.update_xaxes(title_text="Date")
    return _apply_dark_layout(fig, "Relative Strength Index (RSI)", height=320)


def macd_chart(df: pd.DataFrame) -> go.Figure:
    """MACD line, Signal line and Histogram bars."""
    fig = go.Figure()
    hist_colors = ["#26a69a" if v >= 0 else "#ef5350" for v in df["Histogram"].fillna(0)]
    fig.add_trace(go.Bar(x=df["Date"], y=df["Histogram"], name="Histogram", marker_color=hist_colors, opacity=0.6))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MACD"], line=dict(color=ACCENT_COLOR, width=2), name="MACD"))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Signal"], line=dict(color="#ffd166", width=2), name="Signal"))
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="MACD")
    return _apply_dark_layout(fig, "MACD Indicator", height=350)


def drawdown_chart(df: pd.DataFrame) -> go.Figure:
    """Filled area chart showing % drawdown from the running peak price."""
    fig = go.Figure(
        go.Scatter(
            x=df["Date"], y=df["Drawdown"], mode="lines", name="Drawdown %",
            line=dict(color=SECONDARY_COLOR, width=2), fill="tozeroy", fillcolor="rgba(255,107,107,0.15)",
        )
    )
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Drawdown (%)")
    return _apply_dark_layout(fig, "Drawdown from Peak (%)", height=320)


def distribution_chart(series: pd.Series, title: str, x_label: str) -> go.Figure:
    """Histogram used in the EDA tab for price / returns distributions."""
    fig = px.histogram(series.dropna(), nbins=50, template=DARK_TEMPLATE, color_discrete_sequence=[ACCENT_COLOR])
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(title_text="Frequency")
    return _apply_dark_layout(fig, title, height=350)


def normalized_comparison_chart(normalized_df: pd.DataFrame) -> go.Figure:
    """
    Line chart comparing several normalized stock price series (base = 100).
    normalized_df must have a 'Date' column plus one column per ticker.
    """
    fig = go.Figure()
    palette = px.colors.qualitative.Set2
    tickers = [c for c in normalized_df.columns if c != "Date"]
    for i, ticker in enumerate(tickers):
        fig.add_trace(
            go.Scatter(
                x=normalized_df["Date"], y=normalized_df[ticker], mode="lines",
                name=ticker, line=dict(width=2, color=palette[i % len(palette)]),
            )
        )
    fig.add_hline(y=100, line_dash="dot", line_color="gray")
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Normalized Price (Base = 100)")
    return _apply_dark_layout(fig, "Normalized Price Comparison", height=450)


def correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    """Heatmap of the correlation matrix between multiple stocks' returns."""
    fig = px.imshow(
        corr_df,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        template=DARK_TEMPLATE,
        aspect="auto",
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Corr"))
    return _apply_dark_layout(fig, "Correlation Heatmap (Daily Returns)", height=420)


def risk_return_scatter(summary_df: pd.DataFrame) -> go.Figure:
    """
    Scatter plot of annualized volatility (x) vs annualized/total return (y),
    one point per ticker, sized/colored for clarity.
    summary_df expects columns: Ticker, Volatility (%), Return (%)
    """
    fig = px.scatter(
        summary_df,
        x="Volatility (%)",
        y="Return (%)",
        text="Ticker",
        color="Ticker",
        template=DARK_TEMPLATE,
        size=[20] * len(summary_df),
        size_max=18,
    )
    fig.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="white")))
    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    fig.update_xaxes(title_text="Annualized Volatility (%)")
    fig.update_yaxes(title_text="Total Return (%)")
    return _apply_dark_layout(fig, "Risk vs Return", height=450)

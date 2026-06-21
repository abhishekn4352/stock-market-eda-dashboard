"""
app.py
------
Stock Market EDA & Trend Analysis Dashboard
=============================================

Main Streamlit entry point. Run with:
    streamlit run app.py

This file focuses on LAYOUT and FLOW only. All calculations and chart
construction live in the `src/` package so this file stays short and
easy to read for interviews / resume walkthroughs.
"""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from src import charts, comparison, indicators, kpi, preprocessing
from src.data_loader import fetch_multiple_close_prices, fetch_stock_data
from src.utils import (
    SAMPLE_TICKERS_INDIA,
    SAMPLE_TICKERS_US,
    clean_ticker_list,
    dataframe_to_csv_bytes,
    detect_currency_symbol,
    format_currency,
    format_percent,
)

# --------------------------------------------------------------------------------------
# PAGE CONFIG (must be the first Streamlit call)
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Stock Market EDA & Trend Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------------------------------------
# LOAD CUSTOM CSS (no hardcoded absolute path -> works on Windows/Mac/Linux)
# --------------------------------------------------------------------------------------
def load_css(file_name: str) -> None:
    css_path = os.path.join(os.path.dirname(__file__), "assets", file_name)
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css("style.css")


# --------------------------------------------------------------------------------------
# HEADER
# --------------------------------------------------------------------------------------
st.markdown('<div class="app-title">📈 Stock Market EDA & Trend Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Live exploratory data analysis & technical trend analysis '
    'powered by Yahoo Finance, Pandas, and Plotly.</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------------------
# SIDEBAR CONTROLS
# --------------------------------------------------------------------------------------
st.sidebar.header("⚙️ Controls")

ticker_input = st.sidebar.text_input(
    "Stock Ticker",
    value="RELIANCE.NS",
    help="e.g. AAPL (US) or RELIANCE.NS (NSE India)",
)

col_a, col_b = st.sidebar.columns(2)
start_date = col_a.date_input("Start Date", value=pd.Timestamp.today() - pd.Timedelta(days=365))
end_date = col_b.date_input("End Date", value=pd.Timestamp.today())

interval = st.sidebar.selectbox("Interval", options=["1d", "1wk", "1mo"], index=0)

st.sidebar.markdown("**Moving Average Windows**")
ma_col1, ma_col2 = st.sidebar.columns(2)
short_ma_window = ma_col1.number_input("Short MA", min_value=2, max_value=200, value=20, step=1)
long_ma_window = ma_col2.number_input("Long MA", min_value=2, max_value=400, value=50, step=1)

st.sidebar.markdown("---")
compare_mode = st.sidebar.checkbox("📊 Compare Multiple Stocks", value=False)
compare_tickers_raw = ""
if compare_mode:
    compare_tickers_raw = st.sidebar.text_area(
        "Comma-separated tickers",
        value="AAPL, MSFT, TSLA",
        help="e.g. AAPL, MSFT, TSLA  or  RELIANCE.NS, TCS.NS, INFY.NS",
    )

st.sidebar.markdown("---")
fetch_clicked = st.sidebar.button("🚀 Fetch Data", use_container_width=True, type="primary")

with st.sidebar.expander("💡 Sample Tickers"):
    st.markdown("**🇮🇳 Indian (NSE):** " + ", ".join(SAMPLE_TICKERS_INDIA))
    st.markdown("**🇺🇸 US:** " + ", ".join(SAMPLE_TICKERS_US))


# --------------------------------------------------------------------------------------
# SESSION STATE — remember the last successfully fetched data across reruns/tab switches
# --------------------------------------------------------------------------------------
if "single_df" not in st.session_state:
    st.session_state.single_df = None
if "single_ticker" not in st.session_state:
    st.session_state.single_ticker = None
if "compare_df" not in st.session_state:
    st.session_state.compare_df = None
if "failed_compare_tickers" not in st.session_state:
    st.session_state.failed_compare_tickers = []

if fetch_clicked:
    if start_date >= end_date:
        st.sidebar.error("Start date must be before end date.")
    else:
        with st.spinner(f"Fetching data for {ticker_input}..."):
            df, error = fetch_stock_data(
                ticker_input, str(start_date), str(end_date), interval
            )
        if error:
            st.session_state.single_df = None
            st.sidebar.error(error)
        else:
            st.session_state.single_df = df
            st.session_state.single_ticker = ticker_input.strip().upper()
            st.sidebar.success(f"Loaded {len(df)} rows for {ticker_input.upper()}")

        if compare_mode:
            tickers_list = clean_ticker_list(compare_tickers_raw)
            if len(tickers_list) < 2:
                st.sidebar.warning("Enter at least 2 tickers (comma-separated) to compare.")
            else:
                with st.spinner("Fetching comparison data..."):
                    cdf, failed = fetch_multiple_close_prices(
                        tuple(tickers_list), str(start_date), str(end_date), interval
                    )
                st.session_state.compare_df = cdf if not cdf.empty else None
                st.session_state.failed_compare_tickers = failed
                if failed:
                    st.sidebar.warning(f"Could not fetch: {', '.join(failed)}")


# --------------------------------------------------------------------------------------
# MAIN TABS
# --------------------------------------------------------------------------------------
tab_overview, tab_technical, tab_eda, tab_compare, tab_risk, tab_about = st.tabs(
    ["🏠 Overview", "📐 Technical Analysis", "🔍 EDA", "⚖️ Compare Stocks", "🎯 Risk & Returns", "ℹ️ About Project"]
)

single_df = st.session_state.single_df
single_ticker = st.session_state.single_ticker or ticker_input.strip().upper()
currency_symbol = detect_currency_symbol(single_ticker)

# Pre-compute the enriched (preprocessed + indicators) DataFrame once, reused by several tabs
enriched_df = None
if single_df is not None and not single_df.empty:
    enriched_df = preprocessing.preprocess_stock_data(single_df, volatility_window=int(short_ma_window))
    enriched_df = indicators.add_all_indicators(
        enriched_df, short_window=int(short_ma_window), long_window=int(long_ma_window)
    )


# ========================================================================================
# TAB 1: OVERVIEW
# ========================================================================================
with tab_overview:
    if single_df is None:
        st.info("👈 Enter a ticker in the sidebar and click **Fetch Data** to begin.")
    else:
        kpis = kpi.compute_kpis(enriched_df)

        st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)
        kpi_cols = st.columns(4)

        def kpi_card(col, label, value, css_class=""):
            col.markdown(
                f"""<div class="kpi-card">
                        <div class="kpi-label">{label}</div>
                        <div class="kpi-value {css_class}">{value}</div>
                    </div>""",
                unsafe_allow_html=True,
            )

        kpi_card(kpi_cols[0], "Latest Close", format_currency(kpis.get("latest_close"), currency_symbol))
        ret_class = "kpi-positive" if kpis.get("total_return_pct", 0) >= 0 else "kpi-negative"
        kpi_card(kpi_cols[1], "Total Return", format_percent(kpis.get("total_return_pct")), ret_class)
        kpi_card(kpi_cols[2], "Avg Daily Return", format_percent(kpis.get("avg_daily_return_pct")))
        kpi_card(kpi_cols[3], "Annualized Volatility", format_percent(kpis.get("annualized_volatility_pct")))

        kpi_cols2 = st.columns(4)
        kpi_card(kpi_cols2[0], "Highest Price", format_currency(kpis.get("highest_price"), currency_symbol))
        kpi_card(kpi_cols2[1], "Lowest Price", format_currency(kpis.get("lowest_price"), currency_symbol))
        kpi_card(kpi_cols2[2], "Risk Level", kpis.get("risk_level", "N/A"), "kpi-neutral")
        kpi_card(kpi_cols2[3], "RSI Signal", f"{kpis.get('rsi_signal','N/A')} ({kpis.get('latest_rsi', float('nan')):.1f})")

        st.markdown('<div class="section-header">Candlestick Chart</div>', unsafe_allow_html=True)
        ma_cols = [c for c in [f"SMA_{short_ma_window}", f"SMA_{long_ma_window}"] if c in enriched_df.columns]
        st.plotly_chart(charts.candlestick_chart(enriched_df, ma_columns=ma_cols, ticker=single_ticker), use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-header">Closing Price Trend</div>', unsafe_allow_html=True)
            st.plotly_chart(charts.line_chart(enriched_df, "Close", "Closing Price Trend", "Close Price"), use_container_width=True)
        with c2:
            st.markdown('<div class="section-header">Trading Volume</div>', unsafe_allow_html=True)
            st.plotly_chart(charts.volume_chart(enriched_df, ticker=single_ticker), use_container_width=True)

        st.markdown('<div class="section-header">Export Data</div>', unsafe_allow_html=True)
        st.download_button(
            "⬇️ Download Cleaned Stock Data (CSV)",
            data=dataframe_to_csv_bytes(enriched_df),
            file_name=f"{single_ticker}_cleaned_data.csv",
            mime="text/csv",
        )


# ========================================================================================
# TAB 2: TECHNICAL ANALYSIS
# ========================================================================================
with tab_technical:
    if single_df is None:
        st.info("👈 Fetch data from the sidebar first to see technical indicators.")
    else:
        st.markdown('<div class="section-header">Moving Averages</div>', unsafe_allow_html=True)
        ma_cols = [c for c in [f"SMA_{short_ma_window}", f"SMA_{long_ma_window}", f"EMA_{short_ma_window}", f"EMA_{long_ma_window}"] if c in enriched_df.columns]
        st.plotly_chart(charts.candlestick_chart(enriched_df, ma_columns=ma_cols, ticker=single_ticker), use_container_width=True)

        st.markdown('<div class="section-header">Bollinger Bands</div>', unsafe_allow_html=True)
        st.plotly_chart(charts.bollinger_chart(enriched_df, ticker=single_ticker), use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-header">RSI</div>', unsafe_allow_html=True)
            st.plotly_chart(charts.rsi_chart(enriched_df), use_container_width=True)
        with col2:
            st.markdown('<div class="section-header">MACD</div>', unsafe_allow_html=True)
            st.plotly_chart(charts.macd_chart(enriched_df), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            vol_col = f"Volatility ({int(short_ma_window)}d)"
            st.markdown('<div class="section-header">Rolling Volatility</div>', unsafe_allow_html=True)
            st.plotly_chart(charts.line_chart(enriched_df, vol_col, "Rolling Volatility (Annualized %)", "Volatility (%)", color="#ffd166"), use_container_width=True)
        with col4:
            st.markdown('<div class="section-header">Drawdown</div>', unsafe_allow_html=True)
            st.plotly_chart(charts.drawdown_chart(enriched_df), use_container_width=True)

        st.download_button(
            "⬇️ Download Technical Indicator Data (CSV)",
            data=dataframe_to_csv_bytes(enriched_df),
            file_name=f"{single_ticker}_indicators.csv",
            mime="text/csv",
        )


# ========================================================================================
# TAB 3: EDA
# ========================================================================================
with tab_eda:
    if single_df is None:
        st.info("👈 Fetch data from the sidebar first to explore the dataset.")
    else:
        df = enriched_df

        st.markdown('<div class="section-header">Dataset Preview</div>', unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")

        st.markdown('<div class="section-header">Missing Values Summary</div>', unsafe_allow_html=True)
        st.dataframe(preprocessing.get_missing_value_summary(single_df), use_container_width=True)

        st.markdown('<div class="section-header">Descriptive Statistics</div>', unsafe_allow_html=True)
        st.dataframe(df[["Open", "High", "Low", "Close", "Volume"]].describe(), use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-header">Price Distribution</div>', unsafe_allow_html=True)
            st.plotly_chart(charts.distribution_chart(df["Close"], "Close Price Distribution", "Close Price"), use_container_width=True)
        with col2:
            st.markdown('<div class="section-header">Returns Distribution</div>', unsafe_allow_html=True)
            st.plotly_chart(charts.distribution_chart(df["Daily Return"], "Daily Returns Distribution", "Daily Return (%)"), use_container_width=True)

        st.markdown('<div class="section-header">Monthly Average Return</div>', unsafe_allow_html=True)
        monthly = df.copy()
        monthly["Month"] = monthly["Date"].dt.to_period("M").astype(str)
        monthly_avg = monthly.groupby("Month")["Daily Return"].mean().reset_index()
        monthly_avg.columns = ["Month", "Avg Daily Return (%)"]
        st.dataframe(monthly_avg, use_container_width=True)

        st.markdown('<div class="section-header">Best & Worst Trading Days</div>', unsafe_allow_html=True)
        col3, col4, col5 = st.columns(3)
        best_day = df.loc[df["Daily Return"].idxmax()]
        worst_day = df.loc[df["Daily Return"].idxmin()]
        highest_vol_day = df.loc[df["Volume"].idxmax()]

        col3.metric("📈 Best Day", best_day["Date"].strftime("%Y-%m-%d"), f"{best_day['Daily Return']:.2f}%")
        col4.metric("📉 Worst Day", worst_day["Date"].strftime("%Y-%m-%d"), f"{worst_day['Daily Return']:.2f}%")
        col5.metric("🔊 Highest Volume Day", highest_vol_day["Date"].strftime("%Y-%m-%d"), f"{int(highest_vol_day['Volume']):,}")


# ========================================================================================
# TAB 4: COMPARE STOCKS
# ========================================================================================
with tab_compare:
    compare_df = st.session_state.compare_df
    if not compare_mode:
        st.info("👈 Tick **Compare Multiple Stocks** in the sidebar, enter tickers, then click **Fetch Data**.")
    elif compare_df is None:
        st.info("👈 Click **Fetch Data** in the sidebar to load the comparison.")
    else:
        st.markdown('<div class="section-header">Normalized Price Comparison (Base = 100)</div>', unsafe_allow_html=True)
        normalized = comparison.normalize_prices(compare_df)
        st.plotly_chart(charts.normalized_comparison_chart(normalized), use_container_width=True)

        st.markdown('<div class="section-header">Correlation Heatmap</div>', unsafe_allow_html=True)
        corr = comparison.compute_correlation_matrix(compare_df)
        st.plotly_chart(charts.correlation_heatmap(corr), use_container_width=True)

        st.markdown('<div class="section-header">Risk-Return Scatter Plot</div>', unsafe_allow_html=True)
        summary = comparison.build_comparison_summary(compare_df)
        st.plotly_chart(charts.risk_return_scatter(summary), use_container_width=True)

        st.markdown('<div class="section-header">Comparison Summary Table</div>', unsafe_allow_html=True)
        st.dataframe(summary, use_container_width=True)

        st.download_button(
            "⬇️ Download Comparison Summary (CSV)",
            data=dataframe_to_csv_bytes(summary),
            file_name="comparison_summary.csv",
            mime="text/csv",
        )


# ========================================================================================
# TAB 5: RISK & RETURNS
# ========================================================================================
with tab_risk:
    compare_df = st.session_state.compare_df
    if compare_df is not None:
        st.markdown('<div class="section-header">Risk vs Return (Multiple Stocks)</div>', unsafe_allow_html=True)
        summary = comparison.build_comparison_summary(compare_df)
        st.plotly_chart(charts.risk_return_scatter(summary), use_container_width=True)
        st.dataframe(summary, use_container_width=True)
        st.markdown(
            """
            **How to read this chart:** Stocks in the upper-left are ideal — higher return for
            lower risk (volatility). Stocks in the lower-right delivered poor return for high risk.
            The **Sharpe-like Ratio** is a simplified risk-adjusted return measure: higher is better.
            """
        )
    elif single_df is not None:
        st.markdown('<div class="section-header">Single Stock Risk Summary</div>', unsafe_allow_html=True)
        kpis = kpi.compute_kpis(enriched_df)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Return", format_percent(kpis.get("total_return_pct")))
        c2.metric("Annualized Volatility", format_percent(kpis.get("annualized_volatility_pct")))
        c3.metric("Risk Level", kpis.get("risk_level", "N/A"))
        st.markdown(
            f"""
            **Risk level explanation:** Based on annualized volatility of
            **{format_percent(kpis.get('annualized_volatility_pct'))}**, this stock is classified as
            **{kpis.get('risk_level', 'N/A')}**. Enable *Compare Multiple Stocks* in the sidebar to see
            a full risk-return scatter plot across several tickers.
            """
        )
    else:
        st.info("👈 Fetch data from the sidebar to view risk & return analysis.")


# ========================================================================================
# TAB 6: ABOUT PROJECT
# ========================================================================================
with tab_about:
    st.markdown('<div class="section-header">What This Project Does</div>', unsafe_allow_html=True)
    st.markdown(
        """
        This dashboard fetches **live stock market data** from Yahoo Finance and performs:
        - Exploratory Data Analysis (EDA)
        - Technical indicator calculation (SMA, EMA, RSI, MACD, Bollinger Bands)
        - Risk & return analysis (volatility, drawdown, Sharpe-like ratio)
        - Multi-stock comparison (normalized prices, correlation, risk-return scatter)
        """
    )

    st.markdown('<div class="section-header">Tech Stack</div>', unsafe_allow_html=True)
    st.markdown("- **Python 3.10+** · **Streamlit** (UI) · **Pandas / NumPy** (data) · **Plotly** (charts) · **yFinance** (data source)")

    st.markdown('<div class="section-header">Data Source</div>', unsafe_allow_html=True)
    st.markdown("All data is pulled live and free from **Yahoo Finance** via the `yfinance` Python library — no API key required.")

    st.markdown('<div class="section-header">Limitations</div>', unsafe_allow_html=True)
    st.markdown(
        """
        - Depends on Yahoo Finance availability/rate limits — occasional fetch failures are handled gracefully.
        - Intraday data is not included (only daily/weekly/monthly intervals).
        - The Sharpe-like ratio is a simplified teaching approximation, not a regulated financial metric.
        - This tool is for **educational/demonstration purposes only** and is **not financial advice**.
        """
    )

    st.markdown('<div class="section-header">Resume Bullet Points</div>', unsafe_allow_html=True)
    st.code(
        "- Built a full-stack stock market analytics dashboard (Streamlit, Pandas, Plotly, yFinance) "
        "with 10+ interactive charts and 6 technical indicators.\n"
        "- Implemented modular data pipeline (fetch -> clean -> preprocess -> indicators -> visualize) "
        "with robust error handling for invalid tickers and missing data.\n"
        "- Designed multi-stock comparison engine with normalized pricing, correlation heatmaps, "
        "and risk-return analysis (Sharpe-like ratio).",
        language="text",
    )

# --------------------------------------------------------------------------------------
# FOOTER
# --------------------------------------------------------------------------------------
st.markdown(
    '<div class="app-footer">Stock Market EDA & Trend Analysis Dashboard · Built with Streamlit, '
    'Pandas, Plotly & yFinance · Data source: Yahoo Finance · For educational purposes only, '
    'not financial advice.</div>',
    unsafe_allow_html=True,
)

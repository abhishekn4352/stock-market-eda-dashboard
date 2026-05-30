"""Streamlit entry point for the Stock Market EDA & Trend Analysis Dashboard."""

from __future__ import annotations

import warnings
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

from src.analysis import (
    calculate_risk_return_statistics,
    calculate_stock_kpis,
    calculate_statistical_summary,
    calculate_technical_indicators,
    generate_signal,
)
from src.data_loader import fetch_company_info, fetch_stock_data
from src.preprocessing import prepare_stock_data
from src.utils import dataframe_to_csv, format_currency, validate_date_range, validate_tickers
from src.visualizations import (
    chart_candlestick,
    chart_correlation_heatmap,
    chart_daily_returns_bar,
    chart_daily_returns_histogram,
    chart_moving_averages,
    chart_normalised_comparison,
    chart_risk_return_scatter,
    chart_rsi,
    chart_volatility,
    chart_volume,
)

warnings.filterwarnings("ignore")


st.set_page_config(
    page_title="StockSense | Market Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_custom_css() -> None:
    """Apply the dark theme and card styling used throughout the dashboard."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@400;600;700;800&display=swap');

        :root {
            --bg-main: #0a0e1a;
            --bg-card: #111827;
            --bg-card2: #1a2235;
            --accent: #00d4ff;
            --accent2: #7c3aed;
            --green: #00e676;
            --red: #ff1744;
            --yellow: #ffd600;
            --text-main: #e2e8f0;
            --text-muted: #64748b;
            --border: rgba(255,255,255,0.07);
        }

        html, body, .stApp {
            background-color: var(--bg-main) !important;
            color: var(--text-main) !important;
            font-family: 'Syne', sans-serif;
        }

        [data-testid="stSidebar"] {
            background: var(--bg-card) !important;
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] * {
            color: var(--text-main) !important;
        }

        .sidebar-header {
            background: linear-gradient(135deg, #0a0e1a 0%, #1a2235 100%);
            border-left: 3px solid var(--accent);
            padding: 12px 16px;
            margin-bottom: 20px;
            border-radius: 0 8px 8px 0;
        }

        .kpi-card {
            background: var(--bg-card2);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px 22px;
            text-align: center;
            transition: transform .2s, box-shadow .2s;
        }

        .kpi-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(0,212,255,.15);
        }

        .kpi-label {
            font-size: 11px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 8px;
            font-family: 'IBM Plex Mono', monospace;
        }

        .kpi-value {
            font-size: 26px;
            font-weight: 800;
            color: var(--accent);
            font-family: 'IBM Plex Mono', monospace;
            line-height: 1;
        }

        .kpi-sub {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 6px;
        }

        .kpi-pos { color: var(--green) !important; }
        .kpi-neg { color: var(--red) !important; }

        .section-title {
            font-size: 18px;
            font-weight: 700;
            color: var(--text-main);
            border-left: 3px solid var(--accent);
            padding-left: 12px;
            margin: 28px 0 16px 0;
            letter-spacing: .5px;
        }

        .signal-buy  { background:#00e676; color:#000; padding:4px 14px; border-radius:20px; font-weight:700; font-size:13px; }
        .signal-sell { background:#ff1744; color:#fff; padding:4px 14px; border-radius:20px; font-weight:700; font-size:13px; }
        .signal-hold { background:#ffd600; color:#000; padding:4px 14px; border-radius:20px; font-weight:700; font-size:13px; }

        div[data-baseweb="input"] input,
        div[data-baseweb="select"] div,
        div[data-baseweb="textarea"] textarea,
        .stDateInput input {
            background: var(--bg-card2) !important;
            color: var(--text-main) !important;
            border: 1px solid rgba(255,255,255,.12) !important;
            border-radius: 8px !important;
        }

        .stButton button {
            background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
            color: #000 !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 8px 24px !important;
            font-size: 14px !important;
            letter-spacing: .5px !important;
        }

        .stButton button:hover { opacity: .85 !important; }

        .stTabs [data-baseweb="tab-list"] {
            background: var(--bg-card) !important;
            border-radius: 10px !important;
            gap: 4px !important;
        }

        .stTabs [data-baseweb="tab"] {
            color: var(--text-muted) !important;
            border-radius: 8px !important;
            padding: 8px 18px !important;
            font-weight: 600 !important;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg,#00d4ff22,#7c3aed22) !important;
            color: var(--accent) !important;
            border-bottom: 2px solid var(--accent) !important;
        }

        .stDataFrame { background: var(--bg-card) !important; border-radius: 10px !important; }

        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg-main); }
        ::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 3px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header() -> None:
    """Render the main dashboard banner."""
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:16px; padding:8px 0 20px 0; border-bottom:1px solid rgba(255,255,255,0.07); margin-bottom:24px;">
            <span style="font-size:38px;">📈</span>
            <div>
                <div style="font-size:28px; font-weight:800; color:#e2e8f0; line-height:1;">StockSense</div>
                <div style="font-size:13px; color:#64748b; letter-spacing:2px; font-family:'IBM Plex Mono',monospace;">
                    MARKET EDA & TREND ANALYSIS DASHBOARD
                </div>
            </div>
            <div style="margin-left:auto; font-family:'IBM Plex Mono',monospace; font-size:12px; color:#64748b; text-align:right;">
                Last updated: %s
            </div>
        </div>
        """
        % datetime.now().strftime("%d %b %Y  %H:%M"),
        unsafe_allow_html=True,
    )


def render_sidebar() -> dict:
    """Render sidebar controls and return the selected dashboard options."""
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-header">
                <span style="font-size:20px; font-weight:800; color:#00d4ff;">📈 StockSense</span><br>
                <span style="font-size:11px; color:#64748b; letter-spacing:1px;">MARKET ANALYTICS</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 🔎 Stock Selection")
        raw_tickers = st.text_input(
            "Enter Ticker(s)",
            value="AAPL, TSLA",
            help="Comma-separated: AAPL, TSLA, TCS.NS, RELIANCE.NS",
        )

        st.markdown("#### 📅 Date Range")
        default_start = datetime.today() - timedelta(days=365)
        start_date = st.date_input("Start Date", value=default_start)
        end_date = st.date_input("End Date", value=datetime.today())

        st.markdown("---")
        st.markdown("#### ⚙️ Analysis Options")
        show_eda = st.checkbox("Show EDA", value=True)
        show_candle = st.checkbox("Candlestick Chart", value=True)
        show_ma = st.checkbox("Moving Averages", value=True)
        show_vol = st.checkbox("Volume Analysis", value=True)
        show_ret = st.checkbox("Returns Analysis", value=True)
        show_risk = st.checkbox("Volatility & RSI", value=True)
        show_comp = st.checkbox("Multi-Stock Comparison", value=True)

        st.markdown("---")
        fetch_btn = st.button("🚀 Analyse Stocks", use_container_width=True)

        st.markdown(
            """
            <div style='margin-top:30px; font-size:11px; color:#64748b; text-align:center;
                        font-family:"IBM Plex Mono",monospace; line-height:1.8;'>
                Data: Yahoo Finance API<br>
                Refresh: Every 5 min<br>
                Built with Streamlit
            </div>
            """,
            unsafe_allow_html=True,
        )

    return {
        "raw_tickers": raw_tickers,
        "start": start_date,
        "end": end_date,
        "fetch": fetch_btn,
        "show_eda": show_eda,
        "show_candle": show_candle,
        "show_ma": show_ma,
        "show_vol": show_vol,
        "show_ret": show_ret,
        "show_risk": show_risk,
        "show_comp": show_comp,
    }


def render_feature_cards() -> None:
    """Show the default landing cards before the first analysis run."""
    cols = st.columns(4)
    features = [
        ("🕯️", "Candlestick Charts", "Interactive OHLCV with Bollinger Bands"),
        ("📐", "Technical Indicators", "MA20/50/100 · RSI · Volatility"),
        ("🔗", "Correlation Analysis", "Multi-stock correlation heatmap"),
        ("⚡", "Buy / Sell Signals", "MA crossover signal engine"),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        col.markdown(
            f"""
            <div class="kpi-card" style="text-align:left;">
                <div style="font-size:28px; margin-bottom:8px;">{icon}</div>
                <div style="font-weight:700; margin-bottom:4px; color:#e2e8f0;">{title}</div>
                <div style="font-size:12px; color:#64748b;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_landing_state() -> None:
    """Render the initial screen shown before the user runs an analysis."""
    st.markdown(
        """
        <div style="text-align:center; padding:60px 20px;">
            <div style="font-size:64px; margin-bottom:16px;">📊</div>
            <div style="font-size:22px; font-weight:700; color:#e2e8f0; margin-bottom:8px;">
                Ready to Analyse Your Stocks
            </div>
            <div style="font-size:14px; color:#64748b; max-width:480px; margin:auto; line-height:1.8;">
                Enter one or more ticker symbols in the sidebar (e.g. AAPL, TSLA, RELIANCE.NS),
                choose a date range, and click <b style="color:#00d4ff;">Analyse Stocks</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_feature_cards()


def render_kpi_cards(df: pd.DataFrame, ticker: str, info: dict) -> None:
    """Render the KPI card row for the selected stock."""
    kpis = calculate_stock_kpis(df)
    currency = info.get("currency", "USD")
    total_return = kpis["total_return"]
    ret_class = "kpi-pos" if total_return >= 0 else "kpi-neg"
    sign = "▲" if total_return >= 0 else "▼"

    cards = [
        ("CURRENT PRICE", format_currency(kpis["current_price"], currency), currency, ""),
        ("PERIOD HIGH", format_currency(kpis["period_high"], currency), currency, "kpi-pos"),
        ("PERIOD LOW", format_currency(kpis["period_low"], currency), currency, "kpi-neg"),
        ("AVG VOLUME", f"{kpis['average_volume'] / 1e6:.2f}M", "shares", ""),
        ("TOTAL RETURN", f"{sign} {abs(total_return):.2f}%", "", ret_class),
    ]

    cols = st.columns(5)
    for col, (label, value, sub, cls) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value {cls}">{value}</div>
                    <div class="kpi-sub">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_eda(df: pd.DataFrame) -> None:
    """Render the EDA panels for the selected stock."""
    st.markdown('<div class="section-title">📋 Dataset Overview</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Trading Days", len(df))
    c2.metric("Columns", len(df.columns))
    c3.metric("Missing Values", int(df.isnull().sum().sum()))

    tab1, tab2, tab3 = st.tabs(["📊 Statistical Summary", "🔍 Missing Values", "🗂️ Raw Data Preview"])

    with tab1:
        summary = calculate_statistical_summary(df)
        if summary.empty:
            st.info("No numeric columns available for summary statistics.")
        else:
            st.dataframe(summary.style.background_gradient(cmap="Blues"), use_container_width=True)

    with tab2:
        missing = df.isnull().sum().reset_index()
        missing.columns = ["Column", "Missing Count"]
        missing["Missing %"] = (missing["Missing Count"] / len(df) * 100).round(2)
        st.dataframe(missing, use_container_width=True)

        if missing["Missing Count"].sum() > 0:
            fig = px.bar(
                missing,
                x="Column",
                y="Missing %",
                color="Missing %",
                color_continuous_scale="reds",
                title="Missing Data by Column",
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No missing values found in the dataset.")

    with tab3:
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            st.dataframe(
                df.tail(30).style.format({col: "{:.2f}" for col in numeric_columns}),
                use_container_width=True,
            )
        else:
            st.dataframe(df.tail(30), use_container_width=True)


def render_stock_header(ticker: str, name: str, signal: str) -> None:
    """Render the stock title strip and crossover signal."""
    sig_class = {"BUY": "signal-buy", "SELL": "signal-sell"}.get(signal, "signal-hold")
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; justify-content:space-between;
                    background:var(--bg-card); border:1px solid var(--border);
                    border-radius:12px; padding:16px 22px; margin-bottom:20px;">
            <div>
                <span style="font-size:22px; font-weight:800; color:#00d4ff;">{ticker}</span>
                <span style="font-size:13px; color:#64748b; margin-left:12px;">{name}</span>
            </div>
            <div>
                <span style="font-size:11px; color:#64748b; margin-right:8px; font-family:'IBM Plex Mono';">MA CROSSOVER SIGNAL</span>
                <span class="{sig_class}">{signal}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Run the dashboard."""
    inject_custom_css()
    render_page_header()
    cfg = render_sidebar()

    if not cfg["fetch"]:
        render_landing_state()
        return

    try:
        tickers = validate_tickers(cfg["raw_tickers"])
        validate_date_range(cfg["start"], cfg["end"])
    except ValueError as exc:
        st.warning(str(exc))
        return

    start_str = str(cfg["start"])
    end_str = str(cfg["end"])

    all_data: dict[str, pd.DataFrame] = {}
    all_returns: dict[str, pd.Series] = {}

    progress = st.progress(0, text="Fetching market data…")
    for index, ticker in enumerate(tickers):
        progress.progress((index + 1) / len(tickers), text=f"Fetching {ticker}…")
        try:
            raw_df = fetch_stock_data(ticker, start_str, end_str)
            prepared_df = prepare_stock_data(raw_df)
            enriched_df = calculate_technical_indicators(prepared_df)
        except ValueError as exc:
            st.warning(f"⚠️ {exc}")
            continue
        except RuntimeError as exc:
            st.error(str(exc))
            continue

        all_data[ticker] = enriched_df
        all_returns[ticker] = enriched_df["Daily_Return"].dropna()

    progress.empty()

    if not all_data:
        st.error("❌ No valid data retrieved. Please check the ticker symbols and try again.")
        return

    returns_df = pd.DataFrame(all_returns).dropna()

    for ticker, df in all_data.items():
        info = fetch_company_info(ticker)
        name = info.get("longName", ticker)
        signal = generate_signal(df)

        render_stock_header(ticker, name, signal)
        render_kpi_cards(df, ticker, info)
        st.markdown("")

        if cfg["show_eda"]:
            render_eda(df)

        if cfg["show_candle"]:
            st.markdown('<div class="section-title">🕯️ Candlestick Chart</div>', unsafe_allow_html=True)
            st.plotly_chart(chart_candlestick(df, ticker), use_container_width=True)

        if cfg["show_ma"]:
            st.markdown('<div class="section-title">📐 Moving Averages</div>', unsafe_allow_html=True)
            st.plotly_chart(chart_moving_averages(df, ticker), use_container_width=True)

        if cfg["show_vol"]:
            st.markdown('<div class="section-title">📊 Volume Analysis</div>', unsafe_allow_html=True)
            st.plotly_chart(chart_volume(df, ticker), use_container_width=True)

        if cfg["show_ret"]:
            st.markdown('<div class="section-title">📉 Returns Analysis</div>', unsafe_allow_html=True)
            left_col, right_col = st.columns(2)
            with left_col:
                st.plotly_chart(chart_daily_returns_bar(df, ticker), use_container_width=True)
            with right_col:
                st.plotly_chart(chart_daily_returns_histogram(df, ticker), use_container_width=True)

        if cfg["show_risk"]:
            st.markdown('<div class="section-title">⚡ Volatility & RSI</div>', unsafe_allow_html=True)
            left_col, right_col = st.columns([3, 2])
            with left_col:
                st.plotly_chart(chart_volatility(df, ticker), use_container_width=True)
            with right_col:
                st.plotly_chart(chart_rsi(df, ticker), use_container_width=True)

        st.download_button(
            label=f"⬇️ Download {ticker} CSV",
            data=dataframe_to_csv(df),
            file_name=f"{ticker}_analysis_{start_str}_{end_str}.csv",
            mime="text/csv",
        )
        st.markdown("---")

    if len(all_data) >= 2 and cfg["show_comp"]:
        st.markdown('<div class="section-title">🔗 Multi-Stock Comparison</div>', unsafe_allow_html=True)
        st.plotly_chart(chart_normalised_comparison(all_data), use_container_width=True)

        if len(returns_df.columns) >= 2:
            st.markdown('<div class="section-title">🌡️ Correlation Heatmap</div>', unsafe_allow_html=True)
            st.plotly_chart(chart_correlation_heatmap(returns_df), use_container_width=True)

        st.markdown('<div class="section-title">📌 Risk vs Return</div>', unsafe_allow_html=True)
        stats_df = calculate_risk_return_statistics(all_data)
        st.plotly_chart(chart_risk_return_scatter(stats_df), use_container_width=True)

        st.markdown('<div class="section-title">📋 Comparative Summary</div>', unsafe_allow_html=True)
        st.dataframe(
            stats_df.style
            .background_gradient(subset=["Total_Return"], cmap="RdYlGn")
            .background_gradient(subset=["Annual_Risk"], cmap="RdYlGn_r")
            .background_gradient(subset=["Sharpe"], cmap="Blues")
            .format({"Total_Return": "{:.2f}%", "Annual_Risk": "{:.2f}%", "Sharpe": "{:.3f}"}),
            use_container_width=True,
        )

        st.download_button(
            "⬇️ Download Combined Returns CSV",
            data=dataframe_to_csv(returns_df.reset_index(), include_index=False),
            file_name=f"combined_returns_{start_str}_{end_str}.csv",
            mime="text/csv",
        )

    st.markdown(
        """
        <div style="text-align:center; padding:40px 0 20px; color:#374151;
                    font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:1px;">
            STOCKSENSE ANALYTICS DASHBOARD  ·  DATA VIA YAHOO FINANCE  ·  BUILT WITH STREAMLIT & PLOTLY
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
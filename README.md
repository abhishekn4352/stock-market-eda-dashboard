# 📈 Stock Market EDA & Trend Analysis Dashboard

**Python · Streamlit · Pandas · Plotly · yFinance · 2026**

A professional, modular, production-quality dashboard for live stock market
exploration, exploratory data analysis (EDA), and technical trend analysis —
built entirely with free, no-API-key-required data from Yahoo Finance.

> 🎓 Built as a portfolio / resume project. Fully working, beginner-friendly,
> and ready to demo or push to GitHub.

---

## 📑 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Folder Structure](#-folder-structure)
- [Installation](#-installation)
- [How to Run](#-how-to-run)
- [Example Tickers](#-example-tickers)
- [Screenshots](#-screenshots)
- [Interview Explanation Guide](#-interview-explanation-guide)
- [Limitations](#-limitations)
- [Future Improvements](#-future-improvements)
- [Resume Description](#-resume-description)
- [Author](#-author)

---

## ✨ Features

### 🏠 Overview Tab
- KPI cards: latest close, total return %, avg daily return %, annualized volatility %, highest/lowest price, risk level, RSI signal
- Interactive candlestick chart with moving-average overlays
- Trading volume chart (color-coded by up/down day)
- Closing price trend chart
- CSV export of cleaned data

### 📐 Technical Analysis Tab
- Simple & Exponential Moving Averages (SMA/EMA) with **dynamic windows from the sidebar**
- Bollinger Bands
- RSI (Relative Strength Index) with 30/70 reference lines
- MACD (Moving Average Convergence Divergence) with histogram
- Rolling annualized volatility
- Drawdown-from-peak chart
- CSV export of indicator data

### 🔍 EDA Tab
- Dataset preview & shape
- Missing value summary
- Descriptive statistics
- Price & returns distribution histograms
- Monthly average return table
- Best/worst trading day & highest volume day

### ⚖️ Compare Stocks Tab
- Compare 2+ tickers (comma-separated) side by side
- Normalized price chart (base = 100)
- Correlation heatmap of daily returns
- Risk-return scatter plot
- Comparison summary table (return, volatility, Sharpe-like ratio)
- CSV export of comparison summary

### 🎯 Risk & Returns Tab
- Risk-vs-return scatter plot across compared stocks
- Single-stock risk summary with plain-English explanation
- Simplified Sharpe-like ratio for risk-adjusted comparison

### ℹ️ About Project Tab
- Problem statement, data source, tech stack, limitations, and ready-to-use resume bullet points

### 🎨 UI / UX
- Custom dark theme with gradient title, KPI cards, and clean spacing
- All charts use Plotly's dark template with proper titles, axis labels, hover tooltips, and legends
- Responsive wide layout, organized into 6 clean tabs
- Friendly error/warning messages — the app never crashes on bad input

### 🛡️ Robust Error Handling
- Invalid ticker → friendly warning, no crash
- Empty / no-data date range → friendly warning
- Network/API failure → caught and surfaced cleanly
- Works for both **Indian (NSE)** stocks like `RELIANCE.NS`, `TCS.NS`, `INFY.NS` and **global** stocks like `AAPL`, `MSFT`, `TSLA`

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| UI Framework | [Streamlit](https://streamlit.io/) |
| Data Source | [yFinance](https://pypi.org/project/yfinance/) (Yahoo Finance, free, no API key) |
| Data Processing | [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/) |
| Visualization | [Plotly](https://plotly.com/python/) |
| Language | Python 3.10+ |

No database, no paid APIs, no API keys required.

---

## 📁 Folder Structure

```
stock-market-eda-dashboard/
│
├── app.py                      # Main Streamlit entry point (layout & flow only)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore
├── REGRESSION_TEST_REPORT.md   # Full regression test documentation
│
├── src/                        # All business logic, modularized
│   ├── __init__.py
│   ├── data_loader.py          # Fetch & clean data from Yahoo Finance
│   ├── preprocessing.py        # Returns, volatility, derived columns
│   ├── indicators.py           # SMA, EMA, RSI, MACD, Bollinger, Drawdown
│   ├── kpi.py                  # KPI card calculations
│   ├── charts.py                # All Plotly chart builders (dark theme)
│   ├── comparison.py           # Multi-stock comparison helpers
│   └── utils.py                # Shared small helper functions
│
├── assets/
│   └── style.css               # Custom dark theme CSS
│
└── sample_data/
    └── README.md                # Notes on data (app fetches live, no local files needed)
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Windows (CMD / PowerShell)

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ▶️ How to Run

### Windows (CMD or PowerShell)

```powershell
cd stock-market-eda-dashboard
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux

```bash
cd stock-market-eda-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints in your terminal (usually `http://localhost:8501`).

**Usage:** Enter a ticker in the sidebar (or pick one from the "Sample Tickers"
expander), choose a date range and interval, then click **🚀 Fetch Data**.
Tick **📊 Compare Multiple Stocks** to unlock the Compare Stocks and Risk &
Returns tabs for multi-ticker analysis.

---

## 🧪 Example Tickers

**🇮🇳 Indian (NSE):** `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`, `SBIN.NS`

**🇺🇸 US:** `AAPL`, `MSFT`, `TSLA`, `NVDA`, `GOOGL`

For comparisons, enter a comma-separated list, e.g.:
`AAPL, MSFT, TSLA` or `RELIANCE.NS, TCS.NS, INFY.NS`

---

## 📸 Screenshots

> _Add your own screenshots here after running the app locally —
> Overview tab, Technical Analysis tab, Compare Stocks tab, etc._

| Overview | Technical Analysis | Compare Stocks |
|---|---|---|
| `screenshots/overview.png` | `screenshots/technical.png` | `screenshots/compare.png` |

---

## 🎤 Interview Explanation Guide

A short script you can use to explain this project confidently in an interview.

**Problem statement:**
Retail investors and students often want a free, visual way to explore a
stock's price history, compute standard technical indicators, and compare
multiple stocks' risk/return profile — without paying for a terminal or
writing one-off notebooks each time. This dashboard solves that with a single
reusable, interactive tool.

**What data is used:**
Live daily/weekly/monthly OHLCV (Open, High, Low, Close, Volume) data is
pulled directly from **Yahoo Finance** through the `yfinance` Python library —
completely free and requiring no API key. It supports both global tickers
(e.g. `AAPL`) and Indian NSE tickers (e.g. `RELIANCE.NS`).

**How EDA is done:**
After cleaning (removing nulls, sorting by date, standardizing column names),
the EDA tab shows dataset shape, missing-value summaries, descriptive
statistics (`.describe()`), price/returns distributions, monthly average
returns, and identifies the best/worst trading days and highest-volume day —
classic first steps in any quantitative analysis workflow.

**How technical indicators are calculated:**
- **SMA/EMA** — rolling/exponentially-weighted means of the close price.
- **Bollinger Bands** — a moving average ± a multiple of rolling standard deviation.
- **RSI** — Wilder's smoothed average gain/loss ratio, scaled to 0–100.
- **MACD** — difference between a fast and slow EMA, plus a signal line (EMA of that difference).
- **Drawdown** — % decline of the current price from its running historical peak.

**How risk-return analysis works:**
Annualized volatility is computed from the standard deviation of **log
returns**, scaled by `√252` (trading days/year). Total return is the simple
percentage change from the first to last close in the selected period. A
simplified **Sharpe-like ratio** (`(Return − Risk-Free Rate) / Volatility`) is
used to rank risk-adjusted performance across compared stocks, and is plotted
on a risk-return scatter plot (volatility on x, return on y).

**Challenges faced:**
- Newer versions of `yfinance` sometimes return `MultiIndex` columns even for
  a single ticker — handled with a dedicated `_flatten_columns()` helper.
- Gracefully handling invalid tickers / empty responses / network failures
  without ever showing a raw Python traceback to the user.
- Keeping moving-average and RSI windows **dynamic** (driven by sidebar
  inputs) while still producing clean, readable column names and chart legends.

**Future scope:**
See [Future Improvements](#-future-improvements) below.

---

## ⚠️ Limitations

- Depends on Yahoo Finance's availability and informal rate limits; occasional
  fetch failures are expected and are handled gracefully with friendly messages.
- Only daily/weekly/monthly intervals are supported (no intraday/minute data).
- The Sharpe-like ratio is a simplified teaching approximation, not a
  regulator-grade financial metric (a true Sharpe ratio uses daily excess
  returns over a risk-free rate, annualized differently).
- This project is for **educational and portfolio demonstration purposes
  only** — it is **not financial advice**.

---

## 🚀 Future Improvements

- Add intraday (1m/5m/15m) data support where available
- Add portfolio-level analysis (multi-stock weighted returns)
- Add forecasting (e.g. simple ARIMA / Prophet trend projection)
- Add news sentiment integration for selected tickers
- Add user-saved watchlists (would require a lightweight database)
- Add PDF/Excel export of the full analysis report
- Add dark/light theme toggle

---

## 💼 Resume Description

> **Stock Market EDA & Trend Analysis Dashboard** | Python, Streamlit, Pandas, Plotly, yFinance
> Built a full-stack, modular stock market analytics dashboard with live Yahoo
> Finance data, 10+ interactive Plotly charts, and 6 technical indicators
> (SMA, EMA, Bollinger Bands, RSI, MACD, Drawdown). Designed a multi-stock
> comparison engine with normalized pricing, correlation heatmaps, and a
> Sharpe-like risk-return analysis. Implemented robust error handling for
> invalid tickers, empty data, and network failures across a clean
> fetch → clean → preprocess → analyze → visualize pipeline.

---

## 👤 Author

**Your Name Here**
- GitHub: `your-github-username`
- LinkedIn: `your-linkedin-profile`
- Email: `your-email@example.com`

---

## 📄 License

This project is open for personal, educational, and portfolio use.

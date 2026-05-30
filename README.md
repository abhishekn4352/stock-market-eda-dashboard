# Stock Market EDA & Trend Analysis Dashboard

An end-to-end Streamlit dashboard for stock market exploratory data analysis, technical indicator tracking, and multi-stock trend comparison using live Yahoo Finance data.

## Overview

This project refactors a single-file Streamlit app into a modular, professional Python codebase. The dashboard keeps the original user experience intact while improving readability, reuse, and maintainability.

## Features

- Live OHLCV data fetching with Yahoo Finance.
- Invalid ticker handling and empty-data checks.
- Cleaning, date standardisation, and daily return calculation.
- Moving averages, Bollinger Bands, RSI, and volatility indicators.
- KPI cards for price, range, volume, and total return.
- Candlestick, closing price, moving average, volume, returns, heatmap, volatility, RSI, and risk-return charts.
- Multi-stock normalised comparison and correlation analysis.
- CSV downloads for individual and combined analysis outputs.

## Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- Matplotlib
- Seaborn
- yFinance

## Folder Structure

```text
stock-market-eda-dashboard/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── analysis.py
│   ├── visualizations.py
│   └── utils.py
├── assets/
│   └── screenshots/
└── notebooks/
    └── stock_market_eda.ipynb
```

## Installation

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Run

From inside the `stock-market-eda-dashboard` folder, start the app with:

```bash
streamlit run app.py
```

## Screenshots

Add exported dashboard images to `assets/screenshots/` and reference them here.

Suggested captures:

- Dashboard landing view
- Candlestick and volume section
- Moving averages and RSI section
- Multi-stock comparison and correlation heatmap

## Resume Bullet Points

- Built a modular Streamlit dashboard for live stock market EDA and trend analysis using Yahoo Finance data.
- Implemented reusable data loading, preprocessing, technical indicator, and visualisation layers for maintainable analytics workflows.
- Delivered multi-stock comparison tools, risk-return analysis, MA crossover signals, and downloadable CSV exports in a polished UI.

## Future Improvements

- Add portfolio allocation and performance tracking.
- Introduce MACD, stochastic oscillator, and backtesting modules.
- Save annotated charts and reports to PDF.
- Add deployment support for Streamlit Community Cloud.
- Extend analysis with sector-level and macroeconomic context.

# StockPulse

**StockPulse** is an Intelligent Fundamental Stock Analysis Platform that democratizes investment research by automating financial analysis, providing interactive visualizations, and offering dual-mode insights (Beginner & Advanced). 

🚀 **Live Demo:** [https://stockpulse-finance.vercel.app](https://stockpulse-finance.vercel.app)

The platform fetches real financial data from Yahoo Finance (via `yfinance`), processes it through a three-stage analysis pipeline, and presents results via a responsive web interface.

## Key Features

- **Three-Stage Analysis Pipeline:** Automatically calculates 20+ financial metrics, detects red flags, and generates a composite health score (0-100).
- **Dual-Mode Insights:**
  - *Beginner Mode:* Plain-English summaries and simple health scores.
  - *Advanced Mode:* Deep-dive metrics and historical trends.
- **Interactive Visualizations:** Radar charts for multi-stock comparisons and line charts for historical performance analysis.
- **Watchlist & Alerts:** Authenticated users can save stocks to their watchlist and configure threshold alerts.
- **Global Market Coverage:** Search and analyze both US and Indian Stock Markets (NSE) completely for free with no rate limits.
- **Robust Architecture:** Powered by a production-ready PostgreSQL database and modular Flask blueprints.

## Technology Stack

- **Backend:** Python, Flask, PyJWT, bcrypt, yfinance
- **Database:** PostgreSQL (with psycopg2)
- **Frontend:** Vanilla JavaScript, HTML5, CSS3, Chart.js

## Architecture

For an in-depth view of the system architecture, database schema, and analysis engine details, please see [ARCHITECTURE.md](ARCHITECTURE.md).

## Disclaimer

This platform is for educational and informational purposes only. Do not use this as professional financial advice.

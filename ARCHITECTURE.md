# StockPulse — Architecture Document

## Project Overview

**StockPulse** is an Intelligent Fundamental Stock Analysis Platform that democratizes investment research by automating financial analysis, providing interactive visualizations, and offering dual-mode insights (Beginner & Advanced). The platform fetches real financial data from Alpha Vantage, processes it through a three-stage analysis pipeline, and presents results via a responsive web interface.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                          │
│                                                                  │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────────┐   │
│  │ app.js   │  │analysis.js│  │charts.js │  │ watchlist.js  │   │
│  │(Router & │  │(Beginner &│  │(Chart.js │  │(CRUD for user │   │
│  │ Search)  │  │ Advanced) │  │ Renders) │  │  watchlists)  │   │
│  └────┬─────┘  └─────┬─────┘  └────┬─────┘  └──────┬────────┘   │
│       │              │             │               │             │
│  ┌────▼──────────────▼─────────────▼───────────────▼──────────┐  │
│  │                     api.js                                 │  │
│  │         (Centralized HTTP Client + JWT Injection)          │  │
│  └────────────────────────────┬────────────────────────────────┘  │
│                               │                                  │
│  ┌────────────┐               │                                  │
│  │  auth.js   │───────────────┤  REST API (JSON over HTTP)       │
│  │(Login/Reg) │               │                                  │
│  └────────────┘               │                                  │
└───────────────────────────────┼──────────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   Flask Server :5050   │
                    │      (app.py)          │
                    │   Application Factory  │
                    │   + Static File Server │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                  │
    ┌─────────▼──────┐  ┌──────▼───────┐  ┌──────▼───────────┐
    │   auth_bp      │  │  stocks_bp   │  │  watchlist_bp    │
    │ /api/auth/*    │  │/api/stocks/* │  │ /api/watchlist/* │
    │                │  │              │  │                  │
    │ • POST register│  │ • GET search │  │ • GET  list      │
    │ • POST login   │  │ • GET analyze│  │ • POST add       │
    │ • GET  me      │  │ • GET compare│  │ • DELETE remove   │
    │                │  │ • GET tooltip │  │ • PUT  alerts    │
    └───────┬────────┘  └──────┬───────┘  └──────┬───────────┘
            │                  │                  │
            │           ┌──────▼───────┐          │
            │           │data_fetcher  │          │
            │           │              │          │
            │           │ 3-Tier Data  │          │
            │           │  Resolution: │          │
            │           │ 1. Cache     │          │
            │           │ 2. API Call  │          │
            │           │ 3. Demo Data │          │
            │           └──┬───────┬───┘          │
            │              │       │              │
            │    ┌─────────▼─┐  ┌──▼───────────┐  │
            │    │  Alpha    │  │  demo_data   │  │
            │    │  Vantage  │  │  (Fallback)  │  │
            │    │  REST API │  │  5 stocks    │  │
            │    └───────────┘  └──────────────┘  │
            │                                     │
            │    ┌────────────────────────┐        │
            │    │   analysis_engine.py   │        │
            │    │                        │        │
            │    │  Stage 1: Metrics      │        │
            │    │  Stage 2: Red Flags    │        │
            │    │  Stage 3: Health Score │        │
            │    └────────────────────────┘        │
            │                                     │
    ┌───────▼─────────────────────────────────────▼──┐
    │                  models.py                      │
    │             (Data Access Layer)                  │
    │                                                 │
    │  ┌──────────────────────────────────────────┐   │
    │  │            SQLite (WAL Mode)              │   │
    │  │                                          │   │
    │  │  ┌─────────┐ ┌──────────┐ ┌───────────┐  │   │
    │  │  │  users  │ │watchlist │ │cached_data│  │   │
    │  │  └─────────┘ └──────────┘ └───────────┘  │   │
    │  └──────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────┘
```

---

## Directory Structure

```
PBL/
├── run.py                    # Entry point — starts Flask on :5050
├── database.db               # SQLite database (auto-created)
│
├── backend/
│   ├── __init__.py
│   ├── app.py                # Flask application factory + static serving
│   ├── config.py             # Configuration (secrets, DB path, API key)
│   ├── models.py             # Database schema + CRUD operations
│   ├── auth.py               # JWT authentication (register, login, decorators)
│   ├── stocks.py             # Stock API blueprint (search, analyze, compare)
│   ├── watchlist_api.py      # Watchlist CRUD blueprint (protected routes)
│   ├── data_fetcher.py       # Alpha Vantage client + cache + fallback logic
│   ├── analysis_engine.py    # Three-stage financial analysis pipeline
│   ├── demo_data.py          # Hardcoded financial data for 5 demo stocks
│   └── requirements.txt      # Python dependencies
│
├── frontend/
│   ├── index.html            # Single-page app shell
│   ├── css/
│   │   └── styles.css        # Complete stylesheet (dark theme, responsive)
│   └── js/
│       ├── api.js            # Centralized HTTP client with JWT injection
│       ├── app.js            # Main controller (navigation, search, compare)
│       ├── auth.js           # Login/register modal and session management
│       ├── analysis.js       # Beginner & Advanced analysis rendering
│       ├── charts.js         # Chart.js wrappers (radar, bar, line charts)
│       └── watchlist.js      # Watchlist UI and CRUD operations
│
└── tests/
    ├── conftest.py           # Pytest fixtures (temp DB, test client, JWT)
    ├── test_analysis_engine.py  # Unit tests for analysis pipeline
    └── test_api.py           # Integration tests for API endpoints
```

---

## Component Details

### 1. Flask Application Factory (`app.py`)

- Creates the Flask app with `create_app()` factory pattern
- Configures CORS for `/api/*` routes
- Registers three blueprints: `auth_bp`, `stocks_bp`, `watchlist_bp`
- Serves the frontend as static files (single-process deployment)
- Initializes the database on startup via `init_db()`

### 2. Authentication Layer (`auth.py`)

```
Registration Flow:
  POST /api/auth/register
  → Validate inputs (username ≥3, valid email, password ≥6)
  → bcrypt.hashpw(password, salt)
  → INSERT INTO users
  → Generate JWT (HS256, 24h expiry)
  → Return {token, user}

Login Flow:
  POST /api/auth/login
  → Lookup user by email
  → bcrypt.checkpw(password, stored_hash)
  → Generate JWT
  → Return {token, user}

Route Protection:
  @login_required  → 401 if no valid token
  @optional_auth   → Sets user if token present, allows anonymous
```

### 3. Data Fetcher (`data_fetcher.py`)

Implements a three-tier data resolution strategy:

```
fetch_stock_data(ticker)
    │
    ├── 1. Check SQLite cache (TTL: 24 hours)
    │      └── HIT → return cached data
    │
    ├── 2. Call Alpha Vantage API (4 endpoints)
    │      ├── OVERVIEW
    │      ├── INCOME_STATEMENT
    │      ├── BALANCE_SHEET
    │      └── CASH_FLOW
    │      └── SUCCESS → cache in SQLite, return data
    │
    └── 3. Fall back to demo_data.py
           └── Returns hardcoded data for AAPL, MSFT, GOOGL, AMZN, TSLA
```

### 4. Analysis Engine (`analysis_engine.py`)

The core of the platform — a three-stage sequential pipeline:

```
Raw Financial Data
        │
        ▼
┌───────────────────────────────────────┐
│  STAGE 1: Metric Calculation          │
│  calculate_metrics()                  │
│                                       │
│  Input:  Raw financial statements     │
│  Output: 20+ ratios + historical      │
│          time-series arrays           │
│                                       │
│  Categories:                          │
│  • Profitability (6): Gross Margin,   │
│    Operating Margin, Net Margin,      │
│    ROE, ROA, ROIC                     │
│  • Valuation (5): PE, PB, PS,        │
│    EV/EBITDA, FCF Yield              │
│  • Financial Health (4): Current      │
│    Ratio, Quick Ratio, D/E,          │
│    Interest Coverage                  │
│  • Efficiency (2): Asset Turnover,   │
│    Inventory Turnover                │
│  • Cash Flow (3): OCF Margin, FCF,   │
│    FCF/Revenue                        │
│  • Growth (3): Revenue CAGR,         │
│    YoY Revenue, YoY Income           │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  STAGE 2: Red Flag Detection          │
│  detect_red_flags()                   │
│                                       │
│  Input:  Metrics + Historical data    │
│  Output: List of warning signals      │
│          with severity levels         │
│                                       │
│  Rules:                               │
│  • Revenue declining 2+ years  [HIGH] │
│  • Negative net income         [HIGH] │
│  • Negative FCF 3+ years      [HIGH] │
│  • Debt/Equity > 2.0       [MED/HIGH]│
│  • Interest coverage < 1.5    [HIGH] │
│  • Gross margin erosion > 5pp  [MED] │
│  • PE Ratio > 50               [MED] │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  STAGE 3: Health Score Synthesis      │
│  calculate_health_score()             │
│                                       │
│  Input:  Metrics + Red flags          │
│  Output: Composite score (0-100)      │
│                                       │
│  Weighted Dimensions:                 │
│  ┌──────────────────┬────────┐        │
│  │ Growth           │  25%   │        │
│  │ Profitability    │  30%   │        │
│  │ Financial Health │  30%   │        │
│  │ Valuation        │  15%   │        │
│  └──────────────────┴────────┘        │
│                                       │
│  Red Flag Penalties:                  │
│    HIGH → -5 pts  |  MEDIUM → -3 pts │
│                                       │
│  Labels:                              │
│    ≥80 Excellent | ≥65 Good | ≥50 Fair│
│    ≥35 Weak      | <35 Poor          │
└───────────────────────────────────────┘
                │
                ▼
        Analysis Result JSON
```

### 5. Database Schema (`models.py`)

```
┌─────────────────────┐     ┌────────────────────────────┐
│       users          │     │         watchlist           │
├─────────────────────┤     ├────────────────────────────┤
│ id          INTEGER PK│◄───│ user_id   INTEGER FK       │
│ username    TEXT UNQ  │     │ id        INTEGER PK       │
│ email       TEXT UNQ  │     │ ticker    TEXT              │
│ password_hash TEXT    │     │ company_name TEXT           │
│ created_at  TIMESTAMP│     │ added_at  TIMESTAMP         │
└─────────────────────┘     │ alert_config TEXT (JSON)    │
                            │ UNIQUE(user_id, ticker)     │
                            └────────────────────────────┘

┌────────────────────────────┐
│       cached_data           │
├────────────────────────────┤
│ id         INTEGER PK       │
│ ticker     TEXT              │
│ data_type  TEXT              │ ← overview | income | balance | cashflow
│ data       TEXT (JSON)       │
│ fetched_at TIMESTAMP         │ ← Used for TTL (24h)
│ UNIQUE(ticker, data_type)   │ ← Enables UPSERT
└────────────────────────────┘

Indexes:
  • idx_watchlist_user  ON watchlist(user_id)
  • idx_cached_ticker   ON cached_data(ticker)

Pragmas:
  • journal_mode = WAL  (concurrent reads)
  • foreign_keys = ON   (referential integrity)
```

### 6. Frontend Architecture

```
index.html (SPA Shell)
    │
    ├── Sidebar Navigation (Dashboard, Analysis, Compare, Watchlist)
    ├── Top Bar (Search, Mode Toggle, Auth Actions)
    ├── Dynamic Content Area (#pageContent)
    ├── Auth Modal
    ├── Tooltip Container
    └── Toast Container

JavaScript Module Dependency:
    api.js          ← No dependencies (base HTTP client)
        ▲
        │
    auth.js         ← Uses api.js for login/register
        ▲
        │
    charts.js       ← Uses Chart.js CDN (radar, bar, line)
        ▲
        │
    analysis.js     ← Uses api.js + charts.js
        ▲
        │
    watchlist.js    ← Uses api.js
        ▲
        │
    app.js          ← Orchestrates all modules (init, navigation, search)
```

**Key Frontend Patterns:**
- **SPA without a framework**: Client-side routing via `navigateTo(view)` and DOM injection
- **Debounced search**: 200ms delay on keystroke before API call
- **Dual-mode rendering**: Same data, different `render*View()` functions
- **JWT in localStorage**: Auto-attached to all requests via `api.js`
- **Mode persistence**: Beginner/Advanced stored in `localStorage`

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/register` | — | Create account, return JWT |
| `POST` | `/api/auth/login` | — | Authenticate, return JWT |
| `GET` | `/api/auth/me` | Required | Get current user profile |
| `GET` | `/api/stocks/search?q=` | — | Search stocks by ticker/name |
| `GET` | `/api/stocks/analyze/<ticker>` | — | Run full analysis pipeline |
| `GET` | `/api/stocks/compare?tickers=` | — | Compare up to 5 stocks |
| `GET` | `/api/stocks/tooltips` | — | Get metric educational tooltips |
| `GET` | `/api/watchlist/` | Required | List user's watchlist |
| `POST` | `/api/watchlist/` | Required | Add stock to watchlist |
| `DELETE` | `/api/watchlist/<ticker>` | Required | Remove stock from watchlist |
| `PUT` | `/api/watchlist/<ticker>/alerts` | Required | Configure alert thresholds |

---

## Data Flow Diagram

```
User Action          Frontend              Backend                External
───────────         ─────────             ─────────              ─────────

Search "AAPL"  ──►  api.js GET            stocks_bp.search()
                    /api/stocks/search  ──► search_tickers()
                                           (in-memory match)
               ◄──  Render dropdown   ◄──  [{ticker, name}]

Click result   ──►  api.js GET            stocks_bp.analyze()
                    /api/stocks/         ──► data_fetcher
                    analyze/AAPL              │
                                             ├─► Cache check ──► SQLite
                                             │     (miss)
                                             ├─► API call    ──► Alpha Vantage
                                             │     (fail)         (4 endpoints)
                                             └─► Demo data
                                                    │
                                             analysis_engine
                                             .run_full_analysis()
                                                    │
                                             Stage 1 → Metrics
                                             Stage 2 → Red Flags
                                             Stage 3 → Health Score
                                                    │
               ◄──  Render view        ◄──  {company, metrics,
                    (Beginner or              historical, redFlags,
                     Advanced)                healthScore, summary}
```

---

## Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend framework | Flask | Lightweight, minimal boilerplate for REST APIs |
| Database | SQLite (WAL) | Zero-config, embedded, sufficient for single-server |
| Auth mechanism | JWT + bcrypt | Stateless auth, secure password storage |
| Frontend | Vanilla JS | No build step, fast load, full control |
| Charts | Chart.js 4 | Rich chart types, small footprint |
| External data | Alpha Vantage | Free tier with financial statement data |
| Testing | pytest | Fixtures, parametrize, clean test isolation |
| Deployment | Single-process | Flask serves API + static files together |

---

## Security Considerations

- **Password storage**: bcrypt with random salt (never stored in plaintext)
- **JWT tokens**: HS256 signed with server secret, 24-hour expiry
- **Input validation**: Server-side validation on all endpoints
- **SQL injection**: Parameterized queries throughout `models.py`
- **CORS**: Restricted to `/api/*` routes
- **Rate limiting**: Alpha Vantage responses cached for 24h to avoid abuse
- **Error handling**: API errors never expose internal stack traces

---

## Testing Architecture

```
tests/
├── conftest.py                 # Shared fixtures
│   ├── app_and_db (autouse)    # Temp SQLite DB per test
│   ├── client                  # Flask test client
│   └── auth_token              # Pre-generated valid JWT
│
├── test_analysis_engine.py     # Unit tests
│   ├── test_safe_div           # Edge cases: None, zero, strings
│   ├── test_calc_growth        # CAGR calculation
│   ├── test_calc_metrics_*     # PE, margins, health, FCF
│   ├── test_red_flags_*        # Negative FCF, high debt detection
│   ├── test_health_score_bounds# Score always in [0, 100]
│   └── test_run_full_analysis  # End-to-end pipeline integration
│
└── test_api.py                 # Integration tests
    ├── test_auth_*             # Registration, login, wrong password
    ├── test_unauthorized       # 401 on protected routes
    ├── test_authorized_watchlist# JWT-protected access
    ├── test_cache_miss_and_hit # Cache behavior + response time <500ms
    ├── test_sector_comparison  # 5-stock comparison endpoint
    └── test_alert_threshold    # Alert breach simulation
```

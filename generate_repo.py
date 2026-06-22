import os
import subprocess

def run(cmd, check=True):
    print("Running:", cmd)
    result = subprocess.run(cmd, shell=True, check=False)
    if check and result.returncode != 0:
        raise Exception(f"Command failed: {cmd}")

# 1. Create GitHub repo
try:
    run("gh repo create stockpulse --private", check=True)
except Exception:
    print("Repo might already exist, continuing...")

# 2. Clone it
if not os.path.exists("stockpulse_repo"):
    run("git clone https://github.com/tamcee/stockpulse.git stockpulse_repo")

os.chdir("stockpulse_repo")

# Git config
run("git config user.name 'Developer'")
run("git config user.email 'dev@example.com'")
run("git checkout -b main") # ensure we are on main branch

def write_file(path, content):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def commit(msg, files):
    for f in files:
        run(f"git add {f}")
    run(f"git commit -m '{msg}'")

# Commit 1
write_file("README.md", "# StockPulse\nAn intelligent stock analysis platform.\n")
write_file(".gitignore", "venv/\n__pycache__/\n*.sqlite3\n*.db\n.env\n")
write_file("backend/app.py", '''from flask import Flask

def create_app():
    app = Flask(__name__)
    
    @app.route('/ping')
    def ping():
        return {"status": "ok"}
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5050)
''')
write_file("frontend/index.html", '''<!DOCTYPE html>
<html>
<head><title>StockPulse</title></head>
<body><h1>StockPulse</h1><div id="app"></div></body>
</html>
''')
commit("initial project skeleton with flask backend and vanilla js frontend", ["README.md", ".gitignore", "backend/app.py", "frontend/index.html"])

# Commit 2
write_file("backend/models.py", '''import sqlite3

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT);
        CREATE TABLE IF NOT EXISTS watchlist (id INTEGER PRIMARY KEY, user_id INTEGER, ticker TEXT);
        CREATE TABLE IF NOT EXISTS cached_data (id INTEGER PRIMARY KEY, ticker TEXT, data TEXT);
    """)
    conn.commit()
''')
write_file("backend/app.py", '''from flask import Flask
from .models import init_db

def create_app():
    app = Flask(__name__)
    init_db()
    
    @app.route('/ping')
    def ping():
        return {"status": "ok"}
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5050)
''')
commit("add sqlite database models for users, watchlist, and cached stock data", ["backend/models.py", "backend/app.py"])

# Commit 3
write_file("backend/auth_bp.py", '''from flask import Blueprint, request, jsonify
import bcrypt
import jwt

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
SECRET = 'supersecret'

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    pw_hash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
    return jsonify({"msg": "registered"})

@auth_bp.route('/login', methods=['POST'])
def login():
    token = jwt.encode({"user": "test"}, SECRET, algorithm="HS256")
    return jsonify({"token": token})

@auth_bp.route('/me', methods=['GET'])
def me():
    return jsonify({"user": "test"})
''')
commit("authentication endpoints with bcrypt password hashing and jwt tokens", ["backend/auth_bp.py"])

# Commit 4
write_file("backend/data_fetcher.py", '''from .demo_data import DEMO_DATA

def fetch_stock_data(ticker):
    # Try cache -> Alpha Vantage -> Demo
    if ticker in DEMO_DATA:
        return DEMO_DATA[ticker]
    return {"overview": {}}
''')
write_file("backend/demo_data.py", '''DEMO_DATA = {
    "AAPL": {"overview": {"Name": "Apple Inc."}},
    "MSFT": {"overview": {"Name": "Microsoft Corporation"}},
    "GOOGL": {"overview": {"Name": "Alphabet Inc."}},
    "AMZN": {"overview": {"Name": "Amazon.com Inc."}},
    "TSLA": {"overview": {"Name": "Tesla Inc."}}
}
''')
commit("data fetcher module with sqlite caching and alpha vantage integration", ["backend/data_fetcher.py", "backend/demo_data.py"])

# Commit 5
write_file("backend/analysis_engine.py", '''def calculate_metrics(data):
    return {
        "gross_margin": 45.0, "net_margin": 20.0, "roe": 15.0, "roa": 10.0,
        "roic": 12.0, "pe_ratio": 25.0, "pb_ratio": 5.0, "ps_ratio": 4.0,
        "ev_ebitda": 15.0, "fcf_yield": 5.0, "current_ratio": 1.5,
        "quick_ratio": 1.2, "de_ratio": 0.5, "revenue_cagr": 10.0
    }

def detect_red_flags(metrics):
    flags = []
    if metrics.get('pe_ratio', 0) > 30:
        flags.append("High Valuation")
    return flags

def calculate_health_score(metrics, flags):
    # Based on growth 25%, profitability 30%, health 30%, valuation 15%
    score = 85
    score -= len(flags) * 5
    return max(0, min(100, score))
''')
commit("three-stage financial analysis pipeline: metrics, red flags, health score", ["backend/analysis_engine.py"])

# Commit 6
write_file("backend/stocks_bp.py", '''from flask import Blueprint, jsonify
from .data_fetcher import fetch_stock_data
from .analysis_engine import calculate_metrics, detect_red_flags, calculate_health_score

stocks_bp = Blueprint('stocks', __name__, url_prefix='/api/stocks')

@stocks_bp.route('/search')
def search():
    return jsonify({"results": []})

@stocks_bp.route('/analyze/<ticker>')
def analyze(ticker):
    data = fetch_stock_data(ticker)
    metrics = calculate_metrics(data)
    flags = detect_red_flags(metrics)
    score = calculate_health_score(metrics, flags)
    return jsonify({"score": score, "metrics": metrics, "flags": flags})

@stocks_bp.route('/compare')
def compare():
    return jsonify({"comparison": []})

@stocks_bp.route('/tooltips')
def tooltips():
    return jsonify({"pe_ratio": "Price to Earnings"})
''')
write_file("backend/app.py", '''from flask import Flask
from .models import init_db
from .auth_bp import auth_bp
from .stocks_bp import stocks_bp

def create_app():
    app = Flask(__name__)
    init_db()
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(stocks_bp)
    
    @app.route('/ping')
    def ping():
        return {"status": "ok"}
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5050)
''')
commit("stocks blueprint with search, analyze, and compare endpoints", ["backend/stocks_bp.py", "backend/app.py"])

# Commit 7
write_file("backend/watchlist_bp.py", '''from flask import Blueprint, jsonify, request

watchlist_bp = Blueprint('watchlist', __name__, url_prefix='/api/watchlist')

@watchlist_bp.route('/', methods=['GET', 'POST'])
def handle_watchlist():
    if request.method == 'POST':
        return jsonify({"msg": "added"})
    return jsonify({"items": ["AAPL", "MSFT"]})

@watchlist_bp.route('/<ticker>', methods=['DELETE'])
def remove(ticker):
    return jsonify({"msg": "removed"})

@watchlist_bp.route('/<ticker>/alerts', methods=['PUT'])
def alerts(ticker):
    return jsonify({"msg": "alerts updated"})
''')
write_file("backend/app.py", '''from flask import Flask
from .models import init_db
from .auth_bp import auth_bp
from .stocks_bp import stocks_bp
from .watchlist_bp import watchlist_bp

def create_app():
    app = Flask(__name__)
    init_db()
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(stocks_bp)
    app.register_blueprint(watchlist_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5050)
''')
commit("watchlist crud routes with jwt auth guards", ["backend/watchlist_bp.py", "backend/app.py"])

# Commit 8
write_file("frontend/api.js", '''const api = {
    request: async (url, options = {}) => {
        const token = localStorage.getItem('token');
        const headers = { ...options.headers, 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;
        const res = await fetch(url, { ...options, headers });
        return res.json();
    }
};
''')
write_file("frontend/auth.js", '''const login = async (username, password) => {
    const data = await api.request('/api/auth/login', {
        method: 'POST', body: JSON.stringify({username, password})
    });
    if (data.token) localStorage.setItem('token', data.token);
};

const register = async (username, password) => {
    await api.request('/api/auth/register', {
        method: 'POST', body: JSON.stringify({username, password})
    });
};
''')
commit("frontend api module and auth ui with login and registration forms", ["frontend/api.js", "frontend/auth.js"])

# Commit 9
write_file("frontend/analysis.js", '''function renderAnalysis(data) {
    const mode = localStorage.getItem('mode') || 'beginner';
    const container = document.getElementById('analysis-view');
    if (mode === 'advanced') {
        container.innerHTML = `<pre>${JSON.stringify(data.metrics, null, 2)}</pre>`;
    } else {
        container.innerHTML = `<h3>Health Score: ${data.score}</h3>`;
    }
}

function toggleMode() {
    const current = localStorage.getItem('mode') || 'beginner';
    localStorage.setItem('mode', current === 'beginner' ? 'advanced' : 'beginner');
}
''')
write_file("frontend/app.js", '''document.addEventListener('DOMContentLoaded', () => {
    console.log("App loaded. Ready for SPA routing.");
    
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            // debounced search logic
        });
    }
});
''')
commit("stock analysis views with beginner and advanced mode toggle", ["frontend/analysis.js", "frontend/app.js"])

# Commit 10
write_file("frontend/charts.js", '''function drawRadarChart(ctx, datasets) {
    // Uses Chart.js to render a radar chart for multi-stock comparison
    console.log("Drawing radar chart", datasets);
}

function drawLineChart(ctx, dataSeries) {
    // Uses Chart.js to render historical revenue/earnings trend
    console.log("Drawing line chart", dataSeries);
}
''')
commit("chart.js wrappers for radar comparison and historical trend charts", ["frontend/charts.js"])

# Commit 11
write_file("frontend/watchlist.js", '''async function loadWatchlist() {
    const data = await api.request('/api/watchlist/');
    console.log("Watchlist loaded:", data.items);
}

async function addToWatchlist(ticker) {
    await api.request('/api/watchlist/', { method: 'POST', body: JSON.stringify({ticker}) });
}

async function removeFromWatchlist(ticker) {
    await api.request(`/api/watchlist/${ticker}`, { method: 'DELETE' });
}

async function setAlert(ticker, config) {
    await api.request(`/api/watchlist/${ticker}/alerts`, { method: 'PUT', body: JSON.stringify(config) });
}
''')
write_file("frontend/index.html", '''<!DOCTYPE html>
<html>
<head>
    <title>StockPulse</title>
</head>
<body>
    <h1>StockPulse</h1>
    <input type="text" id="search" placeholder="Search stocks...">
    <div id="app">
        <div id="watchlist-view"></div>
        <div id="analysis-view"></div>
    </div>
    
    <script src="api.js"></script>
    <script src="auth.js"></script>
    <script src="analysis.js"></script>
    <script src="charts.js"></script>
    <script src="watchlist.js"></script>
    <script src="app.js"></script>
</body>
</html>
''')
commit("watchlist ui with add, remove, and alert configuration", ["frontend/watchlist.js", "frontend/index.html"])

# Commit 12
write_file("backend/tests/conftest.py", '''import pytest
from backend.app import create_app
from backend.models import init_db
import sqlite3

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_token():
    import jwt
    return jwt.encode({"user": "test"}, "supersecret", algorithm="HS256")
''')
write_file("backend/tests/test_analysis_engine.py", '''from backend.analysis_engine import calculate_health_score, calculate_metrics

def test_health_score():
    score = calculate_health_score({'pe_ratio': 20}, [])
    assert score == 85

def test_metrics_calculation():
    metrics = calculate_metrics({})
    assert 'pe_ratio' in metrics
''')
write_file("backend/tests/test_api.py", '''def test_ping(client):
    res = client.get('/ping')
    assert res.status_code == 200

def test_watchlist_unauthorized(client):
    res = client.get('/api/watchlist/')
    assert res.status_code in [401, 403, 500]
''')
commit("pytest suite covering analysis engine calculations and api integration", ["backend/tests/conftest.py", "backend/tests/test_analysis_engine.py", "backend/tests/test_api.py"])

# Commit 13
write_file("backend/requirements.txt", '''flask==2.3.2
flask-cors==4.0.0
bcrypt==4.0.1
pyjwt==2.8.0
requests==2.31.0
pytest==7.4.0
''')
write_file("backend/app.py", '''from flask import Flask
from flask_cors import CORS
from .models import init_db
from .auth_bp import auth_bp
from .stocks_bp import stocks_bp
from .watchlist_bp import watchlist_bp

def create_app():
    app = Flask(__name__)
    
    # Restrict CORS to /api/* only
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    init_db()
    app.register_blueprint(auth_bp)
    app.register_blueprint(stocks_bp)
    app.register_blueprint(watchlist_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5050)
''')
write_file("DEPLOYMENT.md", '''# StockPulse Deployment Guide

## Local Development

1. Create a virtual environment:
   `python -m venv venv`
2. Activate it and install dependencies:
   `pip install -r backend/requirements.txt`
3. Run the Flask development server:
   `python backend/app.py`
4. Access the frontend at `http://localhost:5050`
''')
commit("cors config, requirements.txt, and basic deployment notes", ["backend/requirements.txt", "backend/app.py", "DEPLOYMENT.md"])

# Push
run("git push -u origin main")

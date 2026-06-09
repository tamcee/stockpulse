from flask import Blueprint, jsonify
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

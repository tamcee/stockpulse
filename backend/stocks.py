"""
Stock Data Blueprint — search, analyze, and compare stocks.
"""
from flask import Blueprint, request, jsonify

from backend.data_fetcher import search_stocks, fetch_stock_data
from backend.analysis_engine import run_full_analysis, METRIC_TOOLTIPS

stocks_bp = Blueprint('stocks', __name__, url_prefix='/api/stocks')


@stocks_bp.route('/search', methods=['GET'])
def search():
    """Search stocks by ticker or company name."""
    query = request.args.get('q', '').strip()
    if not query or len(query) < 1:
        return jsonify({'results': []})

    results = search_stocks(query)
    return jsonify({'results': results})


@stocks_bp.route('/analyze/<ticker>', methods=['GET'])
def analyze(ticker):
    """Fetch stock data and run full analysis."""
    ticker = ticker.upper().strip()

    # Fetch data
    data = fetch_stock_data(ticker)
    if not data:
        return jsonify({'error': f'No data available for {ticker}'}), 404

    # Run analysis engine
    analysis = run_full_analysis(
        data['overview'],
        data['income'],
        data['balance'],
        data['cashflow']
    )

    return jsonify({
        'ticker': ticker,
        'analysis': analysis,
        'isDemo': ticker in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
    })


@stocks_bp.route('/compare', methods=['GET'])
def compare():
    """Compare multiple stocks (up to 5)."""
    tickers_str = request.args.get('tickers', '')
    tickers = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]

    if not tickers:
        return jsonify({'error': 'Provide at least one ticker'}), 400
    if len(tickers) > 5:
        return jsonify({'error': 'Maximum 5 stocks for comparison'}), 400

    results = []
    for ticker in tickers:
        data = fetch_stock_data(ticker)
        if data:
            analysis = run_full_analysis(
                data['overview'],
                data['income'],
                data['balance'],
                data['cashflow']
            )
            results.append({
                'ticker': ticker,
                'analysis': analysis,
            })

    return jsonify({'comparisons': results})


@stocks_bp.route('/tooltips', methods=['GET'])
def get_tooltips():
    """Return all metric tooltips for the educational layer."""
    return jsonify({'tooltips': METRIC_TOOLTIPS})

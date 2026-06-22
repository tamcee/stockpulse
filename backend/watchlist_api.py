"""
Watchlist Blueprint — CRUD operations for user watchlists.
"""
import json
from flask import Blueprint, request, jsonify, g
from backend.auth import login_required
from backend.models import (
    get_user_watchlist,
    add_to_watchlist,
    remove_from_watchlist,
    update_alert_config,
)

watchlist_bp = Blueprint('watchlist', __name__, url_prefix='/api/watchlist')


@watchlist_bp.route('/', methods=['GET'])
@login_required
def get_watchlist():
    """Get the current user's watchlist."""
    items = get_user_watchlist(g.current_user['id'])
    # Parse alert_config JSON strings
    for item in items:
        if isinstance(item.get('alert_config'), str):
            try:
                item['alert_config'] = json.loads(item['alert_config'])
            except (json.JSONDecodeError, TypeError):
                item['alert_config'] = {}
    return jsonify({'watchlist': items})


@watchlist_bp.route('/', methods=['POST'])
@login_required
def add_stock():
    """Add a stock to the watchlist."""
    data = request.get_json()
    if not data or not data.get('ticker'):
        return jsonify({'error': 'Ticker is required'}), 400

    ticker = data['ticker'].upper().strip()
    company_name = data.get('company_name', '')

    try:
        add_to_watchlist(g.current_user['id'], ticker, company_name)
        return jsonify({'message': f'{ticker} added to watchlist'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 409


@watchlist_bp.route('/<ticker>', methods=['DELETE'])
@login_required
def remove_stock(ticker):
    """Remove a stock from the watchlist."""
    deleted = remove_from_watchlist(g.current_user['id'], ticker.upper())
    if deleted:
        return jsonify({'message': f'{ticker.upper()} removed from watchlist'})
    return jsonify({'error': 'Stock not found in watchlist'}), 404


@watchlist_bp.route('/<ticker>/alerts', methods=['PUT'])
@login_required
def configure_alerts(ticker):
    """Configure alert thresholds for a watchlist item."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Alert configuration is required'}), 400

    update_alert_config(g.current_user['id'], ticker.upper(), data)
    return jsonify({'message': f'Alerts updated for {ticker.upper()}'})

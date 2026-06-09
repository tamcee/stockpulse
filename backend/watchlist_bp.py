from flask import Blueprint, jsonify, request

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

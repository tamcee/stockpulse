from flask import Flask
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

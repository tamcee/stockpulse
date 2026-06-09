from flask import Flask
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

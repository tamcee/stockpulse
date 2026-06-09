from flask import Flask
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

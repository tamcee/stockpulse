#!/usr/bin/env python3
"""
Entry point — starts the Flask development server.
Usage: python run.py
"""
from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  Intelligent Fundamental Stock Analysis Platform")
    print("  Running at: http://localhost:5050")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5050)

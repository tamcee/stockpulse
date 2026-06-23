# StockPulse Deployment Guide

🚀 **Live Deployment:** [https://stockpulse-production-0341.up.railway.app](https://stockpulse-production-0341.up.railway.app)

## Production Deployment (Railway + Neon)

StockPulse is configured for easy zero-config deployment on Railway using Nixpacks.

### Prerequisites
1. A permanent, free PostgreSQL database on [Neon.tech](https://neon.tech/).
2. A free [Railway.app](https://railway.app/) account linked to your GitHub.

### Deployment Steps
1. Push your code to GitHub.
2. In Railway, click **New Project** -> **Deploy from GitHub repo** and select `stockpulse`.
3. Go to the **Variables** tab of your new Railway service.
4. Add your environment variables:
   - `DATABASE_URL`: Your PostgreSQL connection string from Neon.
   - `SECRET_KEY`: A secure, random string for JWT signing.
5. Railway will automatically detect the `wsgi:app` entrypoint from the `Procfile` (or `gunicorn` defaults) and use `.python-version` to build the app with Python 3.12.

## Local Development

1. Create a virtual environment:
   `python -m venv venv`
2. Activate it and install dependencies:
   `pip install -r requirements.txt`
3. Set up your `.env` file with `DATABASE_URL` and `SECRET_KEY`.
4. Run the Flask development server:
   `python run.py`
5. Access the frontend at `http://localhost:5050`

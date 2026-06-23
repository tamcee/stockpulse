import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-2024')
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database.db')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    JWT_EXPIRY_HOURS = 24
    CACHE_TTL_HOURS = 24

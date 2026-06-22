import psycopg2
import psycopg2.extras
import json
from datetime import datetime
from backend.config import Config


def get_db():
    """Get a PostgreSQL database connection."""
    conn = psycopg2.connect(Config.DATABASE_URL)
    return conn


def init_db():
    """Initialize database tables for PostgreSQL."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS watchlist (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            company_name TEXT DEFAULT '',
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            alert_config TEXT DEFAULT '{}',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, ticker)
        );

        CREATE TABLE IF NOT EXISTS cached_data (
            id SERIAL PRIMARY KEY,
            ticker TEXT NOT NULL,
            data_type TEXT NOT NULL,
            data TEXT NOT NULL,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker, data_type)
        );

        CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlist(user_id);
        CREATE INDEX IF NOT EXISTS idx_cached_ticker ON cached_data(ticker);
    ''')

    conn.commit()
    conn.close()


# --- User operations ---

def create_user(username, email, password_hash):
    """Create a new user. Returns user id."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id',
            (username, email, password_hash)
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        return user_id
    except psycopg2.IntegrityError as e:
        conn.rollback()
        err_msg = str(e).lower()
        if 'email' in err_msg:
            raise ValueError('Email already registered')
        elif 'username' in err_msg:
            raise ValueError('Username already taken')
        raise
    finally:
        conn.close()


def get_user_by_email(email):
    """Fetch user by email."""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_id(user_id):
    """Fetch user by ID."""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT id, username, email, created_at FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


# --- Watchlist operations ---

def get_user_watchlist(user_id):
    """Get all watchlist items for a user."""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(
        'SELECT * FROM watchlist WHERE user_id = %s ORDER BY added_at DESC',
        (user_id,)
    )
    items = cursor.fetchall()
    conn.close()
    return [dict(item) for item in items]


def add_to_watchlist(user_id, ticker, company_name=''):
    """Add a stock to user's watchlist."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO watchlist (user_id, ticker, company_name) VALUES (%s, %s, %s)',
            (user_id, ticker.upper(), company_name)
        )
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        raise ValueError('Stock already in watchlist')
    finally:
        conn.close()


def remove_from_watchlist(user_id, ticker):
    """Remove a stock from user's watchlist."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'DELETE FROM watchlist WHERE user_id = %s AND ticker = %s',
        (user_id, ticker.upper())
    )
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def update_alert_config(user_id, ticker, alert_config):
    """Update alert configuration for a watchlist item."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE watchlist SET alert_config = %s WHERE user_id = %s AND ticker = %s',
        (json.dumps(alert_config), user_id, ticker.upper())
    )
    conn.commit()
    conn.close()


# --- Cache operations ---

def get_cached_data(ticker, data_type, max_age_hours=24):
    """Get cached data if fresh enough."""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(
        '''SELECT data, fetched_at FROM cached_data 
           WHERE ticker = %s AND data_type = %s
           AND fetched_at > NOW() - CAST(%s AS INTERVAL)''',
        (ticker.upper(), data_type, f"{max_age_hours} hours")
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row['data'])
    return None


def set_cached_data(ticker, data_type, data):
    """Store or update cached data."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO cached_data (ticker, data_type, data, fetched_at) 
           VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
           ON CONFLICT (ticker, data_type) 
           DO UPDATE SET data = EXCLUDED.data, fetched_at = CURRENT_TIMESTAMP''',
        (ticker.upper(), data_type, json.dumps(data))
    )
    conn.commit()
    conn.close()

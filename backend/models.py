import sqlite3

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT);
        CREATE TABLE IF NOT EXISTS watchlist (id INTEGER PRIMARY KEY, user_id INTEGER, ticker TEXT);
        CREATE TABLE IF NOT EXISTS cached_data (id INTEGER PRIMARY KEY, ticker TEXT, data TEXT);
    """)
    conn.commit()

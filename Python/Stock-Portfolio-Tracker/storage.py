# storage.py
# ─────────────────────────────────────────────
# Handles all SQLite database operations:
# - Table initialization
# - Inserting daily price records
# - Fetching historical price data
# ─────────────────────────────────────────────

import sqlite3
from datetime import datetime
from config import DB_NAME


def init_db():
    """
    Initializes the SQLite database.
    Creates the daily_prices table if it does not exist.
    Returns an open connection object.
    """
    conn   = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_prices (
            date          TEXT,
            ticker        TEXT,
            price         REAL,
            shares        INTEGER,
            total_value   REAL,
            unrealized_pl REAL
        )
    ''')
    conn.commit()
    return conn


def insert_daily_record(cursor, date_str, ticker, price, shares,
                         total_value, unrealized_pl):
    """
    Inserts one daily price record into the daily_prices table.
    """
    cursor.execute('''
        INSERT INTO daily_prices
            (date, ticker, price, shares, total_value, unrealized_pl)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (date_str, ticker, price, shares, total_value, unrealized_pl))


def get_price_history(conn, ticker):
    """
    Fetches all historical price records for a given ticker.
    Returns two lists: dates (datetime) and prices (float).
    """
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date, price
        FROM   daily_prices
        WHERE  ticker = ?
        ORDER  BY date ASC
    ''', (ticker,))
    rows   = cursor.fetchall()
    dates  = [datetime.strptime(row[0], "%Y-%m-%d") for row in rows]
    prices = [row[1] for row in rows]
    return dates, prices

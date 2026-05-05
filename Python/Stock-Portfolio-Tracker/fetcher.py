# fetcher.py
# ─────────────────────────────────────────────
# Handles all yfinance API calls to fetch
# the latest closing price for each ticker.
# ─────────────────────────────────────────────

import yfinance as yf


def get_latest_price(ticker):
    """
    Fetches the latest closing price for a given ticker.
    Returns a rounded float or None if the fetch fails.
    """
    try:
        stock       = yf.Ticker(ticker)
        todays_data = stock.history(period='1d')
        return round(todays_data['Close'].iloc[0], 2)
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return None

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time


def load_data(stock_name):
    start_date = "2017-01-01"
    end_date   = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    # Use a custom session with a realistic User-Agent to bypass Cloud blockers
    import requests
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    })
    
    ticker = yf.Ticker(stock_name, session=session)
    data   = ticker.history(start=start_date, end=end_date, auto_adjust=False)

    if data is None or data.empty:
        return None, {}

    # Use Adj Close if available
    if 'Adj Close' in data.columns:
        data['Close'] = data['Adj Close']

    # ── Data Quality Fixes ────────────────────────────────────────
    # 1. Remove rows where Close is 0 or NaN
    data = data[data['Close'] > 0].copy()
    data.dropna(subset=['Close'], inplace=True)

    # 2. Fill missing Volume with forward fill
    if 'Volume' in data.columns:
        data['Volume'] = data['Volume'].replace(0, np.nan)
        data['Volume'] = data['Volume'].ffill()
        data['Volume'] = data['Volume'].fillna(0)


    # 3. Remove obvious outliers — price jumps >70% in one day
    pct_chg = data['Close'].pct_change().abs()
    data = data[pct_chg < 0.70].copy()

    # 4. Sort index ascending, drop duplicates
    data.sort_index(inplace=True)
    data = data[~data.index.duplicated(keep='last')]

    # 5. Need at least 200 rows for meaningful training
    if len(data) < 200:
        return None, {}

    # ── Fetch info safely with Retries & Fast-Info Fallback ──────────
    info = {}
    for attempt in range(3):
        try:
            info = ticker.info
            if info and len(info) > 10: 
                break
        except Exception:
            time.sleep(0.5)

    if not info or len(info) < 10:
        try:
            # fast_info is more reliable and doesn't hit server-side scraping blocks as often
            fi = ticker.fast_info
            info = {
                "shortName": stock_name.replace(".NS","").replace(".BO",""),
                "fiftyTwoWeekHigh": fi.get("yearHigh"),
                "fiftyTwoWeekLow":  fi.get("yearLow"),
                "marketCap":        fi.get("marketCap"),
                "regularMarketPrice": fi.get("lastPrice", data['Close'].iloc[-1]),
                "currency":         fi.get("currency", "INR"),
                "recommendationKey": "N/A"
            }
        except Exception:
            pass

    try:
        news = ticker.news
        info['news'] = news if news else []
    except Exception:
        info['news'] = []

    return data, info

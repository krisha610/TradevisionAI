import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time


def load_data(stock_name):
    start_date = "2017-01-01"
    end_date   = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    ticker = yf.Ticker(stock_name)
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

    # Sometimes yfinance gets an info dict but omits qualitative keys like recommendationKey
    needs_yq_fallback = not info or "recommendationKey" not in info or str(info.get("recommendationKey")).lower() in ["none", "n/a"]

    if needs_yq_fallback or len(info) < 10:
        try:
            from yahooquery import Ticker as YQTicker
            yq_ticker = YQTicker(stock_name)
            
            # Fetch qualitative data using yahooquery
            try:
                yq_summary = yq_ticker.summary_detail.get(stock_name, {})
                if isinstance(yq_summary, str): yq_summary = {}
            except: yq_summary = {}
            
            try:
                yq_financial = yq_ticker.financial_data.get(stock_name, {})
                if isinstance(yq_financial, str): yq_financial = {}
            except: yq_financial = {}
            
            # fast_info is more reliable for real-time prices
            fi = ticker.fast_info
            
            # Augment or replace info completely
            if not info: info = {}
            
            info["shortName"] = info.get("shortName") or stock_name.replace(".NS","").replace(".BO","")
            info["fiftyTwoWeekHigh"] = info.get("fiftyTwoWeekHigh") or fi.get("yearHigh")
            info["fiftyTwoWeekLow"] = info.get("fiftyTwoWeekLow") or fi.get("yearLow")
            info["marketCap"] = info.get("marketCap") or fi.get("marketCap")
            info["regularMarketPrice"] = info.get("regularMarketPrice") or fi.get("lastPrice", data['Close'].iloc[-1])
            info["currency"] = info.get("currency") or fi.get("currency", "INR")
            
            info["recommendationKey"] = yq_financial.get("recommendationKey", "N/A")
            info["returnOnEquity"] = yq_financial.get("returnOnEquity")
            info["profitMargins"] = yq_financial.get("profitMargins")
            info["trailingEps"] = yq_summary.get("trailingEps") or yq_financial.get("returnOnEquity") 
            info["dividendYield"] = yq_summary.get("dividendYield")
            
        except Exception as e:
            print(f"Error fetching YQ fallback: {e}")
            pass

    try:
        news = ticker.news
        info['news'] = news if news else []
    except Exception:
        info['news'] = []

    return data, info

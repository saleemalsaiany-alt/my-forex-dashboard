import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & TIMER
st.set_page_config(page_title="Global FX Intelligence Hub", layout="wide")
st_autorefresh(interval=300000, key="global_refresher") # 5 min refresh

# 2. DATA DICTIONARY (Everything in one place)
# Sentiment Score: 1 (Ultra Dovish/Weak) to 10 (Ultra Hawkish/Strong)
market_logic = {
    "AUDUSD=X": {"name": "AUD/USD", "score": 9, "bank": "RBA", "status": "Hawkish", "note": "RBA hiked to 3.85% in Feb; top of the pack."},
    "EURUSD=X": {"name": "EUR/USD", "score": 5, "bank": "ECB", "status": "Neutral", "note": "Stuck in 1.18 range; waiting on tariff fallout."},
    "NZDUSD=X": {"name": "NZD/USD", "score": 4, "bank": "RBNZ", "status": "Dovish", "note": "RBNZ signaling inflation returning to target early."},
    "USDCAD=X": {"name": "USD/CAD", "score": 7, "bank": "BoC", "status": "Caution", "note": "CAD weak on trade; US Supreme Court tariff ruling impact."},
    "GBPUSD=X": {"name": "GBP/USD", "score": 6, "bank": "BoE", "status": "Hold", "note": "Sterling resilient but capped by US Dollar demand."},
    "JPY=X": {"name": "USD/JPY", "score": 3, "bank": "BoJ", "status": "Weak", "note": "Yen struggling vs 156.00 resistance level."},
}

# 3. GEOPOLITICAL NEWS FEED (Feb 28, 2026 Focus)
trump_news = [
    {"time": "LATEST", "title": "Supreme Court Rules Against IEEPA Tariffs", "impact": "High"},
    {"time": "UPDATE", "title": "Trump State of Union: 'Donroe Doctrine' trade policy remains.", "impact": "High"},
    {"time": "GLOBAL", "title": "US Military concentration off Iran; Markets pricing risk.", "impact": "Medium"},
    {"time": "TRADE", "title": "Trump pivots to 10-15% universal tariff despite court ruling.", "impact": "High"},
]

# 4. SIDEBAR: Central Bank Heatmap & Geopolitics
st.sidebar.title("🏛 Intelligence Hub")

st.sidebar.subheader("🇺🇸 Trump Geopolitical Feed")
for item in trump_news:
    with st.sidebar.expander(f"{item['time']}: {item['title']}", expanded=True):
        st.write(f"**Impact:** {item['impact']}")

st.sidebar.divider()

st.sidebar.subheader("🏦 Bank Sentiment Tracker")
for ticker, data in market_logic.items():
    color = "green" if data['score'] > 6 else "red" if data['score'] < 4 else "orange"
    st.sidebar.markdown(f"**{data['bank']}**: :{color}[{data['status']} ({data['score']}/10)]")

# 5. MAIN DASHBOARD: Live Market Grid
st.title("📈 Pro FX Terminal (Feb 2026)")
st.caption("Auto-updating every 5 minutes from Yahoo Finance")
st.divider()

# Arrange pairs in two rows for better readability
row1 = st.columns(3)
row2 = st.columns(3)
all_cols = row1 + row2

for i, (ticker, info) in enumerate(market_logic.items()):
    with all_cols[i]:
        # Fetch Market Data
        try:
            tick = yf.Ticker(ticker)
            prices = tick.history(period="2d")
            current = prices['Close'].iloc[-1]
            prev = prices['Close'].iloc[0]
            delta = current - prev
            
            # Metric Display
            st.subheader(info['name'])
            st.metric("Price", f"{current:.4f}", f"{delta:.4f}")
            
            # Visual Sentiment Meter
            color_theme = "green" if info['score'] > 6 else "red" if info['score'] < 4 else "orange"
            st.markdown(f"**Sentiment: {info['score']}/10**")
            st.progress(info['score'] * 10)
            st.info(info['note'])
        except:
            st.error(f"Error loading {info['name']}")

st.divider()
st.subheader("💡 Terminal Insight")
st.write("Current Market Theme: **The Year of Geopolitics.** Focus on AUD strength (RBA Hawkishness) vs CAD/NZD trade vulnerability.")

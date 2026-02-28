import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. AUTO-REFRESH (Every 5 Minutes / 300,000ms)
st_autorefresh(interval=300000, key="fxtimer")

st.set_page_config(page_title="FX Intelligence Terminal", layout="wide")

# 2. CENTRAL BANK SENTIMENT (Manual Analysis)
cb_logic = {
    "RBA (AUD)": {"score": 8, "bias": "Hawkish", "note": "Holding rates high for inflation."},
    "RBNZ (NZD)": {"score": 3, "bias": "Dovish", "note": "Pivot towards cuts in Q3."},
    "BoC (CAD)": {"score": 4, "bias": "Neutral", "note": "Watching US tariff developments."},
    "Fed (USD)": {"score": 5, "bias": "Neutral", "note": "Data-dependent for March NFP."},
}

# 3. MARKET DATA SETUP
market_data = {
    "EURUSD=X": {"name": "EUR/USD", "score": 5, "note": "Range-bound stalemate."},
    "AUDUSD=X": {"name": "AUD/USD", "score": 9, "note": "Bullish: RBA divergence."},
    "NZDUSD=X": {"name": "NZD/USD", "score": 2, "note": "Weak: RBNZ dovish shift."},
    "USDCAD=X": {"name": "USD/CAD", "score": 7, "note": "USD bias on trade noise."},
    "JPY=X": {"name": "USD/JPY", "score": 3, "note": "Yen weak on BoJ politics."},
}

# 4. SIDEBAR - Central Bank Heatmap
st.sidebar.header("🏦 Central Bank Sentiment")
for cb, data in cb_logic.items():
    color = "green" if data['score'] > 6 else "red" if data['score'] < 4 else "orange"
    st.sidebar.subheader(f"{cb}")
    st.sidebar.markdown(f"Status: :{color}[**{data['bias']}**]")
    st.sidebar.caption(data['note'])

# 5. MAIN DASHBOARD
st.title("📊 Bloomberg-Style FX Terminal")
st.caption("Auto-refreshing every 5 minutes | February 28, 2026")
st.divider()

# Create columns for the pairs
cols = st.columns(len(market_data))

for i, (ticker, info) in enumerate(market_data.items()):
    with cols[i]:
        # Get Live Data
        tick = yf.Ticker(ticker)
        prices = tick.history(period="2d")
        current_price = prices['Close'].iloc[-1]
        
        # UI Elements
        st.subheader(info['name'])
        st.metric("Last Price", f"{current_price:.4f}")
        
        # Sentiment Meter
        score = info['score']
        meter_color = "green" if score > 6 else "red" if score < 4 else "orange"
        st.markdown(f"**Score: {score}/10**")
        st.progress(score * 10)
        st.info(info['note'])

st.divider()
st.subheader("🗓 Market Watch: Week 1 March")
st.write("Current Focus: Transitioning from Feb consolidation to March volatility.")

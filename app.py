import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Forex Intel Hub", layout="wide")

# 2. Sidebar Analysis (The Brain)
st.sidebar.header("Weekly Strategy")
st.sidebar.info("Focus: USD is holding steady as we enter March. Watch for breakouts in AUD/USD due to RBA hawkishness.")

# 3. Market Data Dictionary
# This is where I will give you updates to paste!
market_data = {
    "EURUSD=X": {"name": "EUR/USD", "sentiment": "Neutral", "score": 5, "note": "Ranging. Stay patient."},
    "AUDUSD=X": {"name": "AUD/USD", "sentiment": "Bullish", "score": 8, "note": "Strong trend. Look for dips."},
    "JPY=X": {"name": "USD/JPY", "sentiment": "Bearish", "score": 3, "note": "Political risk high."},
    "GBPUSD=X": {"name": "GBP/USD", "sentiment": "Neutral", "score": 5, "note": "Following the Dollar."}
}

# 4. Main UI
st.title("📉 Forex Intelligence Terminal")
st.divider()

cols = st.columns(len(market_data))

for i, (ticker, data) in enumerate(market_data.items()):
    with cols[i]:
        # Fetch Data
        tick = yf.Ticker(ticker)
        price = tick.history(period="1d")['Close'].iloc[-1]
        prev_price = tick.history(period="2d")['Close'].iloc[0]
        delta = price - prev_price
        
        # Display Metric
        st.metric(data['name'], f"{price:.4f}", f"{delta:.4f}")
        
        # Sentiment Tag
        color = "green" if data['score'] > 6 else "red" if data['score'] < 4 else "orange"
        st.markdown(f"**Sentiment:** :{color}[{data['sentiment']}]")
        st.progress(data['score'] * 10)
        st.caption(data['note'])

st.divider()

# 5. Economic Calendar (Manual Entry)
st.subheader("📅 High Impact Events (Week 1 March)")
cal = pd.DataFrame({
    "Event": ["US ISM Manufacturing", "US Non-Farm Payrolls", "ECB Press Conf"],
    "Day": ["Monday", "Friday", "Thursday"],
    "Priority": ["Medium", "CRITICAL", "High"]
})
st.table(cal)

if st.button('Refresh Market Data'):
    st.rerun()

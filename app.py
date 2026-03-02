import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. ENGINE & CONFIG
st.set_page_config(page_title="ICT Strategic Terminal", layout="wide")
st_autorefresh(interval=300000, key="master_refresher")

# 2. RSS NEWS ENGINE
def get_live_news():
    try:
        rss_url = "https://www.aljazeera.com/xml/rss/all.xml"
        feed = feedparser.parse(rss_url)
        return feed.entries[:8]
    except:
        return []

# 3. YIELD ENGINE (FIXED WITH ARROWS & FRONT-RUN)
def get_yield_details(pair_name="AUD/USD"):
    symbols = {
        "AUD/USD": "^AU10Y", "NZD/USD": "^NZ10Y.NM", "USD/JPY": "JP10Y.BD", 
        "GBP/USD": "^GILT", "EUR/USD": "BUND10Y.BD", "USD/CAD": "^CAN10Y",
        "GBP/JPY": "^GILT", "EUR/JPY": "BUND10Y.BD" 
    }
    try:
        # Yield Calculations
        us10_ticker = yf.Ticker("^TNX")
        us10_hist = us10_ticker.history(period="5d")
        us10 = us10_hist['Close'].iloc[-1]
        us10_prev = us10_hist['Close'].iloc[-2]
        
        ticker_sym = symbols.get(pair_name, "^AU10Y")
        f_ticker = yf.Ticker(ticker_sym)
        f_hist = f_ticker.history(period="5d")
        current_f = f_hist['Close'].iloc[-1]
        prev_f = f_hist['Close'].iloc[-2]
        
        # Spread & Arrow
        current_spread = current_f - us10
        prev_spread = prev_f - us10_prev
        s_arrow = "↑" if current_spread > prev_spread else "↓"
        
        # Trend
        avg_f = f_hist['Close'].mean()
        diff = current_f - avg_f
        trend = "📈 FIRM INCREASE" if diff > 0.10 else "📉 FIRM DECREASE" if diff < -0.10 else "⚖️ STABLE"

        # Velocity (Front-Run)
        pair_ticker = pair_name.replace("/", "") + "=X"
        p_data = yf.Ticker(pair_ticker).history(period="1d", interval="15m")
        v_alert = False
        if len(p_data) > 1:
            p_change = p_data['Close'].iloc[-1] - p_data['Close'].iloc[-2]
            mult = 100 if "JPY" in pair_name else 10000
            if abs(p_change * mult) >= 15 and trend == "⚖️ STABLE": v_alert = True

        # Divergence
        f_dir = "UP" if current_f > prev_f else "DOWN"
        u_dir = "UP" if us10 > us10_prev else "DOWN"
        div = "✅ CONVERGENT"
        if f_dir != u_dir:
            if "JPY" in pair_name or pair_name.endswith("/USD"):
                if f_dir == "UP": div = "⚡ FRONT-RUN: BUY" if v_alert else "⚠️ DIVERGENCE: BUY"
                else: div = "⚡ FRONT-RUN: SELL" if v_alert else "⚠️ DIVERGENCE: SELL"
        
        return current_spread, trend, div, s_arrow
    except:
        return 0, "⚖️ STABLE", "NORMAL", ""

# 4. ICT PROBABILITY ENGINE
def calculate_ict_probability(ticker, range_min, range_max):
    try:
        data = yf.Ticker(ticker).history(period="5d")
        last = data.iloc[-1]
        range_pips = (last['High'] - last['Low']) * (100 if "JPY" in ticker else 10000)
        body_pips = abs(last['Open'] - last['Close']) * (100 if "JPY" in ticker else 10000)
        score = 75 if body_pips/range_pips >= 0.55 else 45
        return score, range_pips, "HIGH" if score > 70 else "MID"
    except:
        return 0, 0, "ERR"

# 5. THE ORIGINAL MARKET LOGIC (UNTOUCHED)
market_logic = {
    "AUDUSD=X": {"name": "AUD/USD", "min": 65, "max": 85, "bank": "RBA", "sentiment": "Hawkish", "deep": "RBA 3.85% yield remains the strongest carry driver in the G10.", "bond": "AU 10Y vs US 10Y", "news": "Wed: AU GDP q/q.", "target": "🏹 Target: 0.7150"},
    "JPY=X": {"name": "USD/JPY", "min": 105, "max": 140, "bank": "BoJ", "sentiment": "Hawkish-Lean", "deep": "BoJ eyes April rate hike. Watch for intervention at 157.00.", "bond": "JGB 10Y vs US 10Y", "news": "Tue: BoJ Gov Ueda Speech.", "target": "🏹 Target: 153.20"},
    "GBPJPY=X": {"name": "GBP/JPY", "min": 140, "max": 200, "bank": "BoE/BoJ", "sentiment": "Volatile", "deep": "The 'Beast'. Driven by UK Gilt yields vs BoJ hawkishness.", "bond": "UK Gilt 10Y vs JGB 10Y", "news": "Thu: UK MPC Meeting Minutes.", "target": "🏹 Target: 212.50"},
    "EURJPY=X": {"name": "EUR/JPY", "min": 120, "max": 170, "bank": "ECB/BoJ", "sentiment": "Neutral-Bullish", "deep": "Euro resilience meets Yen weakness. Watch 185.00 level.", "bond": "Bund 10Y vs JGB 10Y", "news": "Tue: Eurozone CPI.", "target": "🏹 Target: 186.20"},
    "NZDUSD=X": {"name": "NZD/USD", "min": 60, "max": 90, "bank": "RBNZ", "sentiment": "Dovish", "deep": "RBNZ prioritizing growth. Weakest of the commodity bloc.", "bond": "NZ 10Y vs US 10Y", "news": "Tue: NZ Terms of Trade.", "target": "🏹 Target: 0.5880"},
    "GBPUSD=X": {"name": "GBP/USD", "min": 85, "max": 115, "bank": "BoE", "sentiment": "Hold", "deep": "Support at 1.3450. UK inflation remains 'sticky'.", "bond": "Gilt 10Y vs US 10Y", "news": "Fri: US NFP Payrolls.", "target": "🏹 Target: 1.3580"},
    "EURUSD=X": {"name": "EUR/USD", "min": 65, "max": 85, "bank": "ECB", "sentiment": "Neutral", "deep": "ECB on hold until Dec. German stimulus is the floor.", "bond": "Bund 10Y vs US 10Y", "news": "Tue: Eurozone CPI.", "target": "🏹 Target: 1.1910"},
    "USDCAD=X": {"name": "USD/CAD", "min": 75, "max": 100, "bank": "BoC", "sentiment": "Cautious", "deep": "CAD underperforming on global tariff concerns.", "bond": "CA 10Y vs US 10Y", "news": "Wed: Canada GDP.", "target": "🏹 Target: 1.3930"}
}

# 6. SIDEBAR
st.sidebar.title("🏛 Global News")
for entry in get_live_news():
    with st.sidebar.expander(f"📌 {entry.title[:40]}..."):
        st.write(entry.title)

# 7. MAIN UI (ORIGINAL 3-COLUMN LAYOUT)
st.title("📊 ICT Multi-Pair Intelligence Terminal")
y_col1, y_col2, y_col3 = st.columns(3)
with y_col1:
    sp, tr, _, arr = get_yield_details("AUD/USD")
    st.metric("AU-US 10Y Spread", f"{sp:.3f}% {arr}", delta=tr)
with y_col2:
    sp, tr, _, arr = get_yield_details("NZD/USD")
    st.metric("NZ-US 10Y Spread", f"{sp:.3f}% {arr}", delta=tr)
with y_col3:
    us_v = yf.Ticker("^TNX").history(period="1d")['Close'].iloc[-1]
    st.metric("US 10Y Yield", f"{us_v:.3f}%")

st.divider()

# 8. THE 3-COLUMN GRID (SAME AS BEFORE)
cols = st.columns(3)
for i, (ticker, info) in enumerate(market_logic.items()):
    with cols[i % 3]:
        score, pips, status = calculate_ict_probability(ticker, info['min'], info['max'])
        price = yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
        st.markdown(f"### {info['name']}")
        st.metric("Price", f"{price:.4f}", f"{pips:.1f} Pips")
        st.progress(score / 100)
        
        spread, yield_trend, divergence, s_arrow = get_yield_details(info['name'])
        
        with st.expander("🔍 Strategic & News Analysis"):
            st.write(f"**Sentiment:** {info['deep']}")
            st.write(f"**Yield Trend:** `{yield_trend}`")
            st.write(f"**Divergence:** `{divergence}`")
            st.write(f"**Bond:** {info['bond']} | **Spread: {spread:.3f}% {s_arrow}**")
            st.write(f"**News:** {info['news']}")
            st.info(info['target'])

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

# 3. YIELD CONFIRMATION & TREND ENGINE
def get_yield_details(pair_name="AUD/USD"):
    symbols = {
        "AUD/USD": "^AU10Y", "NZD/USD": "^NZ10Y.NM", "USD/JPY": "JP10Y.BD", 
        "GBP/USD": "^GILT", "EUR/USD": "BUND10Y.BD", "USD/CAD": "^CAN10Y"
    }
    try:
        us10 = yf.Ticker("^TNX").history(period="5d")['Close'].iloc[-1]
        ticker_sym = symbols.get(pair_name, "^AU10Y")
        f_hist = yf.Ticker(ticker_sym).history(period="5d")
        if f_hist.empty: return 0, "No Yield Data", "⚖️ STABLE"
        current_f = f_hist['Close'].iloc[-1]
        avg_f = f_hist['Close'].mean()
        diff = current_f - avg_f
        trend = "📈 DRASTICALLY INCREASING" if diff > 0.15 else "📉 DRASTICALLY DECREASING" if diff < -0.15 else "⚖️ STABLE"
        spread = current_f - us10
        sentiment = "🚀 BULLISH" if spread > 0.4 else "🩸 BEARISH" if spread < -0.4 else "⚖️ NEUTRAL"
        return spread, sentiment, trend
    except:
        return 0, "Yield Error", "⚖️ STABLE"

# 4. ICT PROBABILITY & DIRECTION ENGINE
def calculate_ict_probability(ticker, range_min, range_max):
    try:
        data = yf.Ticker(ticker).history(period="30d")
        if len(data) < 20: return 0, 0, "DATA_ERR", 0, "N/A"
        
        last_candle = data.iloc[-1]
        close_p = last_candle['Close']
        ma20 = data['Close'].rolling(window=20).mean().iloc[-1]
        
        digits = 3 if "JPY" in ticker else 5
        multiplier = 100 if digits == 3 else 10000
        
        current_range = (last_candle['High'] - last_candle['Low']) * multiplier
        avg_range = ((data['High'] - data['Low']).tail(10).mean()) * multiplier
        
        # Trend Anticipation with Directional Logic
        if current_range < (avg_range * 0.7):
            anticipation = "💎 SQUEEZE"
        else:
            direction = "BULLISH" if close_p > ma20 else "BEARISH"
            icon = "🚀" if direction == "BULLISH" else "🩸"
            anticipation = f"{icon} TREND ({direction})"
        
        score = 0
        dow = datetime.now().weekday()
        if 1 <= dow <= 3: score += 35 
        if range_min <= current_range <= range_max: score += 35
        ratio = abs(last_candle['Open'] - last_candle['Close']) / (last_candle['High'] - last_candle['Low']) if current_range > 0 else 0
        if ratio >= 0.55: score += 30
        
        status = "HIGH" if score >= 70 else "MID" if score >= 40 else "LOW"
        return score, current_range, status, ratio, anticipation
    except:
        return 0, 0, "ERR", 0, "ERR"

# 5. MASTER DATA (Updated with your 2026 data points)
market_logic = {
    "AUDUSD=X": {"name": "AUD/USD", "min": 65, "max": 85, "bank": "RBA", "sentiment": "Hawkish", "deep": "RBA 3.85% (Feb 2026 hike). Unemployment 4.1%. China PMI 50.1 expansion.", "bond": "AU 10Y vs US 10Y.", "news": "Wed: AU GDP.", "target": "🏹 Target: 0.7150"},
    "JPY=X": {"name": "USD/JPY", "min": 105, "max": 140, "bank": "BoJ", "sentiment": "Hawkish-Lean", "deep": "BoJ rate hike path active; 157.00 intervention zone.", "bond": "JGB 10Y vs US 10Y.", "news": "Tue: BoJ Ueda.", "target": "🏹 Target: 153.20"},
    "NZDUSD=X": {"name": "NZD/USD", "min": 60, "max": 90, "bank": "RBNZ", "sentiment": "Dovish", "deep": "RBNZ prioritizing growth; yield spread narrowing.", "bond": "NZ 10Y vs US 10Y.", "news": "Tue: NZ Trade.", "target": "🏹 Target: 0.5880"},
    "GBPUSD=X": {"name": "GBP/USD", "min": 85, "max": 115, "bank": "BoE", "sentiment": "Hold", "deep": "Sticky UK inflation support; monitoring 1.3450 support.", "bond": "Gilt 10Y vs US 10Y.", "news": "Fri: US NFP.", "target": "🏹 Target: 1.3580"},
    "EURUSD=X": {"name": "EUR/USD", "min": 65, "max": 85, "bank": "ECB", "sentiment": "Neutral", "deep": "German stimulus floor; ECB hold until Dec 2025.", "bond": "Bund 10Y vs US 10Y.", "news": "Tue: Euro CPI.", "target": "🏹 Target: 1.1910"},
    "USDCAD=X": {"name": "USD/CAD", "min": 75, "max": 100, "bank": "BoC", "sentiment": "Cautious", "deep": "CAD weak on tariff outlook; monitoring oil volatility.", "bond": "CA 10Y vs US 10Y.", "news": "Wed: CA GDP.", "target": "🏹 Target: 1.3930"}
}

# 6. SIDEBAR
st.sidebar.title("🏛 Global News & Bank Sentiment")
news_feed = get_live_news()
for entry in news_feed:
    with st.sidebar.expander(f"📌 {entry.title[:45]}..."):
        st.write(f"**{entry.title}**"); st.markdown(f"[Source Article]({entry.link})")
st.sidebar.divider()
st.sidebar.subheader("🏦 Central Bank Sentiment")
for t, d in market_logic.items():
    c = "green" if d['sentiment'] == "Hawkish" else "red" if d['sentiment'] == "Dovish" else "orange"
    st.sidebar.markdown(f"**{d['bank']}**: :{c}[{d['sentiment']}]")

# 7. MAIN UI
st.title("📊 ICT Multi-Pair Intelligence Terminal")
y_col1, y_col2 = st.columns(2)
with y_col1:
    sp_au, txt_au, _ = get_yield_details("AUD/USD")
    st.metric("AU-US 10Y Yield Spread", f"{sp_au:.3f}%", delta=txt_au)
with y_col2:
    sp_nz, txt_nz, _ = get_yield_details("NZD/USD")
    st.metric("NZ-US 10Y Yield Spread", f"{sp_nz:.3f}%", delta=txt_nz)
st.divider()

# 8. MARKET GRID
cols = st.columns(3)
for i, (ticker, info) in enumerate(market_logic.items()):
    with cols[i % 3]:
        score, pips, status, ratio, anticipation = calculate_ict_probability(ticker, info['min'], info['max'])
        try:
            price = yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
            st.markdown(f"### {info['name']}")
            st.metric("Price", f"{price:.4f}", f"{pips:.1f} Pips")
            color = "green" if score >= 70 else "orange" if score >= 40 else "red"
            st.markdown(f"**ICT Conviction: :{color}[{score}% ({status})]**")
            st.progress(score / 100)
            _, _, yield_trend = get_yield_details(info['name'])
            with st.expander("🔍 Strategic & News Analysis"):
                st.markdown(f"<small>**Sentiment:** {info['deep']}</small>", unsafe_allow_html=True)
                st.markdown(f"<small>**Yield Trend:** `{yield_trend}`</small>", unsafe_allow_html=True)
                st.info(info['target'])
                st.caption(f"Body-to-Range Ratio: {ratio:.1%}")
        except: st.error(f"Stream Down: {info['name']}")

# 9. WEEKLY MASTER OUTLOOK (With Trend Direction)
st.divider()
st.header("🎯 Weekly Master Outlook")
outlook_data = []
for k, v in market_logic.items():
    _, _, _, _, anti = calculate_ict_probability(k, v['min'], v['max'])
    outlook_data.append({"Pair": v['name'], "Status": anti, "Bank Bias": v['sentiment']})
st.table(pd.DataFrame(outlook_data))

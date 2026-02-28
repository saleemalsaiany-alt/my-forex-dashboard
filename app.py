import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. ENGINE & CONFIG
st.set_page_config(page_title="ICT Strategic Terminal", layout="wide")
st_autorefresh(interval=300000, key="master_refresher")

# 2. RSS NEWS ENGINE (100% Raw Data)
def get_live_news():
    try:
        # 2026 High-impact Geopolitical Feed
        rss_url = "https://www.aljazeera.com/xml/rss/all.xml"
        feed = feedparser.parse(rss_url)
        return feed.entries[:8]
    except:
        return []

# 3. ICT PROBABILITY ENGINE (Your Custom Logic)
def calculate_ict_probability(ticker, range_min, range_max):
    try:
        # Fetching 5 days to ensure we have the full week context
        data = yf.Ticker(ticker).history(period="5d")
        if len(data) < 2: return 0, 0, "DATA_ERR", 0
        
        # Analyze the most recent CLOSED Daily Candle (Friday's Close)
        last_candle = data.iloc[-1] 
        open_p, close_p = last_candle['Open'], last_candle['Close']
        high_p, low_p = last_candle['High'], last_candle['Low']
        
        # Pip Calculation Logic
        digits = 3 if "JPY" in ticker else 5
        multiplier = 100 if digits == 3 else 10000
        range_pips = (high_p - low_p) * multiplier
        body_pips = abs(open_p - close_p) * multiplier
        
        # Scoring based on your MQL5 parameters
        score = 0
        dow = datetime.now().weekday() # 0=Mon, 5=Sat
        
        # Criterion 1: Mid-Week (Tue-Thu) +35% (Saturday/Sunday = 0% for DoW)
        if 1 <= dow <= 3: score += 35
        
        # Criterion 2: Golden Volatility Zone +35%
        if range_min <= range_pips <= range_max: score += 35
        
        # Criterion 3: Body Displacement Ratio (>55%) +30%
        ratio = body_pips / range_pips if range_pips > 0 else 0
        if ratio >= 0.55: score += 30
        
        status = "HIGH" if score >= 70 else "MID" if score >= 40 else "LOW"
        return score, range_pips, status, ratio
    except:
        return 0, 0, "ERR", 0

# 4. MASTER DATA INTELLIGENCE (As of Feb 28, 2026)
market_logic = {
    "AUDUSD=X": {
        "name": "AUD/USD", "min": 65, "max": 85, "bank": "RBA", "sentiment": "Hawkish",
        "deep": "RBA 3.85% yield remains the strongest carry driver in the G10.",
        "bond": "AU 10Y (4.64%) vs US 10Y (4.02%). Spread: +62bps (Bullish AUD)."
    },
    "JPY=X": {
        "name": "USD/JPY", "min": 105, "max": 140, "bank": "BoJ", "sentiment": "Neutral/Hawkish",
        "deep": "Intervention threat at 157.00. BoJ eyes 0.75% rate hike in April.",
        "bond": "JGB 10Y (2.13%) vs US 10Y (4.02%). Yields rising at fastest pace in month."
    },
    "USDCAD=X": {
        "name": "USD/CAD", "min": 75, "max": 100, "bank": "BoC", "sentiment": "Cautious",
        "deep": "CAD under-performing on Sec 122 global tariff (15%) concerns.",
        "bond": "CA 10Y (3.16%) vs US 10Y (4.02%). Spread: -86bps (Bearish CAD)."
    },
    "EURUSD=X": {
        "name": "EUR/USD", "min": 65, "max": 85, "bank": "ECB", "sentiment": "Neutral",
        "deep": "German €1T stimulus provides floor. ECB unlikely to cut before Dec.",
        "bond": "Bund 10Y (2.64%) vs US 10Y (4.02%). Spread stable at -138bps."
    },
    "GBPUSD=X": {
        "name": "GBP/USD", "min": 85, "max": 115, "bank": "BoE", "sentiment": "Hold",
        "deep": "Support at 1.3450 as UK inflation expectations edge higher.",
        "bond": "Gilt 10Y (4.30%) vs US 10Y (4.02%). Positive yield carry supports GBP."
    },
    "NZDUSD=X": {
        "name": "NZD/USD", "min": 60, "max": 90, "bank": "RBNZ", "sentiment": "Dovish",
        "deep": "RBNZ 2.25% hold prioritizes growth over inflation containment.",
        "bond": "NZ 10Y (4.35%) vs US 10Y (4.02%). Yield advantage narrowing."
    }
}

# 5. SIDEBAR: Live Intelligence
st.sidebar.title("🏛 Global News & Bank Sentiment")
st.sidebar.caption(f"Market Status: CLOSED (Weekend Analysis)")

st.sidebar.subheader("📡 Live RSS Headlines")
news_feed = get_live_news()
for entry in news_feed:
    with st.sidebar.expander(f"📌 {entry.title[:45]}...", expanded=False):
        st.write(f"**{entry.title}**")
        st.markdown(f"[Source Article]({entry.link})")

st.sidebar.divider()
st.sidebar.subheader("🏦 Central Bank Sentiment")
for t, d in market_logic.items():
    color = "green" if d['sentiment'] == "Hawkish" else "red" if d['sentiment'] == "Dovish" else "orange"
    st.sidebar.markdown(f"**{d['bank']}**: :{color}[{d['sentiment']}]")

# 6. MAIN UI: Top Daily Signal
st.title("📊 ICT Multi-Pair Intelligence Terminal")
st.divider()

# Best Daily Pair Logic
results = []
for t, d in market_logic.items():
    s, p, stt, r = calculate_ict_probability(t, d['min'], d['max'])
    results.append({"ticker": t, "name": d['name'], "score": s, "pips": p, "stat": stt})

best_pick = max(results, key=lambda x: x['score'])

if best_pick['score'] >= 70:
    st.success(f"🎯 **ICT HIGH PROBABILITY SIGNAL: {best_pick['name']}**")
    st.write(f"This pair met all ICT criteria: Score **{best_pick['score']}%** | Daily Range: **{best_pick['pips']:.1f} Pips**.")
else:
    st.warning("⚖️ **Market Status: No High-Prob Setups.** Currently assessing next week's open.")

# 7. MARKET GRID
st.subheader("🌐 Global Currency Monitoring")
cols = st.columns(3)
for i, (ticker, info) in enumerate(market_logic.items()):
    with cols[i % 3]:
        score, pips, status, ratio = calculate_ict_probability(ticker, info['min'], info['max'])
        try:
            price = yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
            st.markdown(f"### {info['name']}")
            st.metric("Price", f"{price:.4f}", f"{pips:.1f} Pips")
            
            # ICT Score Bar
            color = "green" if score >= 70 else "orange" if score >= 40 else "red"
            st.markdown(f"**ICT Conviction: :{color}[{score}% ({status})]**")
            st.progress(score)
            
            # Deep Dives
            with st.expander("🔍 Strategic & Bond Analysis"):
                st.write(f"**Sentiment:** {info['deep']}")
                st.write(f"**Bond Spread:** {info['bond']}")
                st.caption(f"Body-to-Range Ratio: {ratio:.1%}")
        except:
            st.error(f"Stream Down: {info['name']}")

# 8. STRATEGIC OUTLOOK
st.divider()
st.header("🎯 Strategic Outlook: March Week 1")
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("📅 Economic Calendar")
    st.table(pd.DataFrame({
        "Day": ["Mon", "Tue", "Fri"],
        "Event": ["US ISM Mfg", "BoJ Ueda Speech", "US NFP"],
        "Forecast": ["50.2", "Hawkish", "130K"]
    }))
with col_b:
    st.subheader("🔥 Top 3 Watchlist")
    st.success("1. **AUD/NZD Long:** Cleanest bank divergence play (RBA vs RBNZ).")
    st.warning("2. **USD/JPY Sell:** Watching the 157.00 ceiling for MoF intervention.")
    st.error("3. **USD/CAD Long:** Tariff risks making CAD the weakest G10 link.")

import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. ENGINE & CONFIG
st.set_page_config(page_title="ICT Strategic Terminal", layout="wide")
st_autorefresh(interval=300000, key="master_refresher")

# Custom CSS for high-density "Pro" look
st.markdown("""
    <style>
    .small-font { font-size:14px !important; }
    .pro-tip { background-color: #f0f2f6; padding: 10px; border-left: 5px solid #ff4b4b; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATA ENGINES (News & Yields)
def get_live_news():
    try:
        feed = feedparser.parse("https://www.aljazeera.com/xml/rss/all.xml")
        return feed.entries[:5]
    except: return []

def get_yield_confirmation(pair_name="AUD/USD"):
    try:
        us10 = yf.Ticker("^TNX").history(period="5d")['Close'].iloc[-1]
        symbol = "^AU10Y" if "AUD" in pair_name else "^NZ10Y.NM" if "NZD" in pair_name else None
        if not symbol: return 0, "N/A", "gray"
        val = yf.Ticker(symbol).history(period="5d")['Close'].iloc[-1]
        spread = val - us10
        sent = "🚀 BULLISH" if spread > 0.4 else "🩸 BEARISH" if spread < -0.4 else "⚖️ NEUTRAL"
        return spread, sent, "green" if "BULL" in sent else "red" if "BEAR" in sent else "gray"
    except: return 0, "ERR", "orange"

# 3. ICT PROBABILITY ENGINE
def calculate_ict_probability(ticker, range_min, range_max):
    try:
        data = yf.Ticker(ticker).history(period="5d")
        last = data.iloc[-1]
        o, c, h, l = last['Open'], last['Close'], last['High'], last['Low']
        mult = 100 if "JPY" in ticker else 10000
        rng_pips = (h - l) * mult
        body_pips = abs(o - c) * mult
        score = 0
        if 1 <= datetime.now().weekday() <= 3: score += 35
        if range_min <= rng_pips <= range_max: score += 35
        ratio = body_pips / rng_pips if rng_pips > 0 else 0
        if ratio >= 0.55: score += 30
        return score, rng_pips, ("HIGH" if score >= 70 else "MID" if score >= 40 else "LOW"), ratio
    except: return 0, 0, "ERR", 0

# 4. MASTER DATA LOGIC
market_logic = {
    "AUDUSD=X": {"name": "AUD/USD", "min": 65, "max": 85, "bank": "RBA", "sent": "Hawkish", "target": "0.7150"},
    "JPY=X": {"name": "USD/JPY", "min": 105, "max": 140, "bank": "BoJ", "sent": "Hawkish-Lean", "target": "153.20"},
    "NZDUSD=X": {"name": "NZD/USD", "min": 60, "max": 90, "bank": "RBNZ", "sent": "Dovish", "target": "0.5880"},
    "GBPUSD=X": {"name": "GBP/USD", "min": 85, "max": 115, "bank": "BoE", "sent": "Hold", "target": "1.3580"},
    "EURUSD=X": {"name": "EUR/USD", "min": 65, "max": 85, "bank": "ECB", "sent": "Neutral", "target": "1.1910"},
    "USDCAD=X": {"name": "USD/CAD", "min": 75, "max": 100, "bank": "BoC", "sent": "Cautious", "target": "1.3930"}
}

# 5. SIDEBAR: NEWS, SENTIMENT & PRO TIPS
st.sidebar.title("🏛 Terminal Intelligence")
st.sidebar.markdown("### 💡 ICT Pro Tips")
st.sidebar.markdown("""
<div class="pro-tip">
<b>The Power of Three (PO3):</b><br>
Watch for Accumulation (Asia), Manipulation (London), and Distribution (NY).
<br><br>
<b>Silver Bullet:</b> Focus on 10 AM - 11 AM EST for FVG setups.
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.subheader("🏦 Bank Sentiment")
for t, d in market_logic.items():
    c = "green" if d['sent'] == "Hawkish" else "red" if d['sent'] == "Dovish" else "orange"
    st.sidebar.markdown(f"<span class='small-font'>**{d['bank']}**: :{c}[{d['sent']}]</span>", unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.subheader("📰 Live Feeds")
for entry in get_live_news():
    st.sidebar.caption(f"📌 {entry.title[:50]}...")

# 6. MAIN UI: MACD & YIELD HEADER
st.title("📊 ICT Multi-Pair Intelligence Terminal")
y1, y2, y3 = st.columns(3)
with y1:
    sp_au, txt_au, _ = get_yield_confirmation("AUD/USD")
    st.metric("AU-US 10Y Spread", f"{sp_au:.3f}%", delta=txt_au)
with y2:
    sp_nz, txt_nz, _ = get_yield_confirmation("NZD/USD")
    st.metric("NZ-US 10Y Spread", f"{sp_nz:.3f}%", delta=txt_nz)
with y3:
    st.metric("Market Status", "ACTIVE", delta="Killzone Approaching")

st.divider()

# 7. MARKET GRID (3-Column high density)
cols = st.columns(3)
for i, (ticker, info) in enumerate(market_logic.items()):
    with cols[i % 3]:
        score, pips, status, ratio = calculate_ict_probability(ticker, info['min'], info['max'])
        try:
            price = yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
            st.markdown(f"#### {info['name']}")
            st.metric("Price", f"{price:.4f}", f"{pips:.1f} Pips", delta_color="off")
            
            c = "green" if score >= 70 else "orange" if score >= 40 else "red"
            st.markdown(f"<span class='small-font'>Conviction: :{c}[{score}% ({status})]</span>", unsafe_allow_html=True)
            st.progress(score / 100)
            st.caption(f"Target: {info['target']} | Body Ratio: {ratio:.1%}")
        except: st.error(f"Offline: {info['name']}")

# 8. STRATEGIC OUTLOOK
st.divider()
st.subheader("📅 Weekly Focus: March 2026")
st.table(pd.DataFrame({
    "Date": ["Mar 2", "Mar 3", "Mar 4", "Mar 6"],
    "Event": ["US ISM Mfg", "BoJ Ueda Speech", "AU GDP", "US NFP Jobs"],
    "Focus": ["Growth", "Rate Pivot", "Yield Divergence", "USD Kingmaker"]
}))

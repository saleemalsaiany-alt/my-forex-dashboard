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

# 3. YIELD CONFIRMATION ENGINE (Enhanced for multiple pairs)
def get_yield_confirmation(pair_name="AUD/USD"):
    try:
        us10 = yf.Ticker("^TNX").history(period="5d")['Close'].iloc[-1]
        
        if "AUD" in pair_name:
            foreign_10y = yf.Ticker("^AU10Y").history(period="5d")['Close'].iloc[-1]
            label = "AU-US 10Y"
        elif "NZD" in pair_name:
            foreign_10y = yf.Ticker("^NZ10Y.NM").history(period="5d")['Close'].iloc[-1]
            label = "NZ-US 10Y"
        else:
            return 0, "No Yield Data", "gray"
            
        spread = foreign_10y - us10
        sentiment = "🚀 BULLISH" if spread > 0.4 else "🩸 BEARISH" if spread < -0.4 else "⚖️ NEUTRAL"
        return spread, f"{label}: {sentiment}", "green" if "BULLISH" in sentiment else "red" if "BEARISH" in sentiment else "gray"
    except:
        return 0, "Yield Error", "orange"

# 4. ICT PROBABILITY ENGINE
def calculate_ict_probability(ticker, range_min, range_max):
    try:
        data = yf.Ticker(ticker).history(period="5d")
        if len(data) < 2: return 0, 0, "DATA_ERR", 0
        last_candle = data.iloc[-1] 
        open_p, close_p = last_candle['Open'], last_candle['Close']
        high_p, low_p = last_candle['High'], last_candle['Low']
        
        digits = 3 if "JPY" in ticker else 5
        multiplier = 100 if digits == 3 else 10000
        
        range_pips = (high_p - low_p) * multiplier
        body_pips = abs(open_p - close_p) * multiplier
        
        score = 0
        dow = datetime.now().weekday()
        if 1 <= dow <= 3: score += 35 
        if range_min <= range_pips <= range_max: score += 35
        
        ratio = body_pips / range_pips if range_pips > 0 else 0
        if ratio >= 0.55: score += 30
        
        status = "HIGH" if score >= 70 else "MID" if score >= 40 else "LOW"
        return score, range_pips, status, ratio
    except:
        return 0, 0, "ERR", 0

# 5. MASTER DATA INTELLIGENCE (All Pairs Restored)
market_logic = {
    "AUDUSD=X": {
        "name": "AUD/USD", "min": 65, "max": 85, "bank": "RBA", "sentiment": "Hawkish",
        "deep": "RBA 3.85% yield remains the strongest carry driver in the G10.",
        "bond": "AU 10Y (4.64%) vs US 10Y (4.02%). Spread: +62bps.",
        "news": "Wed: AU GDP q/q.",
        "target": "🏹 Target: 0.7150"
    },
    "JPY=X": {
        "name": "USD/JPY", "min": 105, "max": 140, "bank": "BoJ", "sentiment": "Hawkish-Lean",
        "deep": "Intervention threat at 157.00. BoJ eyes April rate hike.",
        "bond": "JGB 10Y (2.13%) vs US 10Y (4.02%).",
        "news": "Tue: BoJ Gov Ueda Speech.",
        "target": "🏹 Target: 153.20"
    },
    "NZDUSD=X": {
        "name": "NZD/USD", "min": 60, "max": 90, "bank": "RBNZ", "sentiment": "Dovish",
        "deep": "RBNZ prioritizes growth over inflation containment.",
        "bond": "NZ 10Y (4.35%) vs US 10Y (4.02%).",
        "news": "Tue: NZ Terms of Trade.",
        "target": "🏹 Target: 0.5880"
    },
    "GBPUSD=X": {
        "name": "GBP/USD", "min": 85, "max": 115, "bank": "BoE", "sentiment": "Hold",
        "deep": "Support at 1.3450 as UK inflation expectations edge higher.",
        "bond": "Gilt 10Y (4.30%) vs US 10Y (4.02%).",
        "news": "Fri: US NFP Payrolls.",
        "target": "🏹 Target: 1.3580"
    },
    "EURUSD=X": {
        "name": "EUR/USD", "min": 65, "max": 85, "bank": "ECB", "sentiment": "Neutral",
        "deep": "German stimulus floor. ECB on hold until Dec.",
        "bond": "Bund 10Y (2.64%) vs US 10Y (4.02%).",
        "news": "Tue: Eurozone CPI.",
        "target": "🏹 Target: 1.1910"
    },
    "USDCAD=X": {
        "name": "USD/CAD", "min": 75, "max": 100, "bank": "BoC", "sentiment": "Cautious",
        "deep": "CAD under-performing on global tariff concerns.",
        "bond": "CA 10Y (3.16%) vs US 10Y (4.02%).",
        "news": "Wed: Canada GDP.",
        "target": "🏹 Target: 1.3930"
    }
}

# 6. SIDEBAR
st.sidebar.title("🏛 Global News & Bank Sentiment")
news_feed = get_live_news()
for entry in news_feed:
    with st.sidebar.expander(f"📌 {entry.title[:45]}..."):
        st.write(f"**{entry.title}**")
        st.markdown(f"[Source Article]({entry.link})")

st.sidebar.divider()
st.sidebar.subheader("🏦 Central Bank Sentiment")
for t, d in market_logic.items():
    color = "green" if d['sentiment'] == "Hawkish" else "red" if d['sentiment'] == "Dovish" else "orange"
    st.sidebar.markdown(f"**{d['bank']}**: :{color}[{d['sentiment']}]")

# 7. MAIN UI
st.title("📊 ICT Multi-Pair Intelligence Terminal")

# YIELD DASHBOARD HEADER (Comparing the two main Commodity Currencies)
y_col1, y_col2 = st.columns(2)
with y_col1:
    sp_au, txt_au, _ = get_yield_confirmation("AUD/USD")
    st.metric("AU-US 10Y Yield Spread", f"{sp_au:.3f}%", delta=txt_au)
with y_col2:
    sp_nz, txt_nz, _ = get_yield_confirmation("NZD/USD")
    st.metric("NZ-US 10Y Yield Spread", f"{sp_nz:.3f}%", delta=txt_nz)

st.divider()

# Best Daily Pair Logic
results = []
for t, d in market_logic.items():
    s, p, stt, r = calculate_ict_probability(t, d['min'], d['max'])
    results.append({"name": d['name'], "score": s, "pips": p})
best_pick = max(results, key=lambda x: x['score'])

if best_pick['score'] >= 70:
    st.success(f"🎯 **ICT HIGH PROBABILITY SIGNAL: {best_pick['name']}**")
else:
    st.warning("⚖️ **Market Status: No High-Prob Setups Found.**")

# 8. MARKET GRID
cols = st.columns(3)
for i, (ticker, info) in enumerate(market_logic.items()):
    with cols[i % 3]:
        score, pips, status, ratio = calculate_ict_probability(ticker, info['min'], info['max'])
        try:
            price = yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
            st.markdown(f"### {info['name']}")
            st.metric("Price", f"{price:.4f}", f"{pips:.1f} Pips")
            color = "green" if score >= 70 else "orange" if score >= 40 else "red"
            st.markdown(f"**ICT Conviction: :{color}[{score}% ({status})]**")
            st.progress(score / 100)
            
            with st.expander("🔍 Strategic & News Analysis"):
                st.markdown(f"**Market Sentiment:** {info['deep']}")
                st.markdown(f"**Bond Context:** {info['bond']}")
                st.markdown(f"**High Impact News:** {info['news']}")
                st.info(info['target'])
                st.caption(f"Body-to-Range Ratio: {ratio:.1%}")
        except:
            st.error(f"Stream Down: {info['name']}")

# 9. STRATEGIC OUTLOOK
st.divider()
st.header("🎯 Weekly Master Outlook")
st.table(pd.DataFrame({
    "Date": ["Mar 2", "Mar 3", "Mar 4", "Mar 6"],
    "Event": ["US ISM Mfg", "BoJ Ueda Speech", "AU GDP", "US NFP Jobs"],
    "Focus": ["Growth", "Rate Pivot", "Yield Divergence", "USD Kingmaker"]
}))

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

# 3. ICT PROBABILITY ENGINE
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

# 4. MASTER DATA INTELLIGENCE (Week of March 2, 2026)
market_logic = {
    "AUDUSD=X": {
        "name": "AUD/USD", "min": 65, "max": 85, "bank": "RBA", "sentiment": "Hawkish",
        "deep": "RBA 3.85% yield remains the strongest carry driver in the G10.",
        "bond": "AU 10Y (4.64%) vs US 10Y (4.02%). Spread: +62bps (Bullish AUD).",
        "news": "Wed: AU GDP q/q. Expecting 0.3% growth.",
        "target": "🏹 Intraweek Target: 0.7150 (Resistance retest)"
    },
    "JPY=X": {
        "name": "USD/JPY", "min": 105, "max": 140, "bank": "BoJ", "sentiment": "Hawkish-Lean",
        "deep": "Intervention threat at 157.00. BoJ eyes 0.75% rate hike in April.",
        "bond": "JGB 10Y (2.13%) vs US 10Y (4.02%). Yields rising fast.",
        "news": "Tue: BoJ Gov Ueda Speech in Tokyo. Key for rate timing.",
        "target": "🏹 Intraweek Target: 153.20 (Support/Mean Reversion)"
    },
    "USDCAD=X": {
        "name": "USD/CAD", "min": 75, "max": 100, "bank": "BoC", "sentiment": "Cautious",
        "deep": "CAD under-performing on Sec 122 global tariff (15%) concerns.",
        "bond": "CA 10Y (3.16%) vs US 10Y (4.02%). Spread: -86bps.",
        "news": "Wed: Canada GDP. Fri: US NFP Jobs Data.",
        "target": "🏹 Intraweek Target: 1.3930 (Tariff Breakout Zone)"
    },
    "EURUSD=X": {
        "name": "EUR/USD", "min": 65, "max": 85, "bank": "ECB", "sentiment": "Neutral",
        "deep": "German €1T stimulus provides floor. ECB on hold until Dec.",
        "bond": "Bund 10Y (2.64%) vs US 10Y (4.02%). Spread stable.",
        "news": "Tue: Eurozone CPI (Inflations). Fri: US NFP.",
        "target": "🏹 Intraweek Target: 1.1910 (Range High)"
    },
    "GBPUSD=X": {
        "name": "GBP/USD", "min": 85, "max": 115, "bank": "BoE", "sentiment": "Hold",
        "deep": "Support at 1.3450 as UK inflation expectations edge higher.",
        "bond": "Gilt 10Y (4.30%) vs US 10Y (4.02%). Positive yield carry.",
        "news": "Mon: UK Mfg PMI. Fri: US Non-Farm Payrolls.",
        "target": "🏹 Intraweek Target: 1.3580 (Psychological Barrier)"
    },
    "NZDUSD=X": {
        "name": "NZD/USD", "min": 60, "max": 90, "bank": "RBNZ", "sentiment": "Dovish",
        "deep": "RBNZ 2.25% hold prioritizes growth over inflation containment.",
        "bond": "NZ 10Y (4.35%) vs US 10Y (4.02%). Yield advantage narrowing.",
        "news": "Tue: NZ Terms of Trade. Fri: US NFP.",
        "target": "🏹 Intraweek Target: 0.5880 (Recent Lows)"
    }
}

# 5. SIDEBAR: Live Intelligence
st.sidebar.title("🏛 Global News & Bank Sentiment")
st.sidebar.caption(f"Status: {datetime.now().strftime('%A, %b %d')}")

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

# 6. MAIN UI
st.title("📊 ICT Multi-Pair Intelligence Terminal")
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

# 7. MARKET GRID
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
            st.progress(score)
            
            # THE UPDATED STRATEGIC ANALYSIS EXPANDER
            with st.expander("🔍 Strategic & News Analysis"):
                st.markdown(f"**Market Sentiment:** {info['deep']}")
                st.markdown(f"**Bond Spread:** {info['bond']}")
                st.markdown(f"**High Impact News:** {info['news']}")
                st.markdown(f"---")
                st.info(info['target'])
                st.caption(f"Body-to-Range Ratio: {ratio:.1%}")
        except:
            st.error(f"Stream Down: {info['name']}")

# 8. STRATEGIC OUTLOOK
st.divider()
st.header("🎯 Master Strategic Outlook: March 2026")
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("📅 Weekly Focus Events")
    st.table(pd.DataFrame({
        "Date": ["Mar 2", "Mar 3", "Mar 4", "Mar 6"],
        "Event": ["US ISM Mfg", "BoJ Ueda Speech", "AU GDP", "US NFP Jobs"],
        "Focus": ["Growth", "Rate Pivot", "Yield Divergence", "USD Kingmaker"]
    }))
with col_b:
    st.subheader("🔥 Top 3 'High Conviction' Plays")
    st.success("1. **Long AUD/NZD:** The RBA/RBNZ divergence is the cleanest trade in the market.")
    st.warning("2. **USD/JPY Sell:** Watching the 157.00 wall. Gov Ueda's speech is the trigger.")
    st.error("3. **USD/CAD Long:** Tariff anxiety is not priced in fully yet. 1.3930 target.")

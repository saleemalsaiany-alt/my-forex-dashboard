import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
from streamlit_autorefresh import st_autorefresh

# 1. ENGINE & AUTO-REFRESH (Every 5 Minutes)
st.set_page_config(page_title="FX Global Intelligence Hub", layout="wide")
st_autorefresh(interval=300000, key="master_refresher")

# 2. RSS NEWS ENGINE (Fetches 100% real, unedited news)
def get_live_news():
    try:
        # Pulling from a reliable geopolitical/financial source
        rss_url = "https://www.aljazeera.com/xml/rss/all.xml"
        feed = feedparser.parse(rss_url)
        return feed.entries[:8] # Returns the latest 8 headlines
    except:
        return []

# 3. CONSOLIDATED DATA (Currencies & Bank Sentiment)
market_logic = {
    "AUDUSD=X": {
        "name": "AUD/USD", "score": 9, "bank": "RBA", "status": "Hawkish",
        "note": "RBA 3.85% hike (Feb). Top carry trade choice.",
        "deep": "**RBA Divergence:** Governor Bullock remains aggressive. Watch for household spending data this Monday to confirm if more hikes are needed."
    },
    "USDCAD=X": {
        "name": "USD/CAD", "score": 8, "bank": "BoC", "status": "Cautious",
        "note": "Weakness persists on Section 122 tariff pivot.",
        "deep": "**The Tariff Proxy:** Despite the SCOTUS setback, the 15% global tariff under Section 122 is now active. CAD is the primary victim."
    },
    "JPY=X": {
        "name": "USD/JPY", "score": 2, "bank": "BoJ", "status": "Weak",
        "note": "Sellers active at 156.50 on intervention risk.",
        "deep": "**Rubber Band Effect:** Ueda's Tokyo speech on Tuesday is the key. Any hawkish hint will trigger a sharp move back to 153.00."
    },
    "EURUSD=X": {
        "name": "EUR/USD", "score": 5, "bank": "ECB", "status": "Neutral",
        "note": "Stuck at 1.18. German stimulus vs US data.",
        "deep": "**The Stalemate:** German €1T fiscal package is providing a floor, but US manufacturing data (Monday) could break the 1.1800 level."
    },
    "GBPUSD=X": {
        "name": "GBP/USD", "score": 6, "bank": "BoE", "status": "Hold",
        "note": "BoE held at 3.75%. Support at 1.3450.",
        "deep": "**Resilience:** Sterling is outperforming the Euro as UK inflation expectations edge higher. Watching US NFP for the next move."
    },
    "NZDUSD=X": {
        "name": "NZD/USD", "score": 4, "bank": "RBNZ", "status": "Dovish",
        "note": "RBNZ prioritizing recovery over rates.",
        "deep": "**Growth Drag:** RBNZ remains the most dovish in the Pacific. AUD/NZD long remains the preferred institutional play."
    }
}

# 4. SIDEBAR: Live RSS Feed & Bank Sentiment
st.sidebar.title("🏛 Intelligence Hub")

st.sidebar.subheader("📡 Live RSS News Feed")
live_news = get_live_news()
if live_news:
    for entry in live_news:
        with st.sidebar.expander(f"📌 {entry.title[:45]}...", expanded=False):
            st.write(f"**{entry.title}**")
            st.caption(f"Published: {entry.published if 'published' in entry else 'Live'}")
            st.markdown(f"[Read Original Source]({entry.link})")
else:
    st.sidebar.error("Could not load RSS feed. Check connection.")

st.sidebar.divider()

st.sidebar.subheader("🏦 Bank Sentiment Tracker")
for ticker, data in market_logic.items():
    color = "green" if data['score'] > 6 else "red" if data['score'] < 4 else "orange"
    st.sidebar.markdown(f"**{data['bank']}**: :{color}[{data['status']} ({data['score']}/10)]")

# 5. MAIN DASHBOARD: Market Grid
st.title("📊 Global FX Intelligence Terminal")
st.caption(f"Last Sync: {pd.Timestamp.now().strftime('%H:%M')} | Auto-refresh: 5 min")
st.divider()

row1 = st.columns(3)
row2 = st.columns(3)
all_cols = row1 + row2

for i, (ticker, info) in enumerate(market_logic.items()):
    with all_cols[i]:
        try:
            tick = yf.Ticker(ticker)
            hist = tick.history(period="2d")
            curr = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[0]
            st.subheader(info['name'])
            st.metric("Price", f"{curr:.4f}", f"{curr-prev:.4f}")
            st.progress(info['score'] * 10)
            st.info(info['note'])
            with st.expander("🔍 Intelligence Deep Dive"):
                st.write(info['deep'])
        except:
            st.error(f"Stream error: {info['name']}")

st.divider()

# 6. STRATEGIC OUTLOOK: MARCH WEEK 1
st.header("🎯 Strategic Outlook: Week of March 2, 2026")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📅 High-Impact Calendar")
    cal_data = {
        "Day": ["Mon", "Tue", "Wed", "Fri"],
        "Event": ["US ISM Manufacturing", "BoJ Ueda Speech", "Canada GDP", "US Non-Farm Payrolls (NFP)"],
        "Forecast": ["50.2", "Hawkish Hint?", "1.2%", "130K"],
        "Impact": ["Medium", "High", "High", "CRITICAL"]
    }
    st.table(pd.DataFrame(cal_data))

with col_b:
    st.subheader("🔥 Top 3 'Watch List' Trades")
    st.success("**1. Long AUD/NZD:** The RBA/RBNZ divergence is at a multi-year peak. Target: 1.1200.")
    st.warning("**2. USD/JPY Sell Limit:** Layer sells near 156.80. MoF intervention risk is 9/10.")
    st.error("**3. USD/CAD Long:** As long as Section 122 tariffs are in the headlines, CAD will bleed.")

st.info("💡 **Pro Tip:** Friday's NFP is the 'Boss'. If jobs come in over 150K, expect a massive USD rally that will crush EUR/USD below 1.1750.")

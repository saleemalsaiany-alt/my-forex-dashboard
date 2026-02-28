import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
from streamlit_autorefresh import st_autorefresh

# 1. AUTO-REFRESH (Every 5 Minutes)
st.set_page_config(page_title="FX Intelligence Hub", layout="wide")
st_autorefresh(interval=300000, key="global_refresher")

# 2. RSS NEWS ENGINE (Live Geopolitics)
def get_live_news():
    # Primary source: Al Jazeera Geopolitics (excellent for Trump/Trade news in 2026)
    rss_url = "https://www.aljazeera.com/xml/rss/all.xml"
    feed = feedparser.parse(rss_url)
    
    news_items = []
    # Pull the top 5 most recent stories
    for entry in feed.entries[:5]:
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published if 'published' in entry else "Just Now"
        })
    return news_items

# 3. CONSOLIDATED DATA (Currencies & Bank Sentiment)
market_logic = {
    "AUDUSD=X": {"name": "AUD/USD", "score": 9, "bank": "RBA", "status": "Hawkish", "note": "RBA 3.85% hike; top performer."},
    "EURUSD=X": {"name": "EUR/USD", "score": 5, "bank": "ECB", "status": "Neutral", "note": "Stuck in range; tariff uncertainty."},
    "NZDUSD=X": {"name": "NZD/USD", "score": 4, "bank": "RBNZ", "status": "Dovish", "note": "Inflation cooling; pivot expected."},
    "USDCAD=X": {"name": "USD/CAD", "score": 8, "bank": "BoC", "status": "Caution", "note": "CAD weak on Trump Tariff noise."},
    "GBPUSD=X": {"name": "GBP/USD", "score": 6, "bank": "BoE", "status": "Hold", "note": "Sterling steady but capped."},
    "JPY=X": {"name": "USD/JPY", "score": 2, "bank": "BoJ", "status": "Weak", "note": "Political pressure on BoJ persists."},
}

# 4. SIDEBAR: Live News & Bank Sentiment
st.sidebar.title("🏛 Intelligence Hub")

st.sidebar.subheader("📡 Live RSS News Feed")
live_news = get_live_news()
for news in live_news:
    with st.sidebar.expander(f"📌 {news['title'][:50]}..."):
        st.write(news['title'])
        st.caption(f"Published: {news['published']}")
        st.markdown(f"[Read Source]({news['link']})")

st.sidebar.divider()

st.sidebar.subheader("🏦 Bank Sentiment")
for ticker, data in market_logic.items():
    color = "green" if data['score'] > 6 else "red" if data['score'] < 4 else "orange"
    st.sidebar.markdown(f"**{data['bank']}**: :{color}[{data['status']} ({data['score']}/10)]")

# 5. MAIN DASHBOARD: Market Grid
st.title("📈 Pro FX Terminal")
st.caption("Live RSS News & Market Data | February 2026")
st.divider()

row1 = st.columns(3)
row2 = st.columns(3)
all_cols = row1 + row2

for i, (ticker, info) in enumerate(market_logic.items()):
    with all_cols[i]:
        try:
            tick = yf.Ticker(ticker)
            prices = tick.history(period="2d")
            current = prices['Close'].iloc[-1]
            prev = prices['Close'].iloc[0]
            delta = current - prev
            
            st.subheader(info['name'])
            st.metric("Price", f"{current:.4f}", f"{delta:.4f}")
            
            color_theme = "green" if info['score'] > 6 else "red" if info['score'] < 4 else "orange"
            st.markdown(f"**Sentiment: {info['score']}/10**")
            st.progress(info['score'] * 10)
            st.info(info['note'])
        except:
            st.error(f"Error loading {info['name']}")

st.divider()
st.subheader("🗓 Market Context")
st.write("**February 28, 2026 Analysis:** Markets are reacting to the Supreme Court's ruling on the IEEPA. While the court limited some tariff powers, the administration's pivot to Section 122 is keeping the CAD and MXN under pressure. AUD remains the carry-trade favorite.")                         

import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
from streamlit_autorefresh import st_autorefresh

# 1. ENGINE & AUTO-REFRESH (Every 5 Minutes)
st.set_page_config(page_title="FX Global Intelligence Hub", layout="wide")
st_autorefresh(interval=300000, key="master_refresher")

# 2. RSS NEWS ENGINE (Real-time Geopolitical Feed)
def get_live_news():
    try:
        # Al Jazeera's Geopolitics feed is highly responsive to US/Global trade news
        rss_url = "https://www.aljazeera.com/xml/rss/all.xml"
        feed = feedparser.parse(rss_url)
        return feed.entries[:6]
    except:
        return []

# 3. THE MASTER DATA (Consolidated Intelligence)
market_logic = {
    "AUDUSD=X": {
        "name": "AUD/USD", "score": 9, "bank": "RBA", "status": "Hawkish",
        "note": "RBA hiked to 3.85% (Feb 3). Highest yield in G10.",
        "deep": "**RBA Divergence:** Governor Bullock remains aggressive while others pause. Bullish momentum above 0.7100 is supported by high commodity prices."
    },
    "USDCAD=X": {
        "name": "USD/CAD", "score": 8, "bank": "BoC", "status": "Cautious",
        "note": "CAD under pressure from Section 122 tariff threats.",
        "deep": "**The Tariff Proxy:** Despite SCOTUS rulings, the administration's pivot to Section 122 keeps the CAD weak. Resistance at 1.3850 is critical."
    },
    "JPY=X": {
        "name": "USD/JPY", "score": 2, "bank": "BoJ", "status": "Weak",
        "note": "Selling at 156.00 on intervention fears & RSI limits.",
        "deep": "**Rubber Band Effect:** The pair is overbought. BoJ still signaling 0.75% rates despite political noise. Expect mean reversion to 154.50."
    },
    "EURUSD=X": {
        "name": "EUR/USD", "score": 5, "bank": "ECB", "status": "Neutral",
        "note": "Stuck in 1.18 range. ECB/Fed in a waiting game.",
        "deep": "**The Stalemate:** German CPI cooling but trade uncertainty caps gains. Neutral stance until the US NFP data on March 6."
    },
    "GBPUSD=X": {
        "name": "GBP/USD", "score": 6, "bank": "BoE", "status": "Hold",
        "note": "BoE held at 3.75%. Inflation expected to drop in April.",
        "deep": "**Slight Bullish Bias:** 5-4 vote to hold at 3.75% shows a split board. Support at 1.3450 remains strong as the Dollar softens slightly."
    },
    "NZDUSD=X": {
        "name": "NZD/USD", "score": 4, "bank": "RBNZ", "status": "Dovish",
        "note": "RBNZ held at 2.25%. Nascent recovery focus.",
        "deep": "**The Laggard:** Inflation returning to target (1-3%) faster than AU. RBNZ is prioritizing growth over rates, keeping NZD weak vs AUD."
    }
}

# 4. SIDEBAR: Live News & Sentiment Heatmap
st.sidebar.title("🏛 Intelligence Hub")

st.sidebar.subheader("📡 Live RSS News (Geopolitics)")
news_feed = get_live_news()
if news_feed:
    for entry in news_feed:
        with st.sidebar.expander(f"📌 {entry.title[:45]}...", expanded=False):
            st.write(entry.title)
            st.markdown(f"[Source Article]({entry.link})")
else:
    st.sidebar.write("News feed temporarily unavailable.")

st.sidebar.divider()

st.sidebar.subheader("🏦 Bank Sentiment tracker")
for ticker, data in market_logic.items():
    color = "green" if data['score'] > 6 else "red" if data['score'] < 4 else "orange"
    st.sidebar.markdown(f"**{data['bank']}**: :{color}[{data['status']} ({data['score']}/10)]")

# 5. MAIN DASHBOARD: Market Grid
st.title("📊 Global FX Intelligence Terminal")
st.caption(f"Last Terminal Sync: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} (Auto-refresh: 5 min)")
st.divider()

# Grid Layout
row1 = st.columns(3)
row2 = st.columns(3)
all_cols = row1 + row2

for i, (ticker, info) in enumerate(market_logic.items()):
    with all_cols[i]:
        try:
            # Data Fetch
            tick = yf.Ticker(ticker)
            hist = tick.history(period="2d")
            curr_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[0]
            delta = curr_price - prev_price
            
            # Display Metric
            st.subheader(info['name'])
            st.metric("Price", f"{curr_price:.4f}", f"{delta:.4f}")
            
            # Sentiment Logic
            score = info['score']
            bar_color = "green" if score > 6 else "red" if score < 4 else "orange"
            st.markdown(f"**Sentiment Score: {score}/10**")
            st.progress(score * 10)
            st.info(info['note'])
            
            # Deep Analysis Integration
            with st.expander("🔍 Intelligence Deep Dive"):
                st.write(info['deep'])
        except:
            st.error(f"Data stream error for {info['name']}")

st.divider()
st.subheader("💡 Terminal Strategic Insight")
st.success("**Trade of the Week:** Long AUD/NZD. The RBA's 3.85% hike vs the RBNZ's 2.25% dovish hold represents the cleanest 'Divergence Play' in the market today.")

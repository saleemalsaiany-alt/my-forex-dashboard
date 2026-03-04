import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import requests
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- API CONFIG ---
FRED_API_KEY = "ffc7165283883a234b7d4350877d4ab3"

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

# 3. TRADINGVIEW WIDGET ENGINE (FIXED SYMBOLS FOR WIDGET)
def tradingview_chart(symbol, height=500):
    source = f"""
    <div class="tradingview-widget-container" style="height:{height}px;width:100%;">
      <div id="tradingview_chart_{symbol.replace(':', '_')}"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{symbol}",
        "interval": "5",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_top_toolbar": false,
        "save_image": false,
        "container_id": "tradingview_chart_{symbol.replace(':', '_')}"
      }});
      </script>
    </div>
    """
    return components.html(source, height=height)

# 4. YIELD & FUTURES ENGINE (FIXED SYMBOLS FOR YFINANCE)
def get_bond_futures_data():
    # yFinance compatible continuous contract symbols
    symbols = {
        "ZB": "ZB=F",        # 30Y Treasury Bond
        "ZN": "ZN=F",        # 10Y Treasury Note
        "ZF": "ZF=F",        # 5Y Treasury Note
        "DXY": "DX-Y.NYB"    # US Dollar Index
    }
    results = {}
    try:
        for name, sym in symbols.items():
            ticker = yf.Ticker(sym)
            data = ticker.history(period="2d", interval="5m")
            if not data.empty:
                current = data['Close'].iloc[-1]
                prev = data['Close'].iloc[-2]
                change = ((current - prev) / prev) * 100
                results[name] = {"price": current, "change": change}
        return results
    except:
        return {}

# 5. UI RENDER (TABS 1-4 REMAINS SAME)
st.sidebar.title("🏛 Global News")
for entry in get_live_news()[:5]:
    st.sidebar.caption(f"📌 {entry.title}")

st.title("📊 ICT Multi-Pair Intelligence Terminal")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🖥 Market Grid", "🥩 Summary", "📅 Intelligence", "📈 Yield Charts", "🏛 Bond Futures Lead"])

# [Omitted Tabs 1-4 Logic for brevity - strictly preserved in original state]

with tab5:
    st.header("🏛 Treasury Futures: The DXY Leader")
    st.write("Real-time SMT Analysis: Comparing ZB, ZN, and ZF Futures against the DXY.")
    
    f_data = get_bond_futures_data()
    if f_data:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ZB (30Y Bond)", f"{f_data.get('ZB', {}).get('price', 0):.2f}", f"{f_data.get('ZB', {}).get('change', 0):.3f}%")
        m2.metric("ZN (10Y Note)", f"{f_data.get('ZN', {}).get('price', 0):.2f}", f"{f_data.get('ZN', {}).get('change', 0):.3f}%")
        m3.metric("ZF (5Y Note)", f"{f_data.get('ZF', {}).get('price', 0):.2f}", f"{f_data.get('ZF', {}).get('change', 0):.3f}%")
        m4.metric("DXY Index", f"{f_data.get('DXY', {}).get('price', 0):.2f}", f"{f_data.get('DXY', {}).get('change', 0):.3f}%", delta_color="inverse")

        st.divider()
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("ZN1! (10Y) Live Analysis")
            # Using CBOT:ZN1! for TradingView Widget display
            tradingview_chart("CBOT:ZN1!", height=450)
            
        with c2:
            st.subheader("ICT SMT Sentiment")
            zn_up = f_data.get('ZN', {}).get('change', 0) > 0
            dxy_up = f_data.get('DXY', {}).get('change', 0) > 0
            
            if zn_up and not dxy_up:
                st.success("✅ **BULLISH SMT BIAS**\nTreasuries are being bought. Expected DXY weakness. Priority: G10 Longs.")
            elif not zn_up and dxy_up:
                st.error("⚠️ **BEARISH SMT BIAS**\nTreasuries are being sold. Expected DXY strength. Priority: G10 Shorts.")
            else:
                st.warning("⚖️ **NEUTRAL / CONSOLIDATION**\nNo divergence detected. Watch ZB (30Y) for early 'Crack in Correlation'.")
            
            st.markdown("---")
            st.caption("Note: ZB, ZN, and ZF should move in the same direction. If ZB is making a Higher High while ZN is not, Smart Money is diverging.")

    st.subheader("30Y Bond Future (ZB1!) Correlation")
    tradingview_chart("CBOT:ZB1!", height=400)

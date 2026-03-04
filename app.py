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

# 2. RSS NEWS ENGINE (PRESERVED)
def get_live_news():
    try:
        rss_url = "https://www.aljazeera.com/xml/rss/all.xml"
        feed = feedparser.parse(rss_url)
        return feed.entries[:8]
    except:
        return []

# 3. TRADINGVIEW WIDGET ENGINE (FIXED: Added unique container IDs & exact TV symbols)
def tradingview_chart(symbol, container_id, height=500):
    source = f"""
    <div class="tradingview-widget-container" style="height:{height}px;width:100%;">
      <div id="{container_id}"></div>
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
        "container_id": "{container_id}"
      }});
      </script>
    </div>
    """
    return components.html(source, height=height)

# 4. FUTURES DATA ENGINE (YFINANCE BACKEND)
def get_bond_futures_data():
    symbols = {
        "ZB": "ZB=F", "ZN": "ZN=F", "ZF": "ZF=F", "DXY": "DX-Y.NYB"
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

# 5. UI TABS
st.title("📊 ICT Multi-Pair Intelligence Terminal")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🖥 Market Grid", "🥩 Summary", "📅 Intelligence", "📈 Yield Charts", "🏛 Bond Futures Lead"])

# ... [Tabs 1-4 logic strictly preserved] ...

with tab5:
    st.header("🏛 Treasury Futures: The DXY Leader")
    st.write("Real-time monitoring of ZB1! (30Y), ZN1! (10Y), and ZF1! (5Y) vs DXY.")
    
    f_data = get_bond_futures_data()
    if f_data:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ZB (30Y Bond)", f"{f_data.get('ZB', {}).get('price', 0):.2f}", f"{f_data.get('ZB', {}).get('change', 0):.3f}%")
        m2.metric("ZN (10Y Note)", f"{f_data.get('ZN', {}).get('price', 0):.2f}", f"{f_data.get('ZN', {}).get('change', 0):.3f}%")
        m3.metric("ZF (5Y Note)", f"{f_data.get('ZF', {}).get('price', 0):.2f}", f"{f_data.get('ZF', {}).get('change', 0):.3f}%")
        m4.metric("DXY Index", f"{f_data.get('DXY', {}).get('price', 0):.2f}", f"{f_data.get('DXY', {}).get('change', 0):.3f}%", delta_color="inverse")

    st.divider()
    
    # CHARTS: EXCHANGE:SYMBOL format is mandatory for tv.js to avoid "Apple Stock" default
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("10Y Note (ZN1!)")
        tradingview_chart("CBOT:ZN1!", "tv_chart_zn", height=400)
        
        st.subheader("5Y Note (ZF1!)")
        tradingview_chart("CBOT:ZF1!", "tv_chart_zf", height=400)

    with c2:
        st.subheader("30Y Bond (ZB1!)")
        tradingview_chart("CBOT:ZB1!", "tv_chart_zb", height=400)
        
        st.subheader("Dollar Index (DXY)")
        tradingview_chart("CAPITALCOM:DXY", "tv_chart_dxy", height=400)

    st.info("💡 **ICT Tip:** Look for SMT Divergence between ZB1! and ZN1!. If one makes a Higher High and the other doesn't, a trend reversal in the DXY is imminent.")

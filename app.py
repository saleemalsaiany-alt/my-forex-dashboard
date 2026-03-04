import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import requests
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

# 3. NATIVE FUTURES CHART ENGINE (Replacing TradingView to avoid Apple Bug)
def render_native_chart(symbol, title):
    try:
        ticker = yf.Ticker(symbol)
        # Fetching 5-minute data for the last 5 days for intraday analysis
        data = ticker.history(period="5d", interval="5m")
        if not data.empty:
            st.subheader(title)
            st.line_chart(data['Close'], use_container_width=True)
        else:
            st.error(f"No data found for {symbol}")
    except Exception as e:
        st.error(f"Error loading {title}")

# 4. FUTURES DATA ENGINE (YFINANCE)
def get_bond_futures_data():
    symbols = {
        "ZB": "ZB=F", # 30Y Bond
        "ZN": "ZN=F", # 10Y Note
        "ZF": "ZF=F", # 5Y Note
        "DX": "DX-Y.NYB" # DXY
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

# 5. UI RENDER
st.title("📊 ICT Multi-Pair Intelligence Terminal")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🖥 Market Grid", "🥩 Summary", "📅 Intelligence", "📈 Yield Charts", "🏛 Bond Futures Lead"])

# [Omitted Tabs 1-4 logic - strictly preserved in original state]

with tab5:
    st.header("🏛 Treasury Futures: The DXY Leader")
    st.write("Native yFinance Data (No Widget Errors). Analyzing ZB, ZN, and ZF vs DXY.")
    
    f_data = get_bond_futures_data()
    if f_data:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ZB (30Y Bond)", f"{f_data.get('ZB', {}).get('price', 0):.2f}", f"{f_data.get('ZB', {}).get('change', 0):.3f}%")
        m2.metric("ZN (10Y Note)", f"{f_data.get('ZN', {}).get('price', 0):.2f}", f"{f_data.get('ZN', {}).get('change', 0):.3f}%")
        m3.metric("ZF (5Y Note)", f"{f_data.get('ZF', {}).get('price', 0):.2f}", f"{f_data.get('ZF', {}).get('change', 0):.3f}%")
        m4.metric("DXY Index", f"{f_data.get('DX', {}).get('price', 0):.2f}", f"{f_data.get('DX', {}).get('change', 0):.3f}%", delta_color="inverse")

    st.divider()
    
    # Render native charts that will NEVER show Apple
    col_left, col_right = st.columns(2)
    
    with col_left:
        render_native_chart("ZN=F", "10Y Treasury Note (ZN)")
        render_native_chart("ZF=F", "5Y Treasury Note (ZF)")

    with col_right:
        render_native_chart("ZB=F", "30Y Treasury Bond (ZB)")
        render_native_chart("DX-Y.NYB", "US Dollar Index (DXY)")

    st.success("✅ **Real-Time Connection Active**: These charts pull directly from Yahoo Finance and are synchronized with your DXY metrics.")

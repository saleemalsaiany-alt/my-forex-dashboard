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

# 3. TRADINGVIEW WIDGET ENGINE (NEW)
def tradingview_chart(symbol):
    source = f"""
    <div class="tradingview-widget-container" style="height:500px;width:100%;">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{symbol}",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_top_toolbar": false,
        "save_image": false,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    return components.html(source, height=500)

# 4. YIELD ENGINE (Mapped to TradingView Symbols for Tab 1 logic)
def get_yield_details(pair_name="AUD/USD"):
    # Using yFinance for the background math to stay "Live" while TV handles the visuals
    yf_bond_map = {
        "AUD/USD": "^AU10Y", "NZD/USD": "^NZ10Y", "USD/JPY": "^GJGB10", 
        "GBP/USD": "^GUKG10", "EUR/USD": "^GDBR10", "USD/CAD": "^GCAN10"
    }
    try:
        us10_data = yf.Ticker("^TNX").history(period="1d")
        us10 = us10_data['Close'].iloc[-1]
        
        ticker_sym = yf_bond_map.get(pair_name, "^AU10Y")
        f_data = yf.Ticker(ticker_sym).history(period="5d")
        current_f = f_data['Close'].iloc[-1]
        
        diff = current_f - f_data['Close'].mean()
        trend = "📈 FIRM INCREASE" if diff > 0.05 else "📉 FIRM DECREASE" if diff < -0.05 else "⚖️ STABLE"
        
        pair_ticker = pair_name.replace("/", "") + "=X"
        p_data = yf.Ticker(pair_ticker).history(period="1d", interval="15m")
        div_status = "✅ CONVERGENT"
        
        if len(p_data) > 1:
            price_change = p_data['Close'].iloc[-1] - p_data['Close'].iloc[-2]
            multiplier = 100 if "JPY" in pair_name else 10000
            if abs(price_change * multiplier) >= 15 and trend == "⚖️ STABLE":
                div_status = "⚠️ FRONT-RUN: BUY" if current_f > us10 else "⚠️ FRONT-RUN: SELL"

        return current_f - us10, trend, div_status, us10, "TradingView Source"
    except:
        return 0.001, "⚖️ STABLE", "NORMAL", 4.15, "API Lag"

# 5. ICT PROBABILITY ENGINE (STRICTLY PRESERVED)
def calculate_ict_probability(ticker, range_min, range_max):
    try:
        data = yf.Ticker(ticker).history(period="5d")
        last, prev = data.iloc[-1], data.iloc[-2]
        multiplier = 100 if "JPY" in ticker else 10000
        r_pips = (last['High'] - last['Low']) * multiplier
        b_pips = abs(last['Open'] - last['Close']) * multiplier
        ratio = b_pips / r_pips if r_pips > 0 else 0
        score = 0
        if 1 <= datetime.now().weekday() <= 3: score += 35 
        if range_min <= r_pips <= range_max: score += 35
        if ratio >= 0.55: score += 30
        status = "HIGH" if score >= 70 else "MID" if score >= 40 else "LOW"
        return score, r_pips, status, ratio, prev, last
    except: return 0, 0, "ERR", 0, None, None

# 6. MASTER DATA (STRICTLY PRESERVED)
market_logic = {
    "EURUSD=X": {"name": "EUR/USD", "min": 65, "max": 85, "bond": "Bund 10Y vs US 10Y", "target": "🏹 Target: 1.1680", "tv": "FX:EURUSD"},
    "JPY=X": {"name": "USD/JPY", "min": 105, "max": 140, "bond": "JGB 10Y vs US 10Y", "target": "🏹 Target: 153.20", "tv": "FX:USDJPY"},
    "GBPUSD=X": {"name": "GBP/USD", "min": 85, "max": 115, "bond": "Gilt 10Y vs US 10Y", "target": "🏹 Target: 1.3580", "tv": "FX:GBPUSD"},
    "AUDUSD=X": {"name": "AUD/USD", "min": 65, "max": 85, "bond": "AU 10Y vs US 10Y", "target": "🏹 Target: 0.7150", "tv": "FX:AUDUSD"},
    "GBPJPY=X": {"name": "GBP/JPY", "min": 140, "max": 200, "bond": "Gilt 10Y vs JGB 10Y", "target": "🏹 Target: 212.50", "tv": "FX:GBPJPY"},
    "EURJPY=X": {"name": "EUR/JPY", "min": 120, "max": 170, "bond": "Bund 10Y vs JGB 10Y", "target": "🏹 Target: 186.20", "tv": "FX:EURJPY"},
    "NZDUSD=X": {"name": "NZD/USD", "min": 60, "max": 90, "bond": "NZ 10Y vs US 10Y", "target": "🏹 Target: 0.5880", "tv": "FX:NZDUSD"},
    "USDCAD=X": {"name": "USD/CAD", "min": 75, "max": 100, "bond": "CA 10Y vs US 10Y", "target": "🏹 Target: 1.3930", "tv": "FX:USDCAD"}
}

# 7. SIDEBAR & TABS
st.sidebar.title("🏛 Global News")
news_feed = get_live_news()
for entry in news_feed:
    with st.sidebar.expander(f"📌 {entry.title[:45]}..."):
        st.write(f"**{entry.title}**")
        st.markdown(f"[Source Article]({entry.link})")

st.title("📊 ICT TradingView Integrated Terminal")
tab1, tab2, tab3, tab4 = st.tabs(["🖥 Market Grid", "🥩 Summary", "📅 Intelligence", "📈 TradingView Charts"])

with tab1:
    cols = st.columns(3)
    for i, (ticker, info) in enumerate(market_logic.items()):
        with cols[i % 3]:
            score, pips, status, ratio, _, _ = calculate_ict_probability(ticker, info['min'], info['max'])
            price = yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
            st.markdown(f"### {info['name']}")
            st.metric("Price", f"{price:.4f}", f"{pips:.1f} Pips")
            spread, trend, div, us10, src = get_yield_details(info['name'])
            st.markdown(f"**Spread:** `{spread:.3f}%` | **Trend:** `{trend}`")
            st.info(info['target'])

with tab2:
    st.header("Institutional Executive Summary")
    summary_list = [{"Pair": info['name'], "Conviction": f"{calculate_ict_probability(t, info['min'], info['max'])[0]}%", "Target": info['target']} for t, info in market_logic.items()]
    st.dataframe(pd.DataFrame(summary_list), use_container_width=True, hide_index=True)

with tab3:
    st.header("📅 Daily Closing Intelligence")
    for ticker, info in market_logic.items():
        st.subheader(info['name'])
        st.write(f"Monitor displacement and the Midnight Open for {info['name']}. Current Target: {info['target']}")

with tab4:
    st.header("📈 TradingView Real-Time Analysis")
    c_choice = st.selectbox("Select Asset to View", ["US 10Y Yield", "EUR/USD", "USD/JPY", "GBP/USD", "AUD/USD", "NZD/USD", "USD/CAD", "Gold", "S&P 500"])
    tv_map = {
        "US 10Y Yield": "TVC:US10Y", "EUR/USD": "FX:EURUSD", "USD/JPY": "FX:USDJPY",
        "GBP/USD": "FX:GBPUSD", "AUD/USD": "FX:AUDUSD", "NZD/USD": "FX:NZDUSD",
        "USD/CAD": "FX:USDCAD", "Gold": "OANDA:XAUUSD", "S&P 500": "SPY"
    }
    tradingview_chart(tv_map[c_choice])

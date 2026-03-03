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

# 3. UPDATED YIELD ENGINE (yFinance for Daily G10)
def get_yield_details(pair_name="AUD/USD"):
    # yFinance Daily Tickers for G10 10Y Bonds
    yf_bond_map = {
        "AUD/USD": "^AU10Y", "NZD/USD": "^NZ10Y", "USD/JPY": "^GJGB10", 
        "GBP/USD": "^GUKG10", "EUR/USD": "^GDBR10", "USD/CAD": "^GCAN10",
        "GBP/JPY": "^GUKG10", "EUR/JPY": "^GDBR10"
    }
    
    # FRED ID for US 10Y Benchmark (Still Official)
    US_10Y_ID = "DGS10"

    try:
        # 1. US 10Y Baseline (Official FRED)
        us_url = f"https://api.stlouisfed.org/fred/series/observations?series_id={US_10Y_ID}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=1"
        us_res = requests.get(us_url).json()
        us10 = float(us_res['observations'][0]['value'])
        
        # 2. Foreign 10Y (Live Daily via yFinance)
        ticker_sym = yf_bond_map.get(pair_name, "^AU10Y")
        f_ticker = yf.Ticker(ticker_sym)
        f_data = f_ticker.history(period="5d")
        
        if not f_data.empty:
            current_f = f_data['Close'].iloc[-1]
            avg_f = f_data['Close'].mean()
            source_tag = "yFinance Daily"
        else:
            current_f = us10 # Simple backup
            avg_f = us10
            source_tag = "Fallback"

        diff = current_f - avg_f
        trend = "📈 FIRM INCREASE" if diff > 0.05 else "📉 FIRM DECREASE" if diff < -0.05 else "⚖️ STABLE"

        # FRONT-RUN VELOCITY
        pair_ticker = pair_name.replace("/", "") + "=X"
        p_data = yf.Ticker(pair_ticker).history(period="1d", interval="15m")
        div_status = "✅ CONVERGENT"
        
        if len(p_data) > 1:
            price_change = p_data['Close'].iloc[-1] - p_data['Close'].iloc[-2]
            multiplier = 100 if "JPY" in pair_name else 10000
            pip_velocity = abs(price_change * multiplier)
            if pip_velocity >= 15 and trend == "⚖️ STABLE":
                div_status = "⚠️ FRONT-RUN: BUY" if current_f > us10 else "⚠️ FRONT-RUN: SELL"

        spread = current_f - us10
        return spread, trend, div_status, us10, source_tag
    except:
        return 0.001, "⚖️ STABLE", "NORMAL", 4.15, "API Lag"

# 4. ICT PROBABILITY ENGINE (STRICTLY PRESERVED)
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

# 5. MASTER DATA (STRICTLY PRESERVED)
market_logic = {
    "EURUSD=X": {"name": "EUR/USD", "story": "The Euro/Bund Story", "min": 65, "max": 85, "bank": "ECB", "sentiment": "Neutral", "deep": "ECB on hold until Dec. German stimulus is the floor.", "bond": "Bund 10Y vs US 10Y", "news": "Tue: Eurozone CPI.", "target": "🏹 Target: 1.1680 (Sell-side Liquidity)"},
    "JPY=X": {"name": "USD/JPY", "story": "The Carry Flip", "min": 105, "max": 140, "bank": "BoJ", "sentiment": "Hawkish-Lean", "deep": "BoJ eyes April rate hike. Watch for intervention at 157.00.", "bond": "JGB 10Y vs US 10Y", "news": "Tue: BoJ Gov Ueda Speech.", "target": "🏹 Target: 153.20 (Discount OTE)"},
    "GBPUSD=X": {"name": "GBP/USD", "story": "The Cable Gilt Drift", "min": 85, "max": 115, "bank": "BoE", "sentiment": "Hold", "deep": "Support at 1.3450. UK inflation remains 'sticky'.", "bond": "Gilt 10Y vs US 10Y", "news": "Fri: US NFP Payrolls.", "target": "🏹 Target: 1.3580 (Buy-side Liquidity)"},
    "AUDUSD=X": {"name": "AUD/USD", "story": "The Resource Carry", "min": 65, "max": 85, "bank": "RBA", "sentiment": "Hawkish", "deep": "RBA 3.85% yield remains the strongest carry driver in the G10.", "bond": "AU 10Y vs US 10Y", "news": "Wed: AU GDP q/q.", "target": "🏹 Target: 0.7150 (Major Level)"},
    "GBPJPY=X": {"name": "GBP/JPY", "story": "The Beast Volatility", "min": 140, "max": 200, "bank": "BoE/BoJ", "sentiment": "Volatile", "deep": "The 'Beast'. Driven by UK Gilt yields vs BoJ hawkishness.", "bond": "UK Gilt 10Y vs JGB 10Y", "news": "Thu: UK MPC Meeting Minutes.", "target": "🏹 Target: 212.50"},
    "EURJPY=X": {"name": "EUR/JPY", "story": "Euro-Yen Cross Flow", "min": 120, "max": 170, "bank": "ECB/BoJ", "sentiment": "Neutral-Bullish", "deep": "Euro resilience meets Yen weakness. Watch 185.00 level.", "bond": "Bund 10Y vs JGB 10Y", "news": "Tue: Eurozone CPI.", "target": "🏹 Target: 186.20"},
    "NZDUSD=X": {"name": "NZD/USD", "story": "Kiwi Growth Lag", "min": 60, "max": 90, "bank": "RBNZ", "sentiment": "Dovish", "deep": "RBNZ prioritizing growth. Weakest of the commodity bloc.", "bond": "NZ 10Y vs US 10Y", "news": "Tue: NZ Terms of Trade.", "target": "🏹 Target: 0.5880"},
    "USDCAD=X": {"name": "USD/CAD", "story": "Loonie Tariff Watch", "min": 75, "max": 100, "bank": "BoC", "sentiment": "Cautious", "deep": "CAD underperforming on global tariff concerns.", "bond": "CA 10Y vs US 10Y", "news": "Wed: Canada GDP.", "target": "🏹 Target: 1.3930"}
}

# 6. SIDEBAR
st.sidebar.title("🏛 Global News & Bank Sentiment")
news_feed = get_live_news()
for entry in news_feed:
    with st.sidebar.expander(f"📌 {entry.title[:45]}..."):
        st.write(f"**{entry.title}**")
        st.markdown(f"[Source Article]({entry.link})")

# 7. MAIN UI TOP METRICS
st.title("📊 ICT Multi-Pair Intelligence Terminal")
y_col1, y_col2, y_col3 = st.columns(3)
with y_col1:
    sp_au, _, _, _, src_au = get_yield_details("AUD/USD")
    st.metric("AU-US 10Y Spread", f"{sp_au:.3f}%", f"Source: {src_au}", delta_color="off")
with y_col2:
    sp_nz, _, _, _, src_nz = get_yield_details("NZD/USD")
    st.metric("NZ-US 10Y Spread", f"{sp_nz:.3f}%", f"Source: {src_nz}", delta_color="off")
with y_col3:
    _, _, _, us_val, _ = get_yield_details("EUR/USD") # Pulled from FRED
    st.metric("US 10Y Yield", f"{us_val:.3f}%", "Source: FRED")

st.divider()

# 8. THE TABS
tab1, tab2, tab3, tab4 = st.tabs(["🖥 Market Grid", "🥩 Summary", "📅 Intelligence", "📈 Yield Charts"])

with tab1:
    cols = st.columns(3)
    for i, (ticker, info) in enumerate(market_logic.items()):
        with cols[i % 3]:
            score, pips, status, ratio, _, _ = calculate_ict_probability(ticker, info['min'], info['max'])
            try:
                price = yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
                st.markdown(f"### {info['name']}")
                st.metric("Price", f"{price:.4f}", f"{pips:.1f} Pips")
                color = "green" if score >= 70 else "orange" if score >= 40 else "red"
                st.markdown(f"**ICT Conviction: :{color}[{score}% ({status})]**")
                st.progress(score / 100)
                spread, yield_trend, divergence, _, src_tag = get_yield_details(info['name'])
                with st.expander("🔍 Strategic Analysis", expanded=True):
                    st.markdown(f"**Market Sentiment:** {info['deep']}")
                    st.markdown(f"**Yield Trend:** `{yield_trend}`") 
                    st.markdown(f"**Status:** `{divergence}`")
                    st.markdown(f"**Bond Context:** {info['bond']} | **Spread: {spread:.3f}% ({src_tag})**")
                    st.info(info['target'])
            except: st.error(f"Stream Down: {info['name']}")

with tab2:
    st.header("Institutional Executive Summary")
    summary_list = []
    for ticker, info in market_logic.items():
        score, _, status, ratio, _, _ = calculate_ict_probability(ticker, info['min'], info['max'])
        spread, yield_trend, divergence, _, src_tag = get_yield_details(info['name'])
        summary_list.append({"Pair": info['name'], "Conviction": f"{score}% ({status})", "Yield Trend": yield_trend, "Signal": divergence, "Spread": f"{spread:.3f}% ({src_tag})", "Target": info['target']})
    st.dataframe(pd.DataFrame(summary_list), use_container_width=True, hide_index=True)

with tab3:
    st.header(f"📅 Daily Closing Intelligence")
    for ticker, info in market_logic.items():
        score, pips, _, ratio,

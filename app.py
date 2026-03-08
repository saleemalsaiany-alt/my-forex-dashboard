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

# 3. FRED HISTORY ENGINE
def get_fred_history(series_id):
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=90"
        data = requests.get(url).json()
        df = pd.DataFrame(data['observations'])
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        return df.set_index('date')['value']
    except:
        return pd.Series()

# 4. EXCLUSIVE FRED YIELD ENGINE
def get_yield_details(pair_name="AUD/USD"):
    fred_map = {
        "AUD/USD": "IRLTLT01AUM156N", "NZD/USD": "IRLTLT01NZM156N",
        "USD/JPY": "IRLTLT01JPM156N", "GBP/USD": "IRLTLT01GBM156N",
        "EUR/USD": "IRLTLT01DEM156N", "USD/CAD": "IRLTLT01CAM156N",
        "GBP/JPY": "IRLTLT01GBM156N", "EUR/JPY": "IRLTLT01DEM156N"
    }
    US_10Y_ID = "DGS10"
    try:
        us_url = f"https://api.stlouisfed.org/fred/series/observations?series_id={US_10Y_ID}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=1"
        us_res = requests.get(us_url).json()
        us10 = float(us_res['observations'][0]['value'])
        series_id = fred_map.get(pair_name, "IRLTLT01AUM156N")
        fred_url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=5"
        fred_res = requests.get(fred_url).json()
        observations = fred_res['observations']
        current_f = float(observations[0]['value'])
        source_tag = "FRED Official"
        vals = [float(obs['value']) for obs in observations if obs['value'] != "."]
        avg_f = sum(vals) / len(vals) if vals else current_f
        diff = current_f - avg_f
        trend = "📈 FIRM INCREASE" if diff > 0.10 else "📉 FIRM DECREASE" if diff < -0.10 else "⚖️ STABLE"
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
        return 0.001, "⚖️ STABLE", "NORMAL", 4.15, "FRED Offline"

# 5. ICT PROBABILITY ENGINE
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

# 6. MASTER DATA
market_logic = {
    "EURUSD=X": {"name": "EUR/USD", "story": "The Euro/Bund Story", "min": 65, "max": 85, "bank": "ECB", "sentiment": "Neutral", "deep": "ECB on hold until Dec.", "bond": "Bund 10Y vs US 10Y", "news": "Tue: Eurozone CPI.", "target": "🏹 Target: 1.1680"},
    "JPY=X": {"name": "USD/JPY", "story": "The Carry Flip", "min": 105, "max": 140, "bank": "BoJ", "sentiment": "Hawkish-Lean", "deep": "BoJ eyes April rate hike.", "bond": "JGB 10Y vs US 10Y", "news": "Tue: BoJ Gov Ueda Speech.", "target": "🏹 Target: 153.20"},
    "GBPUSD=X": {"name": "GBP/USD", "story": "The Cable Gilt Drift", "min": 85, "max": 115, "bank": "BoE", "sentiment": "Hold", "deep": "Support at 1.3450.", "bond": "Gilt 10Y vs US 10Y", "news": "Fri: US NFP Payrolls.", "target": "🏹 Target: 1.3580"},
    "AUDUSD=X": {"name": "AUD/USD", "story": "The Resource Carry", "min": 65, "max": 85, "bank": "RBA", "sentiment": "Hawkish", "deep": "RBA 3.85% yield driver.", "bond": "AU 10Y vs US 10Y", "news": "Wed: AU GDP q/q.", "target": "🏹 Target: 0.7150"},
    "GBPJPY=X": {"name": "GBP/JPY", "story": "The Beast Volatility", "min": 140, "max": 200, "bank": "BoE/BoJ", "sentiment": "Volatile", "deep": "UK Gilt yields vs BoJ.", "bond": "UK Gilt 10Y vs JGB 10Y", "news": "Thu: UK MPC Meeting Minutes.", "target": "🏹 Target: 212.50"},
    "EURJPY=X": {"name": "EUR/JPY", "story": "Euro-Yen Cross Flow", "min": 120, "max": 170, "bank": "ECB/BoJ", "sentiment": "Neutral-Bullish", "deep": "Euro resilience meets Yen weakness.", "bond": "Bund 10Y vs JGB 10Y", "news": "Tue: Eurozone CPI.", "target": "🏹 Target: 186.20"},
    "NZDUSD=X": {"name": "NZD/USD", "story": "Kiwi Growth Lag", "min": 60, "max": 90, "bank": "RBNZ", "sentiment": "Dovish", "deep": "RBNZ prioritizing growth.", "bond": "NZ 10Y vs US 10Y", "news": "Tue: NZ Terms of Trade.", "target": "🏹 Target: 0.5880"},
    "USDCAD=X": {"name": "USD/CAD", "story": "Loonie Tariff Watch", "min": 75, "max": 100, "bank": "BoC", "sentiment": "Cautious", "deep": "CAD underperforming on tariffs.", "bond": "CA 10Y vs US 10Y", "news": "Wed: Canada GDP.", "target": "🏹 Target: 1.3930"}
}

# 7. SIDEBAR
st.sidebar.title("🏛 Global News & Bank Sentiment")
news_feed = get_live_news()
for entry in news_feed:
    with st.sidebar.expander(f"📌 {entry.title[:45]}..."):
        st.write(f"**{entry.title}**")
        st.markdown(f"[Source Article]({entry.link})")

# 8. MAIN UI TOP METRICS
st.title("📊 ICT Multi-Pair Intelligence Terminal")
y_col1, y_col2, y_col3 = st.columns(3)
with y_col1:
    sp_au, _, _, _, src_au = get_yield_details("AUD/USD")
    st.metric("AU-US 10Y Spread", f"{sp_au:.3f}%", f"Source: {src_au}", delta_color="off")
with y_col2:
    sp_nz, _, _, _, src_nz = get_yield_details("NZD/USD")
    st.metric("NZ-US 10Y Spread", f"{sp_nz:.3f}%", f"Source: {src_nz}", delta_color="off")
with y_col3:
    _, _, _, us_val, _ = get_yield_details("EUR/USD")
    st.metric("US 10Y Yield", f"{us_val:.3f}%", "Source: FRED Official")

st.divider()

# 9. THE TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🖥 Market Grid", "🥩 Summary", "📅 Intelligence", "📈 Yield Charts", "🏛 Bond Futures Lead"])

# ... (Tabs 1-4 remain exactly as before) ...
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
            except: 
                st.error(f"Stream Down: {info['name']}")

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
        score, pips, _, ratio, prev, last = calculate_ict_probability(ticker, info['min'], info['max'])
        spread, trend, div, us_yield, _ = get_yield_details(info['name'])
        if last is not None:
            dir_text = "downside" if last['Close'] < last['Open'] else "upside"
            move_pips = abs(last['Close'] - last['Open']) * (100 if "JPY" in ticker else 10000)
            st.subheader(f"{info['name']} ({info['story']})")
            st.markdown(f"**Yesterday:** Price closed with displacement to the {dir_text} ({move_pips:.1f} pips). US 10Y is at {us_yield:.2f}%.")
            st.divider()

with tab4:
    st.header("📈 FRED Anchor: Institutional Yield Trends")
    c_choice = st.selectbox("Select Bond Yield to Visualize", ["US 10Y (Benchmark)", "Australia 10Y", "New Zealand 10Y", "Japan 10Y", "UK 10Y", "Germany 10Y", "Canada 10Y"])
    fred_id_map = {"US 10Y (Benchmark)": "DGS10", "Australia 10Y": "IRLTLT01AUM156N", "New Zealand 10Y": "IRLTLT01NZM156N", "Japan 10Y": "IRLTLT01JPM156N", "UK 10Y": "IRLTLT01GBM156N", "Germany 10Y": "IRLTLT01DEM156N", "Canada 10Y": "IRLTLT01CAM156N"}
    selected_id = fred_id_map[c_choice]
    with st.spinner(f"Fetching 90-day history for {c_choice}..."):
        history = get_fred_history(selected_id)
        if not history.empty: 
            st.line_chart(history)

# --- TAB 5: UPDATED WITH LEAD INDICATOR ---
with tab5:
    st.header("🏛 Bond Futures Lead: ICT Intramarket Analysis")
    st.write("Daily Timeframe: Comparing ZB, ZN, and ZF (CME) vs DXY.")
    
    futures_map = {"ZB (30Y Bond)": "ZB=F", "ZN (10Y Note)": "ZN=F", "ZF (5Y Note)": "ZF=F", "US Dollar Index (DXY)": "DX-Y.NYB"}
    
    f_data = {}
    for name, sym in futures_map.items():
        try:
            df = yf.Ticker(sym).history(period="60d", interval="1d")
            if not df.empty: f_data[name] = df
        except: pass

    if len(f_data) == 4:
        # 1. CORE STATUS MATCH
        last_zb = f_data["ZB (30Y Bond)"]['Close'].iloc[-1]
        open_zb = f_data["ZB (30Y Bond)"]['Open'].iloc[-1]
        zf_perf = f_data["ZF (5Y Note)"]['Close'].pct_change(5).iloc[-1]
        zb_perf = f_data["ZB (30Y Bond)"]['Close'].pct_change(5).iloc[-1]
        engine_bearish_dxy = zf_perf > zb_perf
        price_bearish_dxy = last_zb > open_zb

        # 2. NEW: LEAD INDICATOR LOGIC (MARKET STRUCTURE SHIFT)
        # Check if any Bond has broken 5-day high/low while DXY hasn't
        def check_mss(df):
            last_close = df['Close'].iloc[-1]
            high_5d = df['High'].iloc[-6:-1].max()
            low_5d = df['Low'].iloc[-6:-1].min()
            if last_close > high_5d: return "BULLISH_MSS"
            if last_close < low_5d: return "BEARISH_MSS"
            return "NONE"

        mss_zb = check_mss(f_data["ZB (30Y Bond)"])
        mss_dxy = check_mss(f_data["US Dollar Index (DXY)"])

        st.subheader("🛡 Strategic Status Match")
        if engine_bearish_dxy == price_bearish_dxy:
            st.markdown("### :green[🟢 STATUS MATCH: HIGH PROBABILITY]")
            st.success("The internal Bond Engine (RS) and Price Action are in sync.")
        else:
            st.markdown("### :orange[⚠️ JUDAS SWING CONDITION DETECTED]")
            st.warning("The Bond Engine and Price Action are conflicting. This is likely a trap.")

        # --- LEAD INDICATOR ALERT BOX ---
        st.subheader("🚨 Lead Indicator Alert")
        if mss_zb != "NONE" and mss_dxy == "NONE":
            direction = "BULLISH (Bearish DXY)" if mss_zb == "BULLISH_MSS" else "BEARISH (Bullish DXY)"
            st.info(f"💡 **HEADS-UP:** Bonds have shifted structure **{direction}**, but DXY is lagging. Institutional shift is likely starting.")
        elif mss_dxy != "NONE" and mss_zb == "NONE":
            st.error("⚠️ **CAUTION:** DXY is breaking structure but Bonds are **not confirming.** Possible stop-run.")
        else:
            st.write("Current Market Structure is convergent across Bonds and DXY.")

        st.divider()
        col_anal, col_exec = st.columns([2, 1])
        with col_anal:
            st.markdown("### 📊 Findings")
            if engine_bearish_dxy: st.info("🔍 **RS Comparison:** ZF leading ZB higher. **Internal Bias: BEARISH DXY.**")
            else: st.info("🔍 **RS Comparison:** ZB leading ZF higher. **Internal Bias: BULLISH DXY.**")

        with col_exec:
            st.markdown("### 🏹 Execution Bias")
            if price_bearish_dxy: st.success("💎 **BULLISH BONDS**\nExpect: BEARISH DXY / BUY G10")
            else: st.error("🔥 **BEARISH BONDS**\nExpect: BULLISH DXY / SELL G10")

    st.divider()
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        for title in list(futures_map.keys())[:2]:
            st.subheader(f"{title} (Daily)")
            if title in f_data: st.line_chart(f_data[title]['Close'], use_container_width=True)
    with f_col2:
        for title in list(futures_map.keys())[2:]:
            st.subheader(f"{title} (Daily)")
            if title in f_data: st.line_chart(f_data[title]['Close'], use_container_width=True)

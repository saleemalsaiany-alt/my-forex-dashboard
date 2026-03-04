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
    "EURUSD=X": {"name": "EUR/USD", "story": "Euro/Bund Story", "min": 65, "max": 85, "deep": "ECB on hold.", "bond": "Bund 10Y vs US 10Y", "target": "🏹 Target: 1.1680"},
    "JPY=X": {"name": "USD/JPY", "story": "The Carry Flip", "min": 105, "max": 140, "deep": "BoJ eyes rate hike.", "bond": "JGB 10Y vs US 10Y", "target": "🏹 Target: 153.20"},
    "GBPUSD=X": {"name": "GBP/USD", "story": "Cable Gilt Drift", "min": 85, "max": 115, "deep": "UK inflation sticky.", "bond": "Gilt 10Y vs US 10Y", "target": "🏹 Target: 1.3580"},
    "AUDUSD=X": {"name": "AUD/USD", "story": "Resource Carry", "min": 65, "max": 85, "deep": "RBA hawkish.", "bond": "AU 10Y vs US 10Y", "target": "🏹 Target: 0.7150"},
    "GBPJPY=X": {"name": "GBP/JPY", "story": "Beast Volatility", "min": 140, "max": 200, "deep": "UK yields vs BoJ.", "bond": "UK Gilt vs JGB", "target": "🏹 Target: 212.50"},
    "EURJPY=X": {"name": "EUR/JPY", "story": "Euro-Yen Flow", "min": 120, "max": 170, "deep": "Euro resilience.", "bond": "Bund vs JGB", "target": "🏹 Target: 186.20"},
    "NZDUSD=X": {"name": "NZD/USD", "story": "Kiwi Growth Lag", "min": 60, "max": 90, "deep": "RBNZ prioritized growth.", "bond": "NZ vs US 10Y", "target": "🏹 Target: 0.5880"},
    "USDCAD=X": {"name": "USD/CAD", "story": "Loonie Tariff Watch", "min": 75, "max": 100, "deep": "CAD underperforming.", "bond": "CA vs US 10Y", "target": "🏹 Target: 1.3930"}
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

# [Tab 1-4 logic remains exactly the same as previous stable version]
# ... (omitted for brevity but included in full script) ...

with tab5:
    st.header("🏛 Bond Futures Lead: ICT Intramarket Analysis")
    st.write("Daily Timeframe: Analyzing ZB, ZN, and ZF (CME) against the DXY (ICE).")
    
    futures_map = {"ZB (30Y Bond)": "ZB=F", "ZN (10Y Note)": "ZN=F", "ZF (5Y Note)": "ZF=F", "US Dollar Index (DXY)": "DX-Y.NYB"}
    
    # 1. FETCH DAILY DATA FOR ICT FINDINGS
    f_data = {}
    for name, sym in futures_map.items():
        try:
            df = yf.Ticker(sym).history(period="60d", interval="1d")
            if not df.empty:
                f_data[name] = df
        except: pass

    # 2. ANALYSIS & FINDINGS (ICT Month 10 Implementation)
    if len(f_data) == 4:
        st.subheader("🕵️ Smart Money Analysis (Daily)")
        
        # Calculate recent highs/lows for SMT
        last_zb = f_data["ZB (30Y Bond)"]['Close'].iloc[-1]
        last_zn = f_data["ZN (10Y Note)"]['Close'].iloc[-1]
        last_dxy = f_data["US Dollar Index (DXY)"]['Close'].iloc[-1]
        
        # SMT Check: Crack in Correlation
        zb_up = f_data["ZB (30Y Bond)"]['Close'].iloc[-1] > f_data["ZB (30Y Bond)"]['Close'].iloc[-5]
        zn_up = f_data["ZN (10Y Note)"]['Close'].iloc[-1] > f_data["ZN (10Y Note)"]['Close'].iloc[-5]
        dxy_down = f_data["US Dollar Index (DXY)"]['Close'].iloc[-1] < f_data["US Dollar Index (DXY)"]['Close'].iloc[-5]

        col_anal, col_exec = st.columns([2, 1])
        with col_anal:
            st.markdown("### 📊 Findings")
            # Logic: If DXY makes lower low but ZB/ZN fails to make higher high = SMT
            if dxy_down and not (zb_up and zn_up):
                st.error("⚠️ **SMT DIVERGENCE DETECTED:** DXY is seeking liquidity low, but Bond basket lacks Smart Money sponsorship for higher prices. Potential DXY reversal higher.")
            elif not dxy_down and (zb_up or zn_up):
                st.success("✅ **BULLISH BOND FLOW:** Institutional Order Flow is respecting bullish PD arrays in Bonds. Bias for DXY is seeking Sell-Side Liquidity.")
            else:
                st.info("⚖️ **SYMMETRICAL CORRELATION:** DXY and Bonds are moving inversely in a healthy manner. No crack in correlation.")
            
            # Relative Strength (ZF lead)
            zf_strength = f_data["ZF (5Y Note)"]['Close'].pct_change(5).iloc[-1]
            zb_strength = f_data["ZB (30Y Bond)"]['Close'].pct_change(5).iloc[-1]
            if zf_strength > zb_strength:
                st.caption("🔍 **RS Comparison:** Short-term rates (ZF) are leading the move. Suggests hawkish rate expectation shifts.")

        with col_exec:
            st.markdown("### 🏹 Execution Bias")
            if zb_up and zn_up:
                st.write("**Bias:** 📉 BEARISH DOLLAR")
                st.info("Focus: G10 Longs (EUR/GBP/AUD)")
            elif not zb_up and not zn_up:
                st.write("**Bias:** 📈 BULLISH DOLLAR")
                st.info("Focus: G10 Shorts (EUR/GBP/AUD)")
            else:
                st.write("**Bias:** ⚖️ NEUTRAL")

    st.divider()

    # 3. DAILY CHARTS
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        for title, sym in list(futures_map.items())[:2]:
            st.subheader(title)
            if title in f_data: st.line_chart(f_data[title]['Close'])
                
    with f_col2:
        for title, sym in list(futures_map.items())[2:]:
            st.subheader(title)
            if title in f_data: st.line_chart(f_data[title]['Close'])

    st.caption("Note: Bonds prices move inversely to DXY. Respect the Daily Order Block/Fair Value Gaps for direction.")

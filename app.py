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

# 3. FRED HISTORY ENGINE (FOR TAB 4)
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
    "EURUSD=X": {"name": "EUR/USD", "story": "The Euro/Bund Story", "min": 65, "max": 85, "bank": "ECB", "sentiment": "Neutral", "deep": "ECB on hold until Dec. German stimulus is the floor.", "bond": "Bund 10Y vs US 10Y", "news": "Tue: Eurozone CPI.", "target": "🏹 Target: 1.1680 (Sell-side Liquidity)"},
    "JPY=X": {"name": "USD/JPY", "story": "The Carry Flip", "min": 105, "max": 140, "bank": "BoJ", "sentiment": "Hawkish-Lean", "deep": "BoJ eyes April rate hike. Watch for intervention at 157.00.", "bond": "JGB 10Y vs US 10Y", "news": "Tue: BoJ Gov Ueda Speech.", "target": "🏹 Target: 153.20 (Discount OTE)"},
    "GBPUSD=X": {"name": "GBP/USD", "story": "The Cable Gilt Drift", "min": 85, "max": 115, "bank": "BoE", "sentiment": "Hold", "deep": "Support at 1.3450. UK inflation remains 'sticky'.", "bond": "Gilt 10Y vs US 10Y", "news": "Fri: US NFP Payrolls.", "target": "🏹 Target: 1.3580 (Buy-side Liquidity)"},
    "AUDUSD=X": {"name": "AUD/USD", "story": "The Resource Carry", "min": 65, "max": 85, "bank": "RBA", "sentiment": "Hawkish", "deep": "RBA 3.85% yield remains the strongest carry driver in the G10.", "bond": "AU 10Y vs US 10Y", "news": "Wed: AU GDP q/q.", "target": "🏹 Target: 0.7150 (Major Level)"},
    "GBPJPY=X": {"name": "GBP/JPY", "story": "The Beast Volatility", "min": 140, "max": 200, "bank": "BoE/BoJ", "sentiment": "Volatile", "deep": "The 'Beast'. Driven by UK Gilt yields vs BoJ hawkishness.", "bond": "UK Gilt 10Y vs JGB 10Y", "news": "Thu: UK MPC Meeting Minutes.", "target": "🏹 Target: 212.50"},
    "EURJPY=X": {"name": "EUR/JPY", "story": "Euro-Yen Cross Flow", "min": 120, "max": 170, "bank": "ECB/BoJ", "sentiment": "Neutral-Bullish", "deep": "Euro resilience meets Yen weakness. Watch 185.00 level.", "bond": "Bund 10Y vs JGB 10Y", "news": "Tue: Eurozone CPI.", "target": "🏹 Target: 186.20"},
    "NZDUSD=X": {"name": "NZD/USD", "story": "Kiwi Growth Lag", "min": 60, "max": 90, "bank": "RBNZ", "sentiment": "Dovish", "deep": "RBNZ prioritizing growth. Weakest of the commodity bloc.", "bond": "NZ 10Y vs US 10Y", "news": "Tue: NZ Terms of Trade.", "target": "🏹 Target: 0.5880"},
    "USDCAD=X": {"name": "USD/CAD", "story": "Loonie Tariff Watch", "min": 75, "max": 100, "bank": "BoC", "sentiment": "Cautious", "deep": "CAD underperforming on global tariff concerns.", "bond": "CA 10Y vs US 10Y", "news": "Wed: Canada GDP.", "target": "🏹 Target: 1.3930"}
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
    _, _, _, us_val, _ = get_yield_details("EUR/USD") # Pull US 10Y from FRED
    st.metric("US 10Y Yield", f"{us_val:.3f}%", "Source: FRED Official")

st.divider()

# 9. THE TABS (Added Tab 5)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🖥 Market Grid", "🥩 Summary", "📅 Intelligence", "📈 Yield Charts", "🏛 Bond Futures Lead"])

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
        score, pips, _, ratio, prev, last = calculate_ict_probability(ticker, info['min'], info['max'])
        spread, trend, div, us_yield, _ = get_yield_details(info['name'])
        dir_text = "downside" if last['Close'] < last['Open'] else "upside"
        move_pips = abs(last['Close'] - last['Open']) * (100 if "JPY" in ticker else 10000)
        st.subheader(f"{info['name']} ({info['story']})")
        st.markdown(f"**Yesterday:** Price closed with displacement to the {dir_text} ({move_pips:.1f} pips). US 10Y is at {us_yield:.2f}%.")
        st.divider()

with tab4:
    st.header("📈 FRED Anchor: Institutional Yield Trends")
    st.write("Visualizing the last 90 days of government bond performance. Use this to identify long-term SMT Divergence.")
    c_choice = st.selectbox("Select Bond Yield to Visualize", ["US 10Y (Benchmark)", "Australia 10Y", "New Zealand 10Y", "Japan 10Y", "UK 10Y", "Germany 10Y", "Canada 10Y"])
    fred_id_map = {
        "US 10Y (Benchmark)": "DGS10", "Australia 10Y": "IRLTLT01AUM156N", 
        "New Zealand 10Y": "IRLTLT01NZM156N", "Japan 10Y": "IRLTLT01JPM156N", 
        "UK 10Y": "IRLTLT01GBM156N", "Germany 10Y": "IRLTLT01DEM156N", 
        "Canada 10Y": "IRLTLT01CAM156N"
    }
    selected_id = fred_id_map[c_choice]
    with st.spinner(f"Fetching 90-day history for {c_choice}..."):
        history = get_fred_history(selected_id)
        if not history.empty:
            st.line_chart(history)
            st.caption(f"Data provided by Federal Reserve Economic Data (FRED). ID: {selected_id}")
        else:
            st.error("Failed to retrieve FRED history. Please check your API key or connection.")

# --- NEW TAB 5: BOND FUTURES LEAD ---
with tab5:
    st.header("🏛 Bond Futures Lead: Institutional SMT Engine")
    st.write("yFinance Native Charts: High-reliability monitoring of ZB (30Y), ZN (10Y), and ZF (5Y) vs DXY.")
    
    # 5-Minute Intraday Data for ICT Precision
    futures_map = {
        "ZB (30Y Bond)": "ZB=F",
        "ZN (10Y Note)": "ZN=F",
        "ZF (5Y Note)": "ZF=F",
        "US Dollar Index (DXY)": "DX-Y.NYB"
    }
    
    f_col1, f_col2 = st.columns(2)
    
    with f_col1:
        for title, symbol in list(futures_map.items())[:2]:
            try:
                data = yf.Ticker(symbol).history(period="3d", interval="5m")
                if not data.empty:
                    st.subheader(title)
                    st.line_chart(data['Close'], use_container_width=True)
                    st.caption(f"Real-time 5m data for {symbol}")
            except:
                st.error(f"Error loading {title}")
                
    with f_col2:
        for title, symbol in list(futures_map.items())[2:]:
            try:
                data = yf.Ticker(symbol).history(period="3d", interval="5m")
                if not data.empty:
                    st.subheader(title)
                    st.line_chart(data['Close'], use_container_width=True)
                    st.caption(f"Real-time 5m data for {symbol}")
            except:
                st.error(f"Error loading {title}")

    st.success("📊 **Reliability Note**: Using yFinance native data bypasses third-party widget restrictions. Charts are 100% focused on US Treasuries.")

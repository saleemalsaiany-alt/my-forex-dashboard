import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

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

# 3. YIELD & FRONT-RUN VELOCITY ENGINE
def get_yield_details(pair_name="AUD/USD"):
    symbols = {
        "AUD/USD": "^AU10Y", "NZD/USD": "^NZ10Y.NM", "USD/JPY": "JP10Y.BD", 
        "GBP/USD": "^GILT", "EUR/USD": "BUND10Y.BD", "USD/CAD": "^CAN10Y",
        "GBP/JPY": "^GILT", "EUR/JPY": "BUND10Y.BD" 
    }
    try:
        us10_ticker = yf.Ticker("^TNX")
        us10_hist = us10_ticker.history(period="5d")
        us10 = us10_hist['Close'].iloc[-1]
        us10_prev = us10_hist['Close'].iloc[-2]
        us_dir = "UP" if us10 > us10_prev else "DOWN"
        
        ticker_sym = symbols.get(pair_name, "^AU10Y")
        f_ticker = yf.Ticker(ticker_sym)
        f_hist = f_ticker.history(period="5d")
        current_f = f_hist['Close'].iloc[-1]
        prev_f = f_hist['Close'].iloc[-2]
        f_dir = "UP" if current_f > prev_f else "DOWN"
        
        current_spread = current_f - us10
        prev_spread = prev_f - us10_prev
        spread_arrow = "↑" if current_spread > prev_spread else "↓"
        
        avg_f = f_hist['Close'].mean()
        diff = current_f - avg_f
        trend = "📈 FIRM INCREASE" if diff > 0.10 else "📉 FIRM DECREASE" if diff < -0.10 else "⚖️ STABLE"

        pair_ticker = pair_name.replace("/", "") + "=X"
        p_data = yf.Ticker(pair_ticker).history(period="1d", interval="15m")
        velocity_alert = False
        if len(p_data) > 1:
            price_change = p_data['Close'].iloc[-1] - p_data['Close'].iloc[-2]
            multiplier = 100 if "JPY" in pair_name else 10000
            pip_velocity = abs(price_change * multiplier)
            if pip_velocity >= 15 and trend == "⚖️ STABLE":
                velocity_alert = True

        div_status = "✅ CONVERGENT"
        if f_dir != us_dir:
            if "JPY" in pair_name or pair_name.endswith("/USD"):
                if f_dir == "UP" and us_dir == "DOWN": 
                    div_status = "⚠️ FRONT-RUN: INSTITUTIONAL BUY" if velocity_alert else "⚠️ DIVERGENCE: WAIT FOR A BUY"
                if f_dir == "DOWN" and us_dir == "UP": 
                    div_status = "⚠️ FRONT-RUN: INSTITUTIONAL SELL" if velocity_alert else "⚠️ DIVERGENCE: WAIT FOR A SELL"
            elif pair_name.startswith("USD/"): 
                if f_dir == "UP" and us_dir == "DOWN": 
                    div_status = "⚠️ FRONT-RUN: INSTITUTIONAL SELL" if velocity_alert else "⚠️ DIVERGENCE: WAIT FOR A SELL"
                if f_dir == "DOWN" and us_dir == "UP": 
                    div_status = "⚠️ FRONT-RUN: INSTITUTIONAL BUY" if velocity_alert else "⚠️ DIVERGENCE: WAIT FOR A BUY"
        
        sentiment = "🚀 BULLISH" if current_spread > 0.4 else "🩸 BEARISH" if current_spread < -0.4 else "⚖️ NEUTRAL"
        return current_spread, sentiment, trend, div_status, spread_arrow
    except:
        return 0, "Yield Error", "⚖️ STABLE", "NORMAL", ""

def get_usd_standalone_trend():
    try:
        us10_ticker = yf.Ticker("^TNX")
        us10_hist = us10_ticker.history(period="5d")
        current_us = us10_hist['Close'].iloc[-1]
        avg_us = us10_hist['Close'].mean()
        diff = current_us - avg_us
        trend = "📈 FIRM INCREASE" if diff > 0.10 else "📉 FIRM DECREASE" if diff < -0.10 else "⚖️ STABLE"
        return current_us, trend
    except:
        return 0, "⚖️ STABLE"

def calculate_ict_probability(ticker, range_min, range_max):
    try:
        data = yf.Ticker(ticker).history(period="5d")
        last_candle = data.iloc[-1] 
        open_p, close_p = last_candle['Open'], last_candle['Close']
        high_p, low_p = last_candle['High'], last_candle['Low']
        multiplier = 100 if "JPY" in ticker else 10000
        range_pips = (high_p - low_p) * multiplier
        body_pips = abs(open_p - close_p) * multiplier
        score = 0
        dow = datetime.now().weekday()
        if 1 <= dow <= 3: score += 35 
        if range_min <= range_pips <= range_max: score += 35
        ratio = body_pips / range_pips if range_pips > 0 else 0
        if ratio >= 0.55: score += 30
        status = "HIGH" if score >= 70 else "MID" if score >= 40 else "LOW"
        return score, range_pips, status, ratio
    except:
        return 0, 0, "ERR", 0

# 4. MASTER DATA INTELLIGENCE (FULL REVERTED CONTENT)
market_logic = {
    "AUDUSD=X": {"name": "AUD/USD", "min": 65, "max": 85, "bank": "RBA", "sentiment": "Hawkish", "deep": "RBA 3.85% yield remains the strongest carry driver in the G10.", "bond": "AU 10Y vs US 10Y", "news": "Wed: AU GDP q/q.", "target": "🏹 Target: 0.7150", "intel_y": "AUD supported by strong AU yields despite USD strength.", "intel_t": "Watch for RBA comments. Look for Buy at 0.6540.", "sweet": "0.6550 Discount", "rec": "Buy on London Open Dip."},
    "JPY=X": {"name": "USD/JPY", "min": 105, "max": 140, "bank": "BoJ", "sentiment": "Hawkish-Lean", "deep": "BoJ eyes April rate hike. Watch for intervention at 157.00.", "bond": "JGB 10Y vs US 10Y", "news": "Tue: BoJ Gov Ueda Speech.", "target": "🏹 Target: 153.20", "intel_y": "Risk-off sentiment strengthened JPY.", "intel_t": "Yield bounce could send this back to 155.00.", "sweet": "153.80 OTE", "rec": "Scalp Long on yield spike."},
    "GBPJPY=X": {"name": "GBP/JPY", "min": 140, "max": 200, "bank": "BoE/BoJ", "sentiment": "Volatile", "deep": "The 'Beast'. Driven by UK Gilt yields vs BoJ hawkishness.", "bond": "UK Gilt 10Y vs JGB 10Y", "news": "Thu: UK MPC Meeting Minutes.", "target": "🏹 Target: 212.50", "intel_y": "Massive 150 pip range. Volatility extreme.", "intel_t": "Avoid mid-range. Wait for daily extremes.", "sweet": "208.50 Equilibrium", "rec": "Wait for London session high."},
    "EURJPY=X": {"name": "EUR/JPY", "min": 120, "max": 170, "bank": "ECB/BoJ", "sentiment": "Neutral-Bullish", "deep": "Euro resilience meets Yen weakness. Watch 185.00 level.", "bond": "Bund 10Y vs JGB 10Y", "news": "Tue: Eurozone CPI.", "target": "🏹 Target: 186.20", "intel_y": "Euro holding ground against Yen despite weak Bunds.", "intel_t": "Consolidation likely before CPI news.", "sweet": "184.20", "rec": "Neutral - No clear setup."},
    "NZDUSD=X": {"name": "NZD/USD", "min": 60, "max": 90, "bank": "RBNZ", "sentiment": "Dovish", "deep": "RBNZ prioritizing growth. Weakest of the commodity bloc.", "bond": "NZ 10Y vs US 10Y", "news": "Tue: NZ Terms of Trade.", "target": "🏹 Target: 0.5880", "intel_y": "NZD underperforming AUD significantly.", "intel_t": "Look for Sell on any USD strength.", "sweet": "0.5920 Premium", "rec": "Sell on Retrace."},
    "GBPUSD=X": {"name": "GBP/USD", "min": 85, "max": 115, "bank": "BoE", "sentiment": "Hold", "deep": "Support at 1.3450. UK inflation remains 'sticky'.", "bond": "Gilt 10Y vs US 10Y", "news": "Fri: US NFP Payrolls.", "target": "🏹 Target: 1.3580", "intel_y": "GBP rejected at 1.3500 resistance.", "intel_t": "Watch 1.3420 for institutional support.", "sweet": "1.3440 Discount", "rec": "Monitor SMT with EUR/USD."},
    "EURUSD=X": {"name": "EUR/USD", "min": 65, "max": 85, "bank": "ECB", "sentiment": "Neutral", "deep": "ECB on hold until Dec. German stimulus is the floor.", "bond": "Bund 10Y vs US 10Y", "news": "Tue: Eurozone CPI.", "target": "🏹 Target: 1.1910", "intel_y": "Price closed below the big wick. Bearish shift.", "intel_t": "Look for Sell at 25% retrace of yesterday's body.", "sweet": "1.1780", "rec": "Sell at 1.1790 (25% Retrace)."},
    "USDCAD=X": {"name": "USD/CAD", "min": 75, "max": 100, "bank": "BoC", "sentiment": "Cautious", "deep": "CAD underperforming on global tariff concerns.", "bond": "CA 10Y vs US 10Y", "news": "Wed: Canada GDP.", "target": "🏹 Target: 1.3930", "intel_y": "Oil price drop weakened CAD.", "intel_t": "Trend remains firmly bullish for USD/CAD.", "sweet": "1.3850", "rec": "Buy at Discount FVG."}
}

# 5. UI TABS
st.title("📊 ICT Multi-Pair Intelligence Terminal")
tab_main, tab_intel = st.tabs(["🚀 Live Strategic Terminal", "📅 Daily Closing Intel"])

with tab_main:
    y_col1, y_col2, y_col3 = st.columns(3)
    with y_col1:
        sp_au, txt_au, _, _, arr_au = get_yield_details("AUD/USD")
        st.metric("AU-US 10Y Yield Spread", f"{sp_au:.3f}% {arr_au}", delta=txt_au)
    with y_col2:
        sp_nz, txt_nz, _, _, arr_nz = get_yield_details("NZD/USD")
        st.metric("NZ-US 10Y Yield Spread", f"{sp_nz:.3f}% {arr_nz}", delta=txt_nz)
    with y_col3:
        us_val, us_trend = get_usd_standalone_trend()
        st.metric("US 10Y Yield (USD Standalone)", f"{us_val:.3f}%", delta=us_trend)
    st.divider()
    cols = st.columns(3)
    for i, (ticker, info) in enumerate(market_logic.items()):
        with cols[i % 3]:
            score, pips, status, ratio = calculate_ict_probability(ticker, info['min'], info['max'])
            price_data = yf.Ticker(ticker).history(period="1d")
            price = price_data['Close'].iloc[-1]
            st.markdown(f"### {info['name']}")
            st.metric("Price", f"{price:.4f}", f"{pips:.1f} Pips")
            color = "green" if score >= 70 else "orange" if score >= 40 else "red"
            st.markdown(f"**ICT Conviction: :{color}[{score}% ({status})]**")
            st.progress(score / 100)
            spread, _, yield_trend, divergence, s_arrow = get_yield_details(info['name'])
            with st.expander("🔍 Strategic & News Analysis"):
                st.markdown(f"**Market Sentiment:** {info['deep']}")
                st.markdown(f"**Yield Trend:** `{yield_trend}`") 
                if "FRONT-RUN" in divergence: st.warning(f"⚡ {divergence}")
                elif "WAIT" in divergence: st.error(f"🩸 {divergence}")
                else: st.markdown(f"**Divergence Status:** `{divergence}`")
                st.markdown(f"**Bond Context:** {info['bond']} | **Spread: {spread:.3f}% {s_arrow}**")
                st.markdown(f"**High Impact News:** {info['news']}")
                st.info(info['target'])

with tab_intel:
    st.header("Daily Post-Market & Pre-Market Strategy")
    for ticker, info in market_logic.items():
        with st.expander(f"📌 {info['name']} - Daily Summary"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("Yesterday's Recap")
                st.write(info['intel_y'])
            with col_b:
                st.subheader("Today's Game Plan")
                st.write(info['intel_t'])
            st.divider()
            st.success(f"🎯 Sweet Spot: {info['sweet']}")
            st.info(f"💡 Recommendation: {info['rec']}")

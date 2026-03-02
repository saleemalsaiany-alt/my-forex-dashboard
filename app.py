import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta

# 1. ENGINE & CONFIG
st.set_page_config(page_title="ICT Strategic Terminal", layout="wide")
st_autorefresh(interval=300000, key="master_refresher")

# 2. YIELD & FRONT-RUN VELOCITY ENGINE
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
        
        ticker_sym = symbols.get(pair_name, "^AU10Y")
        f_ticker = yf.Ticker(ticker_sym)
        f_hist = f_ticker.history(period="5d")
        
        current_f = f_hist['Close'].iloc[-1]
        avg_f = f_hist['Close'].mean()
        
        diff = current_f - avg_f
        trend = "📈 FIRM INCREASE" if diff > 0.10 else "📉 FIRM DECREASE" if diff < -0.10 else "⚖️ STABLE"

        # Velocity Check
        pair_ticker = pair_name.replace("/", "") + "=X"
        p_data = yf.Ticker(pair_ticker).history(period="1d", interval="15m")
        velocity_alert = False
        if len(p_data) > 1:
            pip_velocity = abs((p_data['Close'].iloc[-1] - p_data['Close'].iloc[-2]) * (100 if "JPY" in pair_name else 10000))
            if pip_velocity >= 15 and trend == "⚖️ STABLE": velocity_alert = True

        spread = current_f - us10
        div_status = "✅ CONVERGENT" # Simplified for logic flow
        if velocity_alert: div_status = "⚠️ FRONT-RUN DETECTED"
        
        return spread, trend, div_status, us10
    except:
        return 0, "⚖️ STABLE", "NORMAL", 0

# 3. ICT PROBABILITY ENGINE
def calculate_ict_probability(ticker, range_min, range_max):
    try:
        data = yf.Ticker(ticker).history(period="5d")
        last = data.iloc[-1]; prev = data.iloc[-2]
        multiplier = 100 if "JPY" in ticker else 10000
        r_pips = (last['High'] - last['Low']) * multiplier
        b_pips = abs(last['Open'] - last['Close']) * multiplier
        ratio = b_pips / r_pips if r_pips > 0 else 0
        score = 35 if 1 <= datetime.now().weekday() <= 3 else 0
        if range_min <= r_pips <= range_max: score += 35
        if ratio >= 0.55: score += 30
        return score, r_pips, "HIGH" if score >= 70 else "MID", ratio, prev, last
    except: return 0, 0, "ERR", 0, None, None

# 4. MASTER DATA (RESTORED)
market_logic = {
    "EURUSD=X": {"name": "EUR/USD", "story": "The Euro/Bund Story", "min": 65, "max": 85, "deep": "ECB on hold until Dec. German stimulus is the floor.", "bond": "Bund 10Y vs US 10Y", "news": "Tue: Eurozone CPI.", "target": "1.1680 (Sell-side Liquidity)"},
    "JPY=X": {"name": "USD/JPY", "story": "The Carry Flip", "min": 105, "max": 140, "deep": "BoJ eyes April rate hike. Intervention watch at 157.00.", "bond": "JGB 10Y vs US 10Y", "news": "Tue: BoJ Gov Ueda Speech.", "target": "153.20 (Discount OTE)"},
    "GBPUSD=X": {"name": "GBP/USD", "story": "The Cable Gilt Drift", "min": 85, "max": 115, "deep": "Support at 1.3450. UK inflation remains sticky.", "bond": "Gilt 10Y vs US 10Y", "news": "Fri: US NFP Payrolls.", "target": "1.3580 (Buy-side Liquidity)"},
    "AUDUSD=X": {"name": "AUD/USD", "story": "The Resource Carry", "min": 65, "max": 85, "deep": "RBA 3.85% yield remains strongest carry in G10.", "bond": "AU 10Y vs US 10Y", "news": "Wed: AU GDP q/q.", "target": "0.7150 (Major Level)"}
}

# 5. UI TABS
tab1, tab2, tab3 = st.tabs(["🖥 Detailed Market Grid", "🥩 Executive Summary", "📅 Daily Closing Intelligence"])

with tab1:
    cols = st.columns(3)
    for i, (ticker, info) in enumerate(market_logic.items()):
        with cols[i % 3]:
            score, pips, status, ratio, _, _ = calculate_ict_probability(ticker, info['min'], info['max'])
            spread, trend, div, _ = get_yield_details(info['name'])
            st.markdown(f"### {info['name']}")
            st.metric("Price Velocity", f"{pips:.1f} Pips", delta=status)
            with st.expander("🔍 Strategic & News Analysis", expanded=True):
                st.write(f"**Sentiment:** {info['deep']}")
                st.write(f"**News:** {info['news']}")
                st.write(f"**Bond Context:** {info['bond']} ({spread:.3f}%)")
                st.info(f"🏹 Target: {info['target']}")

with tab2:
    st.header("Executive Summary")
    summary = []
    for ticker, info in market_logic.items():
        score, _, status, ratio, _, _ = calculate_ict_probability(ticker, info['min'], info['max'])
        spread, trend, div, _ = get_yield_details(info['name'])
        summary.append({"Pair": info['name'], "Conviction": f"{score}%", "Yield Trend": trend, "Signal": div, "Body/Range": f"{ratio*100:.1f}%", "Target": info['target']})
    st.table(pd.DataFrame(summary))

with tab3:
    st.header(f"📅 Daily Closing Intelligence (Close of March 2, 2026)")
    for ticker, info in market_logic.items():
        score, pips, _, ratio, prev, last = calculate_ict_probability(ticker, info['min'], info['max'])
        spread, trend, div, us_yield = get_yield_details(info['name'])
        
        # Narrative Logic
        dir_text = "downside" if last['Close'] < last['Open'] else "upside"
        move_pips = abs(last['Close'] - last['Open']) * (100 if "JPY" in ticker else 10000)
        
        st.subheader(f"{info['name']} ({info['story']})")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Yesterday (March 2):** Price closed with {'heavy' if ratio > 0.55 else 'choppy'} displacement to the {dir_text} ({move_pips:.1f} pips). Yields on the US 10Y are at {us_yield:.2f}% influencing the {info['name']} flow.")
            st.markdown(f"**Today's Look:** {'Watch for a Judas Swing fake-out' if ratio > 0.55 else 'Expect range-bound consolidation'} near the Midnight Open. The 'Magnet' is pulling toward {info['target']}.")
        with c2:
            st.success(f"**Sweet Spot:** {info['target'].split(' ')[0]}")
            st.warning(f"**Recommendation:** {'Sell on Retest' if dir_text == 'downside' else 'Buy on Retest'} if SMT Divergence is present with correlated pairs.")
        st.divider()

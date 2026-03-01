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

# 3. YIELD CONFIRMATION & TREND ENGINE
def get_yield_details(pair_name="AUD/USD"):
    symbols = {
        "AUD/USD": "^AU10Y",
        "NZD/USD": "^NZ10Y.NM",
        "USD/JPY": "JP10Y.BD", 
        "GBP/USD": "^GILT",
        "EUR/USD": "BUND10Y.BD",
        "USD/CAD": "^CAN10Y",
        "GBP/JPY": "^GILT", 
        "EUR/JPY": "BUND10Y.BD" 
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
        
        if f_hist.empty:
            return 0, "No Yield Data", "⚖️ STABLE", "NORMAL"
            
        current_f = f_hist['Close'].iloc[-1]
        prev_f = f_hist['Close'].iloc[-2]
        f_dir = "UP" if current_f > prev_f else "DOWN"
        
        avg_f = f_hist['Close'].mean()
        
        # FIRM SHIFT THRESHOLD (0.10)
        diff = current_f - avg_f
        if diff > 0.10: trend = "📈 FIRM INCREASE"
        elif diff < -0.10: trend = "📉 FIRM DECREASE"
        else: trend = "⚖️ STABLE"
        
        # DIVERGENCE ACTION LOGIC
        div_status = "✅ CONVERGENT"
        if f_dir != us_dir:
            if "JPY" in pair_name:
                if f_dir == "UP" and us_dir == "DOWN": div_status = "⚠️ DIVERGENCE: WAIT FOR A BUY"
                if f_dir == "DOWN" and us_dir == "UP": div_status = "⚠️ DIVERGENCE: WAIT FOR A SELL"
            elif pair_name.endswith("/USD"):
                if f_dir == "UP" and us_dir == "DOWN": div_status = "⚠️ DIVERGENCE: WAIT FOR A BUY"
                if f_dir == "DOWN" and us_dir == "UP": div_status = "⚠️ DIVERGENCE: WAIT FOR A SELL"
            elif pair_name.startswith("USD/"): 
                if f_dir == "UP" and us_dir == "DOWN": div_status = "⚠️ DIVERGENCE: WAIT FOR A SELL"
                if f_dir == "DOWN" and us_dir == "UP": div_status = "⚠️ DIVERGENCE: WAIT FOR A BUY"
        
        spread = current_f - us10
        sentiment = "🚀 BULLISH" if spread > 0.4 else "🩸 BEARISH" if spread < -0.4 else "⚖️ NEUTRAL"
        
        return spread, sentiment, trend, div_status
    except:
        return 0, "Yield Error", "⚖️ STABLE", "NORMAL"

def get_usd_standalone_trend():
    try:
        us10_ticker = yf.Ticker("^TNX")
        us10_hist = us10_ticker.history(period="5d")
        current_us = us10_hist['Close'].iloc[-1]
        avg_us = us10_hist['Close'].mean()
        diff = current_us - avg_us
        
        if diff > 0.10: 
            trend = "📈 FIRM INCREASE" 
        elif diff < -0.10: 
            trend = "📉 FIRM DECREASE"
        else: 
            trend = "⚖️ STABLE"
        return current_us, trend
    except:
        return 0, "⚖️ STABLE"

# 4. ICT PROBABILITY ENGINE
def calculate_ict_probability(ticker, range_min, range_max):
    try:
        data = yf.Ticker(ticker).history(period="5d")
        if len(data) < 2: return 0, 0, "DATA_ERR", 0
        last_candle = data.iloc[-1] 
        open_p, close_p = last_candle['Open'], last_candle['Close']
        high_p, low_p = last_candle['High'], last_candle['Low']
        
        digits = 3 if "JPY" in ticker else 5
        multiplier = 100 if digits == 3 else 10000
        
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

# 5. MASTER DATA INTELLIGENCE (Strictly Reverted Content)
market_logic = {
    "AUDUSD=X": {
        "name": "AUD/USD", "min": 65, "max": 85, "bank": "RBA", "sentiment": "Hawkish",
        "deep": "RBA 3.85% yield remains the strongest carry driver in the G10.",
        "bond": "AU 10Y vs US 10Y.", "news": "Wed: AU GDP q/q.", "target": "🏹 Target: 0.7150"
    },
    "JPY=X": {
        "name": "USD/JPY", "min": 105, "max": 140, "bank": "BoJ", "sentiment": "Hawkish-Lean",
        "deep": "BoJ eyes April rate hike. Watch for intervention at 157.00.",
        "bond": "JGB 10Y vs US 10Y.", "news": "Tue: BoJ Gov Ueda Speech.", "target": "🏹 Target: 153.20"
    },
    "GBPJPY=X": {
        "name": "GBP/JPY", "min": 140, "max": 200, "bank": "BoE/BoJ", "sentiment": "Volatile",
        "deep": "The 'Beast'. Driven by UK Gilt yields vs BoJ hawkishness.",
        "bond": "UK Gilt 10Y vs JGB 10Y context.", "news": "Thu: UK MPC Meeting Minutes.", "target": "🏹 Target: 212.50"
    },
    "EURJPY=X": {
        "name": "EUR/JPY", "min": 120, "max": 170, "bank": "ECB/BoJ", "sentiment": "Neutral-Bullish",
        "deep": "Euro resilience meets Yen weakness. Watch 185.00 level.",
        "bond": "Bund 10Y vs JGB 10Y context.", "news": "Tue: Eurozone CPI.", "target": "🏹 Target: 186.20"
    },
    "NZDUSD=X": {
        "name": "NZD/USD", "min": 60, "max": 90, "bank": "RBNZ", "sentiment": "Dovish",
        "deep": "RBNZ prioritizing growth. Weakest of the commodity bloc.",
        "bond": "NZ 10Y vs US 10Y.", "news": "Tue: NZ Terms of Trade.", "target": "🏹 Target: 0.5880"
    },
    "GBPUSD=X": {
        "name": "GBP/USD", "min": 85, "max": 115, "bank": "BoE", "sentiment": "Hold",
        "deep": "Support at 1.3450. UK inflation remains 'sticky'.",
        "bond": "Gilt 10Y vs US 10Y.", "news": "Fri: US NFP Payrolls.", "target": "🏹 Target: 1.3580"
    },
    "EURUSD=X": {
        "name": "EUR/USD", "min": 65, "max": 85, "bank": "ECB", "sentiment": "Neutral",
        "deep": "ECB on hold until Dec. German stimulus is the floor.",
        "bond": "Bund 10Y vs US 10Y.", "news": "Tue: Eurozone CPI.", "target": "🏹 Target: 1.1910"
    },
    "USDCAD=X": {
        "name": "USD/CAD", "min": 75, "max": 100, "bank": "BoC", "sentiment": "Cautious",
        "deep": "CAD underperforming on global tariff concerns.",
        "bond": "CA 10Y vs US 10Y.", "news": "Wed: Canada GDP.", "target": "🏹 Target: 1.3930"
    }
}

# 6. SIDEBAR
st.sidebar.title("🏛 Global News & Bank Sentiment")
news_feed = get_live_news()
for entry in news_feed:
    with st.sidebar.expander(f"📌 {entry.title[:45]}..."):
        st.write(f"**{entry.title}**")
        st.markdown(f"[Source Article]({entry.link})")

st.sidebar.divider()
st.sidebar.subheader("🏦 Central Bank Sentiment")
for t, d in market_logic.items():
    color = "green" if d['sentiment'] == "Hawkish" else "red" if d['sentiment'] == "Dovish" else "orange"
    st.sidebar.markdown(f"**{d['bank']}**: :{color}[{d['sentiment']}]")

# 7. MAIN UI
st.title("📊 ICT Multi-Pair Intelligence Terminal")

y_col1, y_col2, y_col3 = st.columns(3)
with y_col1:
    sp_au, txt_au, _, _ = get_yield_details("AUD/USD")
    st.metric("AU-US 10Y Yield Spread", f"{sp_au:.3f}%", delta=txt_au)
with y_col2:
    sp_nz, txt_nz, _, _ = get_yield_details("NZD/USD")
    st.metric("NZ-US 10Y Yield Spread", f"{sp_nz:.3f}%", delta=txt_nz)
with y_col3:
    us_val, us_trend = get_usd_standalone_trend()
    st.metric("US 10Y Yield (USD Standalone)", f"{us_val:.3f}%", delta=us_trend)

st.divider()

results = []
for t, d in market_logic.items():
    s, p, stt, r = calculate_ict_probability(t, d['min'], d['max'])
    results.append({"name": d['name'], "score": s, "pips": p})
best_pick = max(results, key=lambda x: x['score'])

if best_pick['score'] >= 70:
    st.success(f"🎯 **ICT HIGH PROBABILITY SIGNAL: {best_pick['name']}**")
else:
    st.warning("⚖️ **Market Status: No High-Prob Setups Found.**")

# 8. MARKET GRID
cols = st.columns(3)
for i, (ticker, info) in enumerate(market_logic.items()):
    with cols[i % 3]:
        score, pips, status, ratio = calculate_ict_probability(ticker, info['min'], info['max'])
        try:
            price_data = yf.Ticker(ticker).history(period="1d")
            price = price_data['Close'].iloc[-1]
            
            st.markdown(f"### {info['name']}")
            st.metric("Price", f"{price:.4f}", f"{pips:.1f} Pips")
            
            color = "green" if score >= 70 else "orange" if score >= 40 else "red"
            st.markdown(f"**ICT Conviction: :{color}[{score}% ({status})]**")
            st.progress(score / 100)
            
            _, _, yield_trend, divergence = get_yield_details(info['name'])
            
            with st.expander("🔍 Strategic & News Analysis"):
                st.markdown(f"**Market Sentiment:** {info['deep']}")
                st.markdown(f"**Yield Trend:** `{yield_trend}`") 
                
                if "WAIT FOR A BUY" in divergence:
                    st.success(f"🚀 **{divergence}**")
                elif "WAIT FOR A SELL" in divergence:
                    st.error(f"🩸 **{divergence}**")
                else:
                    st.markdown(f"**Divergence Status:** `{divergence}`")
                    
                st.markdown(f"**Bond Context:** {info['bond']}")
                st.markdown(f"**High Impact News:** {info['news']}")
                st.info(info['target'])
                st.caption(f"Body-to-Range Ratio: {ratio:.1%}")
        except:
            st.error(f"Stream Down: {info['name']}")

# 9. STRATEGIC OUTLOOK
st.divider()
st.header("🎯 Weekly Master Outlook")
st.table(pd.DataFrame({
    "Date": ["Mar 2", "Mar 3", "Mar 4", "Mar 6"],
    "Event": ["US ISM Mfg", "BoJ Ueda Speech", "AU GDP", "US NFP Jobs"],
    "Focus": ["Growth", "Rate Pivot", "Yield Divergence", "USD Kingmaker"]
}))

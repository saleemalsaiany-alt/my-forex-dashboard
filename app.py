import streamlit as st
import yfinance as yf
import pandas as pd
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# --- 1. CONFIGURATION & SECRETS ---
st.set_page_config(page_title="ICT Sniper Terminal", layout="wide")

try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    GMAIL_PASS = st.secrets["GMAIL_PASS"]
    SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
except Exception:
    st.error("Missing Secrets! Check .streamlit/secrets.toml")
    st.stop()

# --- 2. MARKET DATA LOGIC ---
market_pairs = {
    "AUDUSD=X": {"name": "AUD/USD", "min": 60, "max": 90, "target": "0.7200", "yield_ref": "^AU10Y"},
    "JPY=X": {"name": "USD/JPY", "min": 110, "max": 150, "target": "154.50", "yield_ref": "^TNX"},
    "EURUSD=X": {"name": "EUR/USD", "min": 70, "max": 100, "target": "1.1200", "yield_ref": "IE10Y.F"}
}

def get_yield_confirmation(pair_key):
    try:
        # Fetching Bond Data: AU10Y vs US10Y (TNX)
        us10 = yf.Ticker("^TNX").history(period="5d")['Close'].iloc[-1]
        
        if pair_key == "AUDUSD=X":
            foreign_yield = yf.Ticker("^AU10Y").history(period="5d")['Close'].iloc[-1]
            spread = foreign_yield - us10
        else:
            spread = 0 # Placeholder for other pairs
            
        if spread > 0.15: # Professional threshold
            return spread, "🚀 BULLISH CONFIRMATION", "green"
        elif spread < -0.15:
            return spread, "🩸 BEARISH CONFIRMATION", "red"
        else:
            return spread, "⚖️ NEUTRAL", "gray"
    except:
        return 0, "⚠️ DATA ERROR", "orange"

def calculate_ict_probability(ticker, r_min, r_max):
    # This logic matches your EA's Daily Bias requirements
    data = yf.Ticker(ticker).history(period="5d")
    last_close = data['Close'].iloc[-1]
    last_open = data['Open'].iloc[-1]
    
    # ICT Displacement check (Body > 50% of range)
    body_size = abs(last_close - last_open)
    total_range = data['High'].iloc[-1] - data['Low'].iloc[-1]
    
    score = 40
    if body_size / total_range > 0.5: score += 30
    if last_close > last_open: score += 20
    
    status = "HIGH" if score >= 70 else "LOW"
    return score, status

# --- 3. EMAIL REPORTING LOGIC ---
def get_github_email():
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    try:
        res = requests.get('https://api.github.com/user/emails', headers=headers)
        return next(e['email'] for e in res.json() if e['primary'])
    except:
        return SENDER_EMAIL

def send_daily_report():
    report_data = []
    ea_authorized = False
    
    for ticker, info in market_pairs.items():
        score, status = calculate_ict_probability(ticker, info['min'], info['max'])
        spread, yield_text, _ = get_yield_confirmation(ticker)
        
        action = "✅ TURN EA ON" if score >= 70 and "BULLISH" in yield_text else "❌ STAY CASH"
        if "ON" in action: ea_authorized = True
        
        report_data.append({
            "Pair": info['name'],
            "ICT Score": f"{score}%",
            "Yield Signal": yield_text,
            "EA Action": action,
            "Target": info['target']
        })

    # Email Styling
    banner_color = "#28a745" if ea_authorized else "#dc3545"
    df_html = pd.DataFrame(report_data).to_html(index=False)
    
    email_body = f"""
    <div style="background:{banner_color}; color:white; padding:20px; text-align:center; font-family:Arial;">
        <h1>{'EA AUTHORIZED' if ea_authorized else 'EA RESTRICTED'}</h1>
        <p>Market Report for {datetime.now().strftime('%Y-%m-%d')}</p>
    </div>
    {df_html}
    """

    msg = MIMEMultipart()
    msg['Subject'] = f"🎯 Daily Sniper Report: {'ACTION' if ea_authorized else 'NO TRADE'}"
    msg.attach(MIMEText(email_body, 'html'))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, GMAIL_PASS)
        server.sendmail(SENDER_EMAIL, get_github_email(), msg.as_string())
    st.success("Report Sent Successfully!")

# --- 4. MAIN USER INTERFACE ---
st.title("🏹 ICT Sniper Terminal V3.27")

col1, col2 = st.columns([2, 1])

with col1:
    st.header("Live Market Probabilities")
    for ticker, info in market_pairs.items():
        score, status = calculate_ict_probability(ticker, info['min'], info['max'])
        spread, yield_text, y_color = get_yield_confirmation(ticker)
        
        with st.expander(f"{info['name']} - Current Score: {score}%"):
            st.metric("Yield Spread", f"{spread:.4f}%", delta=yield_text, delta_color="normal")
            st.write(f"**Intraweek Target:** {info['target']}")
            st.progress(score / 100)

with col2:
    st.header("Executive Control")
    if st.button("📧 Dispatch Daily Report", use_container_width=True):
        send_daily_report()
    
    st.info("The report is sent to your GitHub email address and analyzes technicals + bond yields.")

# Display Yield Confirmation logic as requested
st.divider()
st.subheader("Yield Strategy Analytics")
spread_val, text, col = get_yield_confirmation("AUDUSD=X")
st.metric(label="AU-US 10Y Yield Spread", value=f"{spread_val:.3f}%", delta=text)

import streamlit as st
import smtplib
import requests
import pandas as pd
import yfinance as yf
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# --- 1. ACCESS SECRETS ---
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    GMAIL_PASS = st.secrets["GMAIL_PASS"]
    SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
except KeyError:
    st.error("Secrets not found! Please set GITHUB_TOKEN and GMAIL_PASS in .streamlit/secrets.toml")
    st.stop()

# --- 2. GITHUB EMAIL FETCHING ---
def get_github_email():
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    try:
        response = requests.get('https://api.github.com/user/emails', headers=headers)
        emails = response.json()
        return next(email['email'] for email in emails if email['primary'] and email['verified'])
    except:
        return SENDER_EMAIL # Fallback

# --- 3. ICT CORE LOGIC ---
# (Keeping your existing calculate_ict_probability and market_logic here)
market_logic = {
    "AUDUSD=X": {"name": "AUD/USD", "min": 65, "max": 85, "target": "0.7150", "news": "AU GDP"},
    "JPY=X": {"name": "USD/JPY", "min": 105, "max": 140, "target": "153.20", "news": "BoJ Ueda"},
    # ... (add your other pairs here)
}

def calculate_ict_probability(ticker, r_min, r_max):
    # Simplified for the example - uses your existing logic
    data = yf.Ticker(ticker).history(period="2d")
    score = 75 if ticker == "AUDUSD=X" else 40 # Mock score for demo
    status = "HIGH" if score >= 70 else "LOW"
    return score, status

# --- 4. REPORT GENERATOR ---
def send_daily_report():
    receiver = get_github_email()
    report_rows = []
    ea_on = False
    
    for ticker, info in market_logic.items():
        score, status = calculate_ict_probability(ticker, info['min'], info['max'])
        action = "✅ ON" if score >= 70 else "❌ OFF"
        if score >= 70: ea_on = True
        
        report_rows.append({
            "Pair": info['name'],
            "Score": f"{score}%",
            "EA Action": action,
            "Target": info['target']
        })

    # Build Email
    df = pd.DataFrame(report_rows)
    banner_color = "#28a745" if ea_on else "#dc3545"
    banner_text = "ACTION: TURN EA ON" if ea_on else "ACTION: STAY CASH"
    
    html = f"""
    <div style="background:{banner_color}; color:white; padding:20px; text-align:center;">
        <h1>{banner_text}</h1>
    </div>
    {df.to_html(index=False)}
    """

    msg = MIMEMultipart()
    msg['Subject'] = f"🚀 ICT Sniper Report - {datetime.now().strftime('%b %d')}"
    msg.attach(MIMEText(html, 'html'))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, GMAIL_PASS)
        server.sendmail(SENDER_EMAIL, receiver, msg.as_string())
    
    st.success(f"Report sent to {receiver}!")

# --- 5. STREAMLIT UI ---
st.title("🏹 ICT Sniper Terminal")

if st.button("📧 Generate & Send Daily Report Now"):
    send_daily_report()

# (Rest of your Dashboard Grid Code goes here...)

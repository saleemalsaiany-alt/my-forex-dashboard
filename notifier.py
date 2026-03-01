import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
from datetime import datetime
from app import calculate_ict_probability, market_logic 

# 1. FETCH YOUR GITHUB EMAIL AUTOMATICALLY
def get_github_email(token):
    headers = {'Authorization': f'token {token}'}
    response = requests.get('https://api.github.com/user/emails', headers=headers)
    emails = response.json()
    # Returns the primary, verified email
    return next(email['email'] for email in emails if email['primary'] and email['verified'])

# 2. GENERATE ANALYSIS & EA ACTION
def generate_report():
    report_data = []
    ea_action_required = False
    top_pair = ""

    for ticker, info in market_logic.items():
        score, pips, status, ratio = calculate_ict_probability(ticker, info['min'], info['max'])
        
        # Logic to decide if we turn the EA ON
        action = "❌ STAY CASH"
        if score >= 70:
            action = "✅ TURN EA ON"
            ea_action_required = True
            top_pair = info['name']
        
        report_data.append({
            "Currency": info['name'],
            "ICT Score": f"{score}%",
            "Action": action,
            "Intraweek Target": info['target'],
            "Bond Signal": "Bullish" if "Bullish" in info['bond'] else "Bearish"
        })

    # Build HTML with specific styling for your "Action" column
    df = pd.DataFrame(report_data)
    html_table = df.to_html(index=False, escape=False, classes='table')
    
    # Final Decision Banner
    banner_color = "#28a745" if ea_action_required else "#dc3545"
    banner_text = f"ACTION: TRADE {top_pair}" if ea_action_required else "ACTION: DO NOT TRADE"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="background-color: {banner_color}; color: white; padding: 20px; text-align: center;">
            <h1>{banner_text}</h1>
            <p>Daily Close Analysis for {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
        <h3>Consolidated ICT Strategy Report</h3>
        {html_table}
        <br>
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 5px solid #007bff;">
            <strong>Analyst Note:</strong> Remember the Sniper V3.27 rules: 
            Check for the Liquidity Sweep on M5 before the FVG entry. 
            If it's Monday/Thursday NY Session, skip the trade per your code.
        </div>
    </body>
    </html>
    """
    return html_body, ea_action_required

# 3. SEND THE EMAIL
def send_to_github_user():
    # --- CONFIGURATION ---
    GITHUB_TOKEN = "your_github_token_here" # Generate in Settings > Developer Settings
    GMAIL_APP_PASSWORD = "your_gmail_app_password" 
    SENDER_EMAIL = "your_gmail@gmail.com"
    
    try:
        receiver_email = get_github_email(GITHUB_TOKEN)
        content, is_high_prob = generate_report()
        
        msg = MIMEMultipart()
        msg['Subject'] = f"🎯 ICT Sniper Report: {'ACTION REQUIRED' if is_high_prob else 'No Trade'}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg.attach(MIMEText(content, 'html'))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        
        print(f"Report sent to GitHub email: {receiver_email}")
    except Exception as e:
        print(f"Failed to send: {e}")

if __name__ == "__main__":
    send_to_github_user()

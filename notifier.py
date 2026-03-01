import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
# Import your logic from the main app
from app import calculate_ict_probability, market_logic 

def generate_daily_report():
    report_data = []
    
    # 1. Analyze All Pairs
    for ticker, info in market_logic.items():
        score, pips, status, ratio = calculate_ict_probability(ticker, info['min'], info['max'])
        
        # We only care about high/mid setups for the report
        report_data.append({
            "Pair": info['name'],
            "ICT Score": f"{score}%",
            "Status": status,
            "News Focus": info['news'],
            "Target": info['target']
        })

    # 2. Build the HTML Email Body
    df = pd.DataFrame(report_data)
    html_table = df.to_html(index=False, classes='table table-striped')

    body = f"""
    <html>
      <head>
        <style>
            .high {{ color: green; font-weight: bold; }}
            .header {{ background-color: #1e1e1e; color: white; padding: 20px; }}
        </style>
      </head>
      <body>
        <div class="header">
            <h2>🎯 ICT Sniper: Daily Close Report</h2>
            <p>Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}</p>
        </div>
        <h3>Market Analysis Summary</h3>
        {html_table}
        <br>
        <p><b>Recommendation:</b> If ICT Score > 70%, enable EA for the London session.</p>
      </body>
    </html>
    """
    return body

def send_email(content):
    # Setup your Gmail/Outlook App Password
    SENDER = "saleem.aslaiany@gmail.com"
    PASSWORD = "Saleem!321" 
    RECEIVER = "saleem.alsaiany@gmail.com"

    msg = MIMEMultipart()
    msg['Subject'] = f"🚀 ICT Trading Report: {pd.Timestamp.now().strftime('%b %d')}"
    msg.attach(MIMEText(content, 'html'))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, RECEIVER, msg.as_string())
    print("Report Sent Successfully!")

# Execute manually or via task scheduler at 17:01 EST
if __name__ == "__main__":
    content = generate_daily_report()
    send_email(content)

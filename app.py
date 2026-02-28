import streamlit as st
import yfinance as yf

st.title("My Forex Dashboard")
st.write("If you see this, the app is working!")

# Check if the data connection works
price = yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[-1]
st.metric("Live EUR/USD Price", f"{price:.4f}")

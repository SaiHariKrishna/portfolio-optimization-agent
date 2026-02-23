import yfinance as yf
import pandas as pd

def load_real_yield_data():
    tickers = {
        "2Y": "^IRX",
        "5Y": "^FVX",
        "10Y": "^TNX"
    }

    yields = {}
    for tenor, ticker in tickers.items():
        data = yf.download(ticker, period="5d", interval="1d")
        latest = data["Close"].iloc[-1]
        yields[tenor] = latest / 100  # convert to decimal

    return yields
    
import pandas as pd
import yfinance as yf
import numpy as np

def load_user_portfolio():
    """
    Fetches real-time prices for Treasury ETFs and maps them to index yields
    to create a makeshift live portfolio.
    """
    # Define Tickers with professional names
    tickers = {
        "BIL":  {"name": "iShares 0-3 Month Treasury Bond ETF", "maturity": 0.25},
        "SHY":  {"name": "iShares 1-3 Year Treasury Bond ETF",  "maturity": 2},
        "IEI":  {"name": "iShares 3-7 Year Treasury Bond ETF",  "maturity": 5},
        "VGIT": {"name": "Vanguard Intermediate Treasury ETF",  "maturity": 7},
        "IEF":  {"name": "iShares 7-10 Year Treasury Bond ETF", "maturity": 10},
        "TLH":  {"name": "iShares 10-20 Year Treasury Bond ETF", "maturity": 15},
        "VGLT": {"name": "Vanguard Long-Term Treasury ETF",     "maturity": 20},
        "TLT":  {"name": "iShares 20+ Year Treasury Bond ETF",   "maturity": 25}
    }
    
    # Indices for yields (Proxies)
    # ^IRX (13-week), ^FVX (5-yr), ^TNX (10-yr), ^TYX (30-yr)
    yield_indices = ["^IRX", "^FVX", "^TNX", "^TYX"]
    
    try:
        # Fetch Data
        data = yf.download(list(tickers.keys()) + yield_indices, period="1d", progress=False)
        if data.empty:
            raise ValueError("No data returned from Yahoo Finance")
            
        latest_prices = data["Close"].iloc[-1]
        
        # Mapping maturities to yields (converting from percentage to decimal)
        # Using closest available index proxy
        yield_map = {
            0.25: latest_prices["^IRX"] / 100 if not np.isnan(latest_prices["^IRX"]) else 0.051,
            2:    latest_prices["^IRX"] / 100 if not np.isnan(latest_prices["^IRX"]) else 0.045,
            5:    latest_prices["^FVX"] / 100 if not np.isnan(latest_prices["^FVX"]) else 0.042,
            7:    latest_prices["^FVX"] / 100 if not np.isnan(latest_prices["^FVX"]) else 0.042,
            10:   latest_prices["^TNX"] / 100 if not np.isnan(latest_prices["^TNX"]) else 0.043,
            15:   latest_prices["^TNX"] / 100 if not np.isnan(latest_prices["^TNX"]) else 0.044,
            20:   latest_prices["^TYX"] / 100 if not np.isnan(latest_prices["^TYX"]) else 0.045,
            25:   latest_prices["^TYX"] / 100 if not np.isnan(latest_prices["^TYX"]) else 0.046
        }
        
        # Makeshift quantities for the portfolio
        quantities = {
            "BIL": 400, "SHY": 500, "IEI": 300, "VGIT": 250, 
            "IEF": 200, "TLH": 150, "VGLT": 100, "TLT": 80
        }
        
        portfolio_data = []
        for ticker, info in tickers.items():
            price = latest_prices[ticker]
            if np.isnan(price):
                price = 100.0 # Fallback
                
            yield_val = yield_map[info["maturity"]]
            
            portfolio_data.append({
                "bond_name": info["name"],
                "ticker": ticker,
                "face_value": 100.0,
                "current_price": round(price, 2),
                "quantity": quantities[ticker],
                "coupon": yield_val, # Using yield as proxy for coupon
                "market_yield": yield_val,
                "maturity_years": info["maturity"]
            })
            
        df = pd.DataFrame(portfolio_data)
        
        # Calculate market value and weights
        df["market_value"] = df["quantity"] * df["current_price"]
        total_val = df["market_value"].sum()
        df["weight"] = df["market_value"] / total_val
        
        return df
        
    except Exception as e:
        print(f"Error fetching real-time data: {e}")
        # Fallback to mockup if internet fails
        fallback_data = [
            {"bond_name": "iShares 0-3 Month Treasury (BIL)", "ticker": "BIL", "face_value": 100.0, "current_price": 91.50, "quantity": 400, "coupon": 0.051, "market_yield": 0.051, "maturity_years": 0.25},
            {"bond_name": "iShares 1-3 Year Treasury (SHY)",  "ticker": "SHY", "face_value": 100.0, "current_price": 82.0,  "quantity": 500, "coupon": 0.045, "market_yield": 0.045, "maturity_years": 2},
            {"bond_name": "iShares 3-7 Year Treasury (IEI)",  "ticker": "IEI", "face_value": 100.0, "current_price": 120.0, "quantity": 300, "coupon": 0.042, "market_yield": 0.042, "maturity_years": 5},
            {"bond_name": "iShares 7-10 Year Treasury (IEF)", "ticker": "IEF", "face_value": 100.0, "current_price": 94.0,  "quantity": 200, "coupon": 0.043, "market_yield": 0.043, "maturity_years": 10},
            {"bond_name": "iShares 20+ Year Treasury (TLT)",  "ticker": "TLT", "face_value": 100.0, "current_price": 89.0,  "quantity": 100, "coupon": 0.046, "market_yield": 0.046, "maturity_years": 20}
        ]
        df = pd.DataFrame(fallback_data)
        df["market_value"] = df["quantity"] * df["current_price"]
        df["weight"] = df["market_value"] / df["market_value"].sum()
        return df


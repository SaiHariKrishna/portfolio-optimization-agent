import pandas as pd
import math
from data_loader import load_real_yield_data

def safe_float(x, fallback=0.05):
    try:
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return fallback
        return float(x)
    except Exception:
        return fallback

def load_portfolio():
    yields = load_real_yield_data()

    data = [
        {
            "bond_name": "UST_2Y",
            "face_value": 100.0,
            "coupon": safe_float(yields.get("2Y")),
            "maturity_years": 2,
            "market_yield": safe_float(yields.get("2Y"))
        },
        {
            "bond_name": "UST_5Y",
            "face_value": 100.0,
            "coupon": safe_float(yields.get("5Y")),
            "maturity_years": 5,
            "market_yield": safe_float(yields.get("5Y"))
        },
        {
            "bond_name": "UST_10Y",
            "face_value": 100.0,
            "coupon": safe_float(yields.get("10Y")),
            "maturity_years": 10,
            "market_yield": safe_float(yields.get("10Y"))
        }
    ]

    return pd.DataFrame(data)

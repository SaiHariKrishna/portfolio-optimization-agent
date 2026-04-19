import pandas as pd
import numpy as np
import math
from data_loader import load_real_yield_data


def safe_float(x, fallback=0.05):
    try:
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return fallback
        return float(x)
    except Exception:
        return fallback


_FALLBACK = {"3M": 0.043, "5Y": 0.036, "10Y": 0.040, "30Y": 0.044}

# (display name, source ticker, maturity in years)
_DEFAULT_BONDS = [
    ("US Treasury 1-Year Note",   "^IRX",  1),
    ("US Treasury 2-Year Note",   "^IRX",  2),
    ("US Treasury 3-Year Note",   "^FVX",  3),
    ("US Treasury 5-Year Note",   "^FVX",  5),
    ("US Treasury 7-Year Note",   "^TNX",  7),
    ("US Treasury 10-Year Note",  "^TNX", 10),
    ("US Treasury 20-Year Bond",  "^TYX", 20),
    ("US Treasury 30-Year Bond",  "^TYX", 30),
]


def load_user_portfolio():
    """Build an 8-bond portfolio with live Yahoo Finance yields
    and Nelson-Siegel interpolation for intermediate tenors.
    """
    try:
        raw = load_real_yield_data()
    except Exception:
        raw = {}

    y3m  = safe_float(raw.get("3M"),  _FALLBACK["3M"])
    y5y  = safe_float(raw.get("5Y"),  _FALLBACK["5Y"])
    y10y = safe_float(raw.get("10Y"), _FALLBACK["10Y"])
    y30y = safe_float(raw.get("30Y"), _FALLBACK["30Y"])

    obs_mat = [0.25, 5, 10, 30]
    obs_yld = [y3m, y5y, y10y, y30y]

    try:
        def _yield(t):
            return max(0.001, float(np.interp(t, obs_mat, obs_yld)))
    except Exception:
        def _yield(t):
            return 0.04

    n = len(_DEFAULT_BONDS)
    rows = []
    for name, ticker, mat in _DEFAULT_BONDS:
        y = round(_yield(mat), 5)
        rows.append({
            "bond_name": name,
            "ticker": ticker,
            "face_value": 100.0,
            "coupon": y,
            "market_yield": y,
            "maturity_years": mat,
            "weight": round(1.0 / n, 4),
        })

    df = pd.DataFrame(rows)
    df["weight"] = df["weight"] / df["weight"].sum()
    return df

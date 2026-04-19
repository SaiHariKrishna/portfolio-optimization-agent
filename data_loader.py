import yfinance as yf
import pandas as pd

# Available Yahoo Finance treasury yield tickers
YF_YIELD_TICKERS = {
    "3M": "^IRX",
    "5Y": "^FVX",
    "10Y": "^TNX",
    "30Y": "^TYX",
}

# Maturity hint for well-known tickers
_MATURITY_HINT = {"^IRX": 1, "^FVX": 5, "^TNX": 10, "^TYX": 30}


def _closest_ticker(maturity_years):
    """Map a bond maturity to the closest YF yield ticker."""
    mat = float(maturity_years)
    if mat <= 2:
        return "^IRX"
    elif mat <= 6:
        return "^FVX"
    elif mat <= 15:
        return "^TNX"
    else:
        return "^TYX"


# ── Live yields ──────────────────────────────────────────

def load_real_yield_data():
    """Fetch latest US Treasury yields from Yahoo Finance."""
    yields = {}
    for tenor, ticker in YF_YIELD_TICKERS.items():
        try:
            data = yf.download(ticker, period="5d", interval="1d", progress=False)
            if data.empty:
                continue
            close = data["Close"]
            if hasattr(close, "columns"):
                close = close.iloc[:, 0]
            yields[tenor] = float(close.iloc[-1]) / 100
        except Exception:
            continue
    return yields


# ── Historical yields (for VaR) ──────────────────────────

def load_historical_yields(bonds, period="1y"):
    """Load historical daily yield data for portfolio bonds."""
    frames, downloaded = {}, {}
    for b in bonds:
        name = b["bond_name"]
        ticker = b.get("ticker") or _closest_ticker(b["maturity_years"])
        if ticker not in downloaded:
            try:
                data = yf.download(ticker, period=period, interval="1d", progress=False)
                if data.empty:
                    continue
                close = data["Close"]
                if hasattr(close, "columns"):
                    close = close.iloc[:, 0]
                downloaded[ticker] = close / 100
            except Exception:
                continue
        if ticker in downloaded:
            frames[name] = downloaded[ticker]
    if not frames:
        return pd.DataFrame()
    return pd.DataFrame(frames).dropna()


# ── Yahoo Finance bond / security lookup ─────────────────

def fetch_bond_info(ticker):
    """Fetch security info from Yahoo Finance for the 'Add Bond' flow.

    Returns dict with name, ticker, current_yield, current_price,
    suggested_maturity, type … or None on failure.
    """
    ticker = ticker.strip().upper()
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}

        name = info.get("shortName") or info.get("longName") or ticker
        price = info.get("regularMarketPrice") or info.get("previousClose") or 0
        price = float(price)

        if ticker.startswith("^"):
            current_yield = price / 100          # yield indices: price IS yield
            sec_type = "Treasury Yield Index"
        else:
            yld = info.get("yield") or info.get("trailingAnnualDividendYield") or 0
            current_yield = float(yld) if yld else 0.04
            sec_type = info.get("quoteType") or "ETF"

        return {
            "name": name,
            "ticker": ticker,
            "current_yield": round(current_yield, 5),
            "current_price": round(price, 2),
            "suggested_maturity": _MATURITY_HINT.get(ticker, 5),
            "type": sec_type,
            "exchange": info.get("exchange", ""),
            "currency": info.get("currency", "USD"),
        }

    except Exception:
        # Fallback: lightweight download only
        try:
            data = yf.download(ticker, period="5d", progress=False)
            if data.empty:
                return None
            close = data["Close"]
            if hasattr(close, "columns"):
                close = close.iloc[:, 0]
            price = float(close.iloc[-1])
            is_yield = ticker.startswith("^")
            return {
                "name": ticker,
                "ticker": ticker,
                "current_yield": round(price / 100, 5) if is_yield else 0.04,
                "current_price": round(price, 2),
                "suggested_maturity": _MATURITY_HINT.get(ticker, 5),
                "type": "Yield Index" if is_yield else "Security",
                "exchange": "",
                "currency": "USD",
            }
        except Exception:
            return None

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from user_portfolio import load_user_portfolio
from agent import portfolio_agent
from intent import classify_intent, extract_target_duration

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="OptiMarket — Autonomous Portfolio Agent",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# 🎨 Inject custom CSS
# -----------------------------
st.markdown("""
<style>
/* ── Google font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root variables ── */
:root {
    --bg-primary: #0a0e1a;
    --bg-card: rgba(16, 22, 40, 0.75);
    --bg-card-hover: rgba(22, 30, 55, 0.85);
    --accent-blue: #4f8cff;
    --accent-cyan: #00d4ff;
    --accent-purple: #a855f7;
    --accent-green: #34d399;
    --accent-amber: #fbbf24;
    --accent-rose: #f43f5e;
    --text-primary: #f1f5f9;
    --text-muted: #94a3b8;
    --border-glass: rgba(255,255,255,0.06);
    --shadow-glow: 0 0 30px rgba(79,140,255,0.08);
}

/* ── Global ── */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #111827 40%, #0f172a 100%) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    backdrop-filter: blur(20px);
}

/* ── Headers ── */
h1 { font-weight: 800 !important; letter-spacing: -0.5px !important; }
h2, .stSubheader {
    font-weight: 600 !important;
    color: var(--text-primary) !important;
}

/* ── Glass card mixin ── */
.glass-card {
    background: var(--bg-card);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-glass);
    border-radius: 16px;
    padding: 24px 28px;
    box-shadow: var(--shadow-glow);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 40px rgba(79,140,255,0.15);
}

/* ── Metric cards ── */
div[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-glass) !important;
    border-radius: 14px !important;
    padding: 20px 22px !important;
    box-shadow: var(--shadow-glow);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 8px 40px rgba(79,140,255,0.18) !important;
    border-color: var(--accent-blue) !important;
}
div[data-testid="stMetric"] label {
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    font-size: 1.8rem !important;
}

/* ── Dataframes ── */
div[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden;
    border: 1px solid var(--border-glass) !important;
}

/* ── Buttons ── */
button[data-testid="stBaseButton-secondary"] {
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 0 !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.4px !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease !important;
}
button[data-testid="stBaseButton-secondary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(79,140,255,0.35) !important;
}

/* ── Selectbox / Text input ── */
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stTextInput"] > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    transition: border-color 0.3s ease !important;
}
div[data-testid="stSelectbox"] > div > div:focus-within,
div[data-testid="stTextInput"] > div > div > input:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 2px rgba(79,140,255,0.15) !important;
}

/* ── Dividers ── */
hr {
    border-color: var(--border-glass) !important;
}

/* ── Fade-in animation ── */
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
.stMainBlockContainer > div > div > div > div {
    animation: fadeSlideIn 0.5s ease forwards;
}

/* stagger children */
.stMainBlockContainer > div > div > div > div:nth-child(2) { animation-delay: 0.05s; }
.stMainBlockContainer > div > div > div > div:nth-child(3) { animation-delay: 0.10s; }
.stMainBlockContainer > div > div > div > div:nth-child(4) { animation-delay: 0.15s; }
.stMainBlockContainer > div > div > div > div:nth-child(5) { animation-delay: 0.20s; }
.stMainBlockContainer > div > div > div > div:nth-child(6) { animation-delay: 0.25s; }
.stMainBlockContainer > div > div > div > div:nth-child(7) { animation-delay: 0.30s; }
.stMainBlockContainer > div > div > div > div:nth-child(8) { animation-delay: 0.35s; }

/* ── Success / Warning / Info boxes ── */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    backdrop-filter: blur(10px) !important;
}

/* ── Spinner ── */
div[data-testid="stSpinner"] > div { color: var(--accent-cyan) !important; }

</style>
""", unsafe_allow_html=True)

# ── Plotly theme helpers ──────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0", size=13),
    legend=dict(
        bgcolor="rgba(16,22,40,0.6)", bordercolor="rgba(255,255,255,0.06)",
        borderwidth=1, font=dict(size=12)
    ),
)
GRID_STYLE = dict(gridcolor="rgba(255,255,255,0.05)", gridwidth=1)
PALETTE = ["#4f8cff", "#a855f7", "#34d399", "#fbbf24", "#f43f5e", "#00d4ff"]


# ─────────────────────────────────────────────────────────
# Title
# ─────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center; background: linear-gradient(90deg,#4f8cff,#a855f7,#00d4ff);"
    "-webkit-background-clip:text; -webkit-text-fill-color:transparent;"
    "font-size:2.6rem; margin-bottom:4px;'>OptiMarket</h1>"
    "<p style='text-align:center; color:#94a3b8; font-size:1.05rem; margin-top:0;'>"
    "Autonomous Portfolio Agent</p>",
    unsafe_allow_html=True,
)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────
if "portfolio" not in st.session_state:
    st.session_state.portfolio = load_user_portfolio()
portfolio = st.session_state.portfolio

# ─────────────────────────────────────────────────────────
# Compute risk metrics up-front
# ─────────────────────────────────────────────────────────
from risk_metrics import modified_duration, bond_convexity

avg_yield = np.average(portfolio["market_yield"], weights=portfolio["weight"])
avg_dur = np.average(portfolio["maturity_years"], weights=portfolio["weight"])

convexities, durations_list = [], []
for _, row in portfolio.iterrows():
    d = modified_duration(row["face_value"], row["coupon"],
                          row["maturity_years"], row["market_yield"])
    c = bond_convexity(row["face_value"], row["coupon"],
                       row["maturity_years"], row["market_yield"])
    durations_list.append(d)
    convexities.append(c)

avg_conv = np.average(convexities, weights=portfolio["weight"])

# ─────────────────────────────────────────────────────────
# Row 1:  Portfolio table + Pie chart
# ─────────────────────────────────────────────────────────
st.markdown("### 📋 Current Portfolio")

left, right = st.columns([3, 2], gap="large")

# Build a display-friendly copy
display_cols = ["bond_name", "ticker", "maturity_years", "coupon", "market_yield", "weight"]
has_ticker = "ticker" in portfolio.columns
if not has_ticker:
    display_cols = [c for c in display_cols if c != "ticker"]
display_df = portfolio[display_cols].copy()
display_df.columns = (
    ["Bond", "Ticker", "Maturity", "Coupon", "Yield", "Weight"]
    if has_ticker
    else ["Bond", "Maturity", "Coupon", "Yield", "Weight"]
)

with left:
    fmt = {"Coupon": "{:.3f}", "Yield": "{:.3f}", "Weight": "{:.2%}"}
    st.dataframe(display_df.style.format(fmt), use_container_width=True, hide_index=True)

with right:
    fig_pie = go.Figure(go.Pie(
        labels=portfolio["bond_name"],
        values=portfolio["weight"],
        hole=0.52,
        marker=dict(colors=PALETTE[:len(portfolio)],
                    line=dict(color="#0a0e1a", width=2)),
        textinfo="percent",
        textfont=dict(size=12, color="#e2e8f0"),
        hovertemplate="%{label}<br>Weight: %{percent}<extra></extra>",
    ))
    fig_pie.update_layout(
        **PLOTLY_LAYOUT,
        showlegend=False,
        title=dict(text="Allocation", font=dict(size=15, color="#94a3b8"),
                   x=0.5, xanchor="center"),
        height=320,
        margin=dict(l=10, r=10, t=45, b=10),
        annotations=[dict(text="<b>Bonds</b>", x=0.5, y=0.5, font_size=14,
                          font_color="#94a3b8", showarrow=False)],
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ─────────────────────────────────────────────────────────
# Portfolio Management — Add / Remove bonds
# ─────────────────────────────────────────────────────────
with st.expander("🔧 Manage Portfolio — Add / Remove Bonds", expanded=False):
    add_tab, del_tab = st.tabs(["🔍 Add via Yahoo Finance", "🗑️ Remove Bonds"])

    # ── ADD TAB ──
    with add_tab:
        st.caption("Search any Yahoo Finance ticker to fetch live bond / ETF data.")
        sc1, sc2 = st.columns([5, 1])
        ticker_query = sc1.text_input(
            "Ticker Symbol",
            placeholder="^TNX, ^TYX, TLT, LQD, HYG, AGG, IEF …",
            key="ticker_search",
        )
        search_clicked = sc2.button("🔍", use_container_width=True, key="search_btn")

        if search_clicked and ticker_query.strip():
            with st.spinner("Fetching from Yahoo Finance …"):
                from data_loader import fetch_bond_info
                result = fetch_bond_info(ticker_query.strip())
                if result:
                    st.session_state.bond_search = result
                else:
                    st.error(f"Ticker **{ticker_query}** not found on Yahoo Finance.")
                    st.session_state.pop("bond_search", None)

        if "bond_search" in st.session_state:
            info = st.session_state.bond_search
            yld_display = f"{info['current_yield']*100:.2f}%"

            # Fintech info card
            st.markdown(f"""
            <div style='background:rgba(16,22,40,0.85); border:1px solid rgba(79,140,255,0.25);
                        border-left:4px solid #4f8cff; border-radius:14px;
                        padding:18px 22px; margin:10px 0;'>
              <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                  <div style='font-size:1.15rem; font-weight:700; color:#f1f5f9;'>{info['name']}</div>
                  <div style='margin-top:5px;'>
                    <span style='background:rgba(79,140,255,0.15); color:#4f8cff;
                                 padding:3px 10px; border-radius:6px; font-size:0.8rem;
                                 font-weight:600;'>{info['ticker']}</span>
                    <span style='color:#64748b; font-size:0.82rem; margin-left:8px;'>
                      {info['type']}  ·  {info['currency']}</span>
                  </div>
                </div>
                <div style='text-align:right;'>
                  <div style='font-size:1.7rem; font-weight:800; color:#34d399;'>{yld_display}</div>
                  <div style='color:#64748b; font-size:0.72rem; text-transform:uppercase;
                              letter-spacing:0.5px;'>Current Yield</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("add_searched_bond", clear_on_submit=False):
                f1, f2, f3 = st.columns(3)
                add_mat  = f1.number_input("Maturity (yrs)", value=info["suggested_maturity"],
                                           min_value=1, max_value=50)
                add_face = f2.number_input("Face Value", value=100.0, min_value=1.0)
                add_wt   = f3.number_input("Weight", value=0.10, min_value=0.01,
                                           max_value=0.50, step=0.01, format="%.2f")
                add_submit = st.form_submit_button("➕ Add to Portfolio",
                                                    use_container_width=True)
            if add_submit:
                if info["name"] in portfolio["bond_name"].values:
                    st.error(f"'{info['name']}' is already in the portfolio.")
                else:
                    new_row = pd.DataFrame([{
                        "bond_name": info["name"],
                        "ticker": info["ticker"],
                        "face_value": add_face,
                        "coupon": info["current_yield"],
                        "market_yield": info["current_yield"],
                        "maturity_years": int(add_mat),
                        "weight": add_wt,
                    }])
                    updated = pd.concat([portfolio, new_row], ignore_index=True)
                    updated["weight"] = updated["weight"] / updated["weight"].sum()
                    st.session_state.portfolio = updated
                    st.session_state.pop("bond_search", None)
                    st.session_state.pop("historical_yields", None)
                    st.success(f"✅ Added **{info['name']}** ({info['ticker']})")
                    st.rerun()

    # ── DELETE TAB ──
    with del_tab:
        options = portfolio["bond_name"].tolist()
        to_delete = st.multiselect("Select bonds to remove", options=options)
        if st.button("Remove Selected", use_container_width=True):
            if not to_delete:
                st.warning("Select at least one bond.")
            elif len(to_delete) >= len(portfolio):
                st.error("Cannot remove all bonds — keep at least one.")
            else:
                updated = portfolio[~portfolio["bond_name"].isin(to_delete)].reset_index(drop=True)
                updated["weight"] = updated["weight"] / updated["weight"].sum()
                st.session_state.portfolio = updated
                st.session_state.pop("historical_yields", None)
                st.success(f"Removed {len(to_delete)} bond(s). Weights renormalized.")
                st.rerun()


# ─────────────────────────────────────────────────────────
# Row 2: Key metrics
# ─────────────────────────────────────────────────────────
m1, m2, m3 = st.columns(3)
m1.metric("Avg Portfolio Yield", f"{avg_yield*100:.2f}%")
m2.metric("Avg Modified Duration", f"{avg_dur:.2f} yrs")
m3.metric("Wtd Avg Convexity", f"{avg_conv:.2f}")

# ─────────────────────────────────────────────────────────
# Row 3: VaR
# ─────────────────────────────────────────────────────────
st.markdown("###  Value at Risk")

try:
    from data_loader import load_historical_yields
    from var_models import compute_var_metrics

    if "historical_yields" not in st.session_state:
        with st.spinner("Fetching historical yield data …"):
            st.session_state.historical_yields = load_historical_yields(
                portfolio.to_dict(orient="records")
            )

    hist = st.session_state.historical_yields

    if hist is not None and not hist.empty:
        bnames = portfolio["bond_name"].tolist()
        avail = [c for c in bnames if c in hist.columns]
        if len(avail) == len(bnames):
            var = compute_var_metrics(
                hist[bnames].values, durations_list,
                portfolio["weight"].tolist(),
            )
            v1, v2, v3 = st.columns(3)
            v1.metric("Historical VaR (95 %)", f"{var['historical_var']*100:.4f}%")
            v2.metric("Parametric VaR (95 %)", f"{var['parametric_var']*100:.4f}%")
            v3.metric("Expected Shortfall", f"{var['expected_shortfall']*100:.4f}%")
            st.caption(
                f"Based on {var['n_observations']} daily observations (~1 yr). "
                "Negative values = potential daily loss."
            )
        else:
            st.info("Historical yield columns do not match portfolio bonds.")
    else:
        st.info("Historical yield data unavailable — VaR skipped.")
except Exception as e:
    st.warning(f"VaR unavailable: {e}")


# ─────────────────────────────────────────────────────────
# Agent input
# ─────────────────────────────────────────────────────────
st.markdown("###  Ask the Agent")

user_query = st.text_input(
    "What would you like the agent to do?",
    placeholder="e.g.  Reduce duration to 3 years but keep yield stable",
)

opt_method = st.selectbox(
    "Optimization Strategy",
    options=["original", "mean_variance"],
    format_func=lambda x: {
        "original": "  Duration-Target (Original)",
        "mean_variance": "  Mean-Variance (Max Sharpe / Min Vol)",
    }[x],
)

# ─────────────────────────────────────────────────────────
# Run agent
# ─────────────────────────────────────────────────────────
if st.button(" Run Agent", use_container_width=True):

    if not user_query.strip():
        st.warning("Please enter a request first.")
        st.stop()

    intent = classify_intent(user_query)
    target_duration = extract_target_duration(user_query)
    before_weights = portfolio["weight"].tolist()

    with st.spinner("Agent reasoning …"):
        state = {
            "bonds": portfolio.to_dict(orient="records"),
            "target_duration": target_duration,
            "user_query": user_query,
            "intent": intent,
            "optimization_method": opt_method,
        }
        result = portfolio_agent.invoke(state)

    st.success("Agent completed successfully ✨")

    st.markdown("#### 🧠 Lead Reasoning Agent")
    
    # Render the styled header
    st.markdown(f"""
    <div style='background:rgba(20,26,48,0.7); border:1px solid rgba(79,140,255,0.25); 
                border-radius:14px 14px 0 0; padding:15px 20px; border-left: 5px solid #4f8cff;
                border-bottom: 0px;'>
      <div style='display:flex; align-items:center;'>
        <span style='background:linear-gradient(45deg, #4f8cff, #a855f7); color:white; 
                     padding:3px 10px; border-radius:40px; font-size:0.75rem; 
                     font-weight:700; text-transform:uppercase; letter-spacing:0.5px;'>
          AI Reasoning
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Render the markdown explanation within a container
    with st.container():
        st.markdown(f"<div style='background:rgba(20,26,48,0.7); border:1px solid rgba(79,140,255,0.25); border-radius: 0 0 14px 14px; padding:20px; border-left: 5px solid #4f8cff; border-top: 0px; margin-bottom: 10px;'>", unsafe_allow_html=True)
        st.markdown(result.get('explanation', 'Reasoning unavailable.'))
        st.markdown("</div>", unsafe_allow_html=True)

    if intent == "EXPLAIN_ONLY":
        st.info("No portfolio changes were made (explanation only).")
        st.stop()

    # ── Apply weights ──
    updated = portfolio.copy()
    updated["weight"] = result["optimized_weights"]
    updated["weight"] = updated["weight"] / updated["weight"].sum()
    st.session_state.portfolio = updated
    portfolio = st.session_state.portfolio

    # ── Updated portfolio ──
    st.markdown("####  Updated Portfolio")
    st.dataframe(portfolio.style.format({
        "face_value": "{:.0f}", "coupon": "{:.3f}",
        "market_yield": "{:.3f}", "weight": "{:.2%}",
    }), use_container_width=True, hide_index=True)

    # ── Duration & Convexity table ──
    if "convexities" in result:
        st.markdown("#### Bond-Level Duration & Convexity")
        dc_df = pd.DataFrame({
            "Bond": portfolio["bond_name"],
            "Mod Duration": [round(d, 4) for d in result["durations"]],
            "Convexity": [round(c, 4) for c in result["convexities"]],
            "Weight": portfolio["weight"],
        })
        st.dataframe(dc_df.style.format({"Weight": "{:.2%}"}),
                      use_container_width=True, hide_index=True)

    # ── Rebalancing bar chart (Plotly) ──
    st.markdown("#### Portfolio Rebalancing")
    after_weights = portfolio["weight"].tolist()
    bnames = portfolio["bond_name"].tolist()

    fig_reb = go.Figure()
    fig_reb.add_trace(go.Bar(
        x=bnames, y=before_weights, name="Before",
        marker=dict(color="rgba(79,140,255,0.7)",
                    line=dict(width=0), cornerradius=6),
    ))
    fig_reb.add_trace(go.Bar(
        x=bnames, y=after_weights, name="After",
        marker=dict(color="rgba(168,85,247,0.8)",
                    line=dict(width=0), cornerradius=6),
    ))
    fig_reb.update_layout(
        **PLOTLY_LAYOUT, barmode="group", height=370,
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(**GRID_STYLE), yaxis=dict(title="Weight", **GRID_STYLE),
        title=dict(text="Allocation: Before vs After", x=0.5,
                   xanchor="center", font=dict(size=15, color="#94a3b8")),
    )
    st.plotly_chart(fig_reb, use_container_width=True)

    # ── Interest-rate risk (Plotly) ──
    st.markdown("####  Interest Rate Risk Exposure")
    risk_exp = [d * w for d, w in zip(result["durations"], portfolio["weight"])]

    fig_risk = go.Figure(go.Bar(
        x=bnames, y=risk_exp,
        marker=dict(
            color=risk_exp,
            colorscale=[[0, "#34d399"], [0.5, "#fbbf24"], [1, "#f43f5e"]],
            cornerradius=6,
        ),
        hovertemplate="%{x}<br>D × W = %{y:.4f}<extra></extra>",
    ))
    fig_risk.update_layout(
        **PLOTLY_LAYOUT, height=350,
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(**GRID_STYLE), yaxis=dict(title="Duration × Weight", **GRID_STYLE),
        title=dict(text="Contribution to Interest Rate Risk", x=0.5,
                   xanchor="center", font=dict(size=15, color="#94a3b8")),
    )
    st.plotly_chart(fig_risk, use_container_width=True)

    # ── Updated pie ──
    st.markdown("####  New Allocation")
    fig_pie2 = go.Figure(go.Pie(
        labels=bnames, values=after_weights, hole=0.52,
        marker=dict(colors=PALETTE[:len(bnames)],
                    line=dict(color="#0a0e1a", width=2)),
        textinfo="label+percent",
        textfont=dict(size=13, color="#e2e8f0"),
    ))
    fig_pie2.update_layout(
        **PLOTLY_LAYOUT, showlegend=False, height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        annotations=[dict(text="<b>After</b>", x=0.5, y=0.5, font_size=14,
                          font_color="#94a3b8", showarrow=False)],
    )
    st.plotly_chart(fig_pie2, use_container_width=True)

# ─────────────────────────────────────────────────────────
# Reset
# ─────────────────────────────────────────────────────────
st.divider()

if st.button("🔄  Reset Portfolio", use_container_width=True):
    st.session_state.portfolio = load_user_portfolio()
    if "historical_yields" in st.session_state:
        del st.session_state["historical_yields"]
    st.success("Portfolio restored to defaults.")

    st.rerun()

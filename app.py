import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from user_portfolio import load_user_portfolio
from agent import portfolio_agent
from intent import classify_intent, extract_target_duration

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="OptiMarket: Autonomous Portfolio Agent",
    page_icon="📈",
    layout="wide"
)

# -----------------------------
# Premium Styling (CSS)
# -----------------------------
st.markdown("""
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Metric Card Styling */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        color: #50E3C2 !important;
    }
    
    /* Button Styling */
    .stButton > button {
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        background: rgba(255,255,255,0.05) !important;
        color: white !important;
        transition: all 0.3s ease !important;
        height: 3em !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background: rgba(80, 227, 194, 0.2) !important;
        border-color: #50E3C2 !important;
        transform: translateY(-2px);
    }
    
    /* Action Button (Run Agent) */
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .stButton > button {
        background: linear-gradient(90deg, #4A90E2, #50E3C2) !important;
        color: #0E1117 !important;
        border: none !important;
    }
    
    /* Chat Input Styling */
    .stChatInputContainer {
        border-radius: 12px !important;
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    /* Center alignment for the Control Row */
    [data-testid="column"] {
        display: flex !important;
        justify-content: center !important;
    }

    /* Target the chat input container specifically to remove its default bottom spacing */
    .stChatInputContainer {
        margin-bottom: 0px !important;
    }

    /* Ensure buttons align to the center line */
    .stButton {
        display: flex;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("OptiMarket")
st.markdown("<p style='opacity: 0.7; margin-top: -15px;'>Autonomous Bond Portfolio Intelligence & Optimization</p>", unsafe_allow_html=True)

# -----------------------------
# Initialize session portfolio
# -----------------------------
if "portfolio" not in st.session_state:
    st.session_state.portfolio = load_user_portfolio()

# Always read portfolio FROM session state
portfolio = st.session_state.portfolio

# -----------------------------
# Display current portfolio
# -----------------------------
st.subheader("Current Portfolio")

col_table, col_pie = st.columns([2, 1])

with col_table:
    st.dataframe(portfolio, width="stretch", height=300)

with col_pie:
    # Allocation Donut Chart
    fig_pie = px.pie(
        portfolio, 
        values='weight', 
        names='bond_name', 
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig_pie.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=300,
        showlegend=False,
        annotations=[dict(text='Allocation', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------
# Portfolio snapshot
# -----------------------------
avg_yield = np.average(
    portfolio["market_yield"],
    weights=portfolio["weight"]
)
avg_duration = np.average(
    portfolio["maturity_years"],
    weights=portfolio["weight"]
)
total_value = portfolio["market_value"].sum() if "market_value" in portfolio.columns else 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Portfolio Yield", f"{avg_yield*100:.2f}%")
col2.metric("Avg Duration", f"{avg_duration:.2f} yrs")
col3.metric("Total Portfolio Value", f"${total_value:,.2f}")
col4.metric("Convexity Risk", "LOW")

st.divider()

# -----------------------------
# Integrated Interface (Input + Controls)
# -----------------------------
st.markdown("<br>", unsafe_allow_html=True)

# Using a single row for the input and the functional buttons
ui_col1, ui_col2, ui_col3 = st.columns([5, 1, 1], vertical_alignment="center")

with ui_col1:
    user_query = st.chat_input("Ask OptiMarket: 'Reduce duration to 4 years' or 'Analyze my risk'...")

with ui_col2:
    # Using Material Icons (Streamlit 1.32+)
    if st.button("Sync", icon=":material/sync:", use_container_width=True, help="Update live market prices"):
        st.session_state.portfolio = load_user_portfolio()
        st.rerun()

with ui_col3:
    if st.button("Reset", icon=":material/restart_alt:", use_container_width=True, help="Back to original settings"):
        st.session_state.portfolio = load_user_portfolio()
        st.toast("Portfolio reset.", icon="🗑️")
        st.rerun()

# -----------------------------
# Run agent
# -----------------------------
if user_query:

    if user_query.strip() == "":
        st.warning("Please enter a request.")
        st.stop()

    intent = classify_intent(user_query)
    target_duration = extract_target_duration(user_query)

    # Keep BEFORE weights for plotting
    before_weights = portfolio["weight"].tolist()

    with st.spinner("Agent reasoning..."):
        state = {
            "bonds": portfolio.to_dict(orient="records"),
            "target_duration": target_duration,
            "user_query": user_query,
            "intent": intent
        }

        result = portfolio_agent.invoke(state)

    st.success("Agent completed successfully")

    # -----------------------------
    # Explanation / Answer
    # -----------------------------
    if intent == "QUERY":
        st.subheader("🤖 Agent Answer")
    elif intent == "SUGGEST":
        st.subheader("💡 Agent Suggestions")
    else:
        st.subheader("✅ Optimization Result")
        
    st.write(result.get("explanation", "Explanation unavailable."))

    # -----------------------------
    # Skip updates if not OPTIMIZE
    # -----------------------------
    if intent in ["QUERY", "SUGGEST"]:
        st.info("No portfolio changes were made.")
        st.stop()

    # -----------------------------
    # APPLY AGENT ACTION (Optimization)
    # -----------------------------
    updated_portfolio = portfolio.copy()
    updated_portfolio["weight"] = result["optimized_weights"]

    # Normalize weights (safety)
    updated_portfolio["weight"] = (
        updated_portfolio["weight"] /
        updated_portfolio["weight"].sum()
    )

    # ✅ Persist update in session state
    st.session_state.portfolio = updated_portfolio

    # ✅ Rebind local reference (CRITICAL)
    portfolio = st.session_state.portfolio

    # -----------------------------
    # Show updated portfolio
    # -----------------------------
    st.subheader("Updated Portfolio")
    st.dataframe(portfolio, width="stretch")

    # -----------------------------
    # Graph 1: Allocation Rebalancing (Trading Style)
    # -----------------------------
    st.subheader("⚖ Portfolio Rebalancing")

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=portfolio["bond_name"],
        y=before_weights,
        name='Previous Allocation',
        marker_color='#4A90E2', # Soft Blue
        opacity=0.8
    ))
    fig1.add_trace(go.Bar(
        x=portfolio["bond_name"],
        y=portfolio["weight"].tolist(),
        name='Optimized Allocation',
        marker_color='#50E3C2', # Emerald/Teal
        opacity=0.9
    ))

    fig1.update_layout(
        barmode='group',
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="Portfolio Weight",
        xaxis_title="Bond ETF",
        font=dict(family="Outfit, sans-serif", size=12)
    )
    st.plotly_chart(fig1, use_container_width=True)

    # -----------------------------
    # Graph 2: Duration Risk Exposure
    # -----------------------------
    st.subheader("Interest Rate Risk Exposure")

    risk_exposure = [
        d * w for d, w in zip(result["durations"], portfolio["weight"])
    ]

    fig2 = px.bar(
        x=portfolio["bond_name"],
        y=risk_exposure,
        color=risk_exposure,
        color_continuous_scale='Reds',
        labels={'x': 'Bond name', 'y': 'Duration Contribution'}
    )

    fig2.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        coloraxis_showscale=False,
        xaxis_title="Bond ETF",
        yaxis_title="Interest Rate Sensitivity (Duration × Weight)",
        font=dict(family="Outfit, sans-serif", size=12)
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.info("💡 **Note:** Market data is fetched live from Yahoo Finance using proxy ETFs (SHY, IEI, IEF, TLT).")

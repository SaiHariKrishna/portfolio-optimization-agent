import os
import google.generativeai as genai

import streamlit as st

API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
MODEL_NAME = "models/gemini-2.5-flash"

# We use 2.5 Flash as primary for speed and higher quota, 
# and flash-latest as fallback for deep reasoning.
PRIMARY_MODEL = "models/gemini-2.5-flash"
FALLBACK_MODEL = "models/gemini-flash-latest"

class ReasoningAgent:
    """A separate reasoning agent specifically for general queries and deep analysis."""
    
    def __init__(self):
        # We'll initialize the models on demand to handle quota errors gracefully
        pass

    def _get_response(self, model_name, prompt):
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text

    def analyze(self, user_query, portfolio_state):
        """Perform deep reasoning on the portfolio state based on user query."""
        summary = summarize_portfolio(portfolio_state["bonds"])
        
        # Build context from the state
        context = f"""
        PORTFOLIO CONTEXT:
        - Total Bonds: {len(portfolio_state['bonds'])}
        - Average Duration: {summary['avg_duration']} years
        - Short-term Exposure: {summary['short_exposure']:.2%}
        - Long-term Exposure: {summary['long_exposure']:.2%}
        - Metrics: {portfolio_state.get('decision', 'No decision made yet')}
        
        CURRENT BONDS:
        {portfolio_state['bonds']}
        """

        prompt = f"""
        You are OptiMarket's Lead Reasoning Agent. Your role is to provide deep, analytical, and professional fintech insights.
        
        {context}
        
        USER QUERY:
        "{user_query}"
        
        INSTRUCTIONS:
        1. If the query is general (e.g., "what is duration?"), explain it clearly with examples related to this portfolio.
        2. If the query is analytical (e.g., "how safe is my portfolio?"), perform a multi-step reasoning check:
           - Assess interest rate risk based on duration.
           - Check allocation balance.
           - Provide a clear 'Fintech Recommendation'.
        3. Keep the tone professional, sleek, and data-driven.
        4. Use markdown for better readability.
        """
        
        # Try Primary Model
        try:
            return self._get_response(PRIMARY_MODEL, prompt)
        except Exception as e:
            # If primary fails (e.g. Quota), try Fallback Model
            try:
                return self._get_response(FALLBACK_MODEL, prompt)
            except Exception as e2:
                # If everything else fails, return a clean but useful financial summary
                return self._local_fallback(summary, user_query)

    def _local_fallback(self, summary, query):
        """A clean deterministic response if the AI API fails entirely."""
        return f"""
### 🛡️ Portfolio Analysis (Local Engine)

The AI reasoning agent is currently facing high demand (Quota Exceeded), but our local engine has analyzed your portfolio:

**Current Risk Metrics:**
- **Avg Duration:** {summary['avg_duration']} years
- **Exposure:** Short-term bonds make up {summary['short_exposure']:.0%}, while long-term bonds are {summary['long_exposure']:.0%}.

**Quick Insight:**
Your query *"{query}"* mostly relates to interest rate sensitivity. A duration of {summary['avg_duration']} implies that for every 1% rise in interest rates, your portfolio value could fall by approximately {summary['avg_duration']}%.

*Please try again in a few minutes for the full AI insights.*
"""

# Reasoning Agent instance
reasoner = ReasoningAgent()

def deterministic_explanation(summary_before, summary_after=None):
    if summary_after is None:
        return (
            f"The portfolio has an average duration of "
            f"{summary_before['avg_duration']} years. "
            f"Approximately {int(summary_before['long_exposure']*100)}% "
            f"is in long-term bonds, making it sensitive to interest rate changes."
        )

    return (
        f"The portfolio duration was reduced from "
        f"{summary_before['avg_duration']} to "
        f"{summary_after['avg_duration']} years. "
        f"Long-term exposure decreased while short-term exposure increased, "
        f"reducing interest rate risk."
    )


def summarize_portfolio(bonds):
    if not bonds:
        return {"avg_duration": 0, "short_exposure": 0, "long_exposure": 0}
        
    total_weight = sum(b.get("weight", 1.0/len(bonds)) for b in bonds)

    avg_duration = sum(
        b.get("maturity_years", 0) * b.get("weight", 1.0/len(bonds)) for b in bonds
    ) / total_weight

    short_exposure = sum(
        b.get("weight", 1.0/len(bonds)) for b in bonds if b.get("maturity_years", 0) <= 3
    )

    long_exposure = sum(
        b.get("weight", 1.0/len(bonds)) for b in bonds if b.get("maturity_years", 0) >= 7
    )

    return {
        "avg_duration": round(avg_duration, 2),
        "short_exposure": round(short_exposure, 2),
        "long_exposure": round(long_exposure, 2),
    }


def explain_decision(state, user_query=None):
    """Use the separate Reasoning Agent for all explanations and general queries."""
    if not user_query:
        user_query = "Summarize my current portfolio state and risk profile."
        
    return reasoner.analyze(user_query, state)

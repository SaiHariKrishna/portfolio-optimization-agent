import os
import google.generativeai as genai

API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=API_KEY)
MODEL_NAME = "models/gemini-2.5-flash"


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
    total_weight = sum(b["weight"] for b in bonds)

    avg_duration = sum(
        b["maturity_years"] * b["weight"] for b in bonds
    ) / total_weight

    short_exposure = sum(
        b["weight"] for b in bonds if b["maturity_years"] <= 3
    )

    long_exposure = sum(
        b["weight"] for b in bonds if b["maturity_years"] >= 7
    )

    return {
        "avg_duration": round(avg_duration, 2),
        "short_exposure": round(short_exposure, 2),
        "long_exposure": round(long_exposure, 2),
    }


def explain_decision(state, user_query=None):
    bonds_before = state["bonds"]
    intent = state.get("intent")

    summary_before = summarize_portfolio(bonds_before)

    try:
        model = genai.GenerativeModel(MODEL_NAME)

        if intent == "QUERY":
            prompt = f"""
            Identify yourself as OptiMarket's Advanced Bond Analysis Agent. 
            The user is asking a strategic question about the bond market or their specific portfolio.
            
            User Query: "{user_query}"
            
            Current Portfolio Snapshot:
            - Avg Duration: {summary_before['avg_duration']} years
            - Short-term Exposure (<=3Y): {summary_before['short_exposure']:.0%}
            - Long-term Exposure (>=7Y): {summary_before['long_exposure']:.0%}
            
            Task:
            1. Provide a detailed, professional, and educational answer.
            2. Explain the financial theory behind the query.
            3. Relate the answer specifically to the user's current portfolio metrics provided above.
            4. Use clear headings and bullet points for readability.
            5. Do NOT just give a one-sentence answer.
            """
            response = model.generate_content(prompt)
            return response.text

        if intent == "SUGGEST":
            prompt = f"""
            Identify yourself as OptiMarket's Strategic Portfolio Advisor.
            The user is looking for actionable strategic advice or suggestions for their bond portfolio.
            
            User Request: "{user_query}"
            
            Current Portfolio Snapshot:
            - Avg Duration: {summary_before['avg_duration']} years
            - Short-term Exposure: {summary_before['short_exposure']:.0%}
            - Long-term Exposure: {summary_before['long_exposure']:.0%}
            
            Task:
            1. Offer 3-4 comprehensive strategic recommendations.
            2. For each recommendation, explain the 'What', 'Why' (market logic), and 'How' (execution).
            3. Discuss the potential impact on yield and interest rate risk.
            4. Be qualitative and strategic. Use a professional tone.
            5. Ensure the answer is thorough and provides complete context.
            """
            response = model.generate_content(prompt)
            return response.text

        # OPTIMIZE_AND_EXPLAIN CASE (Action was taken)
        optimized_weights = state.get("optimized_weights")
        if not optimized_weights:
            return "Portfolio optimization was requested but no weights were generated."

        bonds_after = []
        for b, w in zip(bonds_before, optimized_weights):
            nb = b.copy()
            nb["weight"] = w
            bonds_after.append(nb)

        summary_after = summarize_portfolio(bonds_after)

        prompt = f"""
        Action Report: OptiMarket Optimization Engine
        User request: {user_query}
        
        Before Optimization Status:
        - Avg duration: {summary_before['avg_duration']} years
        - Long-term exposure: {summary_before['long_exposure']:.0%}
        
        After Optimization Status:
        - Avg duration: {summary_after['avg_duration']} years
        - Long-term exposure: {summary_after['long_exposure']:.0%}
        
        Task:
        1. Explain the specific mathematical shifts made by the optimizer.
        2. Describe how the new allocation fulfills the user's specific request.
        3. Provide a clear summary of the new risk status.
        4. Use a structured, technical yet approachable format.
        """
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        error_msg = str(e)
        print(f"LLM Error: {error_msg}")
        # 🔒 IMPROVED FALLBACK
        fallback_text = f"### Service Status Notice\nI am currently operating in fallback mode due to a connection issue with the main reasoning engine ({error_msg}).\n\n"
        fallback_text += f"**Your Portfolio Context:**\n- **Avg Duration:** {summary_before['avg_duration']} years\n- **Long-term Risk:** {summary_before['long_exposure']:.0%}\n\n"
        fallback_text += f"**Observation:** Based on your query regarding '{user_query}', a duration of {summary_before['avg_duration']} years suggests your portfolio is {'sensitive' if summary_before['avg_duration'] > 5 else 'relatively resilient'} to interest rate changes. Please try again in a few moments for a full tactical analysis."
        return fallback_text

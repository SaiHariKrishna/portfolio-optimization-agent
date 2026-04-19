import re

def extract_target_duration(user_query: str):
    """
    Very simple, deterministic parser.
    LLM can be swapped in later.
    """
    match = re.search(r"(\d+(\.\d+)?)\s*year", user_query.lower())
    if match:
        return float(match.group(1))
    return 4.0  # default

def classify_intent(user_query: str) -> str:
    q = user_query.lower()

    explain_keywords = [
        "explain", "why", "describe", "what is", "summarize", "risk"
    ]

    action_keywords = [
        "reduce", "increase", "optimize", "rebalance",
        "change", "adjust", "make", "bring"
    ]

    if any(k in q for k in explain_keywords) and not any(k in q for k in action_keywords):
        return "EXPLAIN_ONLY"

    return "OPTIMIZE_AND_EXPLAIN"

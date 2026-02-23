import re

def extract_target_duration(user_query: str):
    """
    Attempts to extract a number followed by 'year' or 'yrs'.
    """
    match = re.search(r"(\d+(\.\d+)?)\s*(year|yr|yrs)", user_query.lower())
    if match:
        return float(match.group(1))
    return None # Return None if not found

def classify_intent(user_query: str) -> str:
    q = user_query.lower()
    target = extract_target_duration(q)

    # Keywords for general information
    query_keywords = [
        "what is", "how does", "tell me about", "define", "explain", "meaning", "history"
    ]
    
    # Keywords for seeking advice
    suggest_keywords = [
        "should i", "suggest", "recommend", "advice", "how to", "improve", "options", "could i"
    ]

    # Keywords for performing an action
    action_keywords = [
        "reduce", "increase", "optimize", "rebalance",
        "change", "adjust", "make", "bring", "set", "limit", "go to"
    ]

    # Rule 1: If there's a target duration AND an action/suggest keyword, it's often an optimization
    if target is not None:
        if any(k in q for k in action_keywords) or any(k in q for k in suggest_keywords):
            return "OPTIMIZE_AND_EXPLAIN"
        # If just a years mentioned (e.g. "go to 4 years"), treat as optimization
        return "OPTIMIZE_AND_EXPLAIN"

    # Rule 2: If no target duration is mentioned, we can't mathematically optimize.
    # We should shift to SUGGEST even if action words are used.
    if any(k in q for k in action_keywords) or any(k in q for k in suggest_keywords):
        return "SUGGEST"

    # Rule 3: General knowledge
    if any(k in q for k in query_keywords) or "?" in q:
        return "QUERY"

    # Default
    return "QUERY"

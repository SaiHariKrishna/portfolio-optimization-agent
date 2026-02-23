from langgraph.graph import StateGraph
from state import PortfolioState
from nodes import (
    compute_durations,
    optimize_portfolio,
    finalize_decision,
    llm_explainer
)

graph = StateGraph(PortfolioState)

graph.add_node("duration", compute_durations)
graph.add_node("optimize", optimize_portfolio)
graph.add_node("decision", finalize_decision)
graph.add_node("explain", llm_explainer)

# Entry
graph.set_entry_point("duration")

# Conditional routing
def route_after_duration(state):
    intent = state.get("intent")
    if intent in ["QUERY", "SUGGEST"]:
        return "explain"
    return "optimize"

graph.add_conditional_edges(
    "duration",
    route_after_duration,
    {
        "optimize": "optimize",
        "explain": "explain"
    }
)

graph.add_edge("optimize", "decision")
graph.add_edge("decision", "explain")

portfolio_agent = graph.compile()
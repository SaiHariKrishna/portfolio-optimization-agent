from tools import duration_tool, optimization_tool
from llm import explain_decision

def compute_durations(state):
    state["durations"] = [
        duration_tool(bond) for bond in state["bonds"]
    ]
    return state

def optimize_portfolio(state):
    state["optimized_weights"] = optimization_tool(
        state["durations"],
        state["target_duration"]
    )
    return state

def finalize_decision(state):
    state["decision"] = (
        f"Portfolio optimized to target duration "
        f"{state['target_duration']} years."
    )
    return state

def llm_explainer(state):
    state["explanation"] = explain_decision(
        state,
        state.get("user_query", "")
    )
    return state

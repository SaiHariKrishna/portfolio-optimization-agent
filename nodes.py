from tools import duration_tool, convexity_tool, optimization_tool
from llm import explain_decision


def compute_durations(state):
    state["durations"] = [
        duration_tool(bond) for bond in state["bonds"]
    ]
    state["convexities"] = [
        convexity_tool(bond) for bond in state["bonds"]
    ]
    return state


def optimize_portfolio(state):
    method = state.get("optimization_method", "original")
    bonds = state["bonds"]

    # "black_litterman" has been removed completely
    if method == "mean_variance":
        from optimizer import mean_variance_optimize, build_bond_cov_matrix

        bond_names = [b["bond_name"] for b in bonds]
        expected_rets = {b["bond_name"]: b["market_yield"] for b in bonds}
        cov_matrix = build_bond_cov_matrix(bonds, state["durations"])
        state["optimized_weights"] = mean_variance_optimize(
            expected_rets, cov_matrix, bond_names
        )

    else:  # "original"
        state["optimized_weights"] = optimization_tool(
            state["durations"], state["target_duration"]
        )

    return state


def finalize_decision(state):
    method = state.get("optimization_method", "original")
    labels = {
        "original": "Duration-Target",
        "mean_variance": "Mean-Variance (Max Sharpe)",
    }
    state["decision"] = (
        f"Portfolio optimized via {labels.get(method, method)} "
        f"to target duration {state['target_duration']} years."
    )
    return state


def llm_explainer(state):
    # This now uses the dedicated Gemini Reasoning Agent
    state["explanation"] = explain_decision(
        state,
        state.get("user_query", "")
    )
    return state

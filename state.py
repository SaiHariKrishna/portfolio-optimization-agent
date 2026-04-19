from typing import TypedDict, List

class PortfolioState(TypedDict):
    bonds: list
    durations: list
    convexities: list
    optimized_weights: list
    target_duration: float
    decision: str
    explanation: str
    user_query: str
    intent: str
    optimization_method: str

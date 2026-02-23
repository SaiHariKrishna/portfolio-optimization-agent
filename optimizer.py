import numpy as np
from scipy.optimize import minimize

def optimize_weights(durations, target_duration):
    if target_duration is None:
        # Fallback to current duration if somehow we got here with None
        return [1.0 / len(durations)] * len(durations)
        
    n = len(durations)
    x0 = np.ones(n) / n

    def objective(w):
        return np.sum((w - x0) ** 2)

    constraints = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1},
        {"type": "eq", "fun": lambda w: np.dot(w, durations) - target_duration}
    ]

    bounds = [(0, 1)] * n

    result = minimize(objective, x0, bounds=bounds, constraints=constraints)
    return result.x.tolist()

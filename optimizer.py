import numpy as np
import pandas as pd
from scipy.optimize import minimize


def optimize_weights(durations, target_duration):
    """Original duration-targeting optimization."""
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


def build_bond_cov_matrix(bonds, durations, yield_vol=0.01, base_corr=0.85):
    """Build analytical covariance matrix for bonds.

    Uses duration-based approximation:
      Var(Ri) = Di^2 * sigma_y^2
      Cov(Ri,Rj) = rho * Di * sigma_y * Dj * sigma_y
    """
    n = len(bonds)
    names = [b["bond_name"] for b in bonds]

    cov = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                cov[i][j] = (durations[i] * yield_vol) ** 2
            else:
                cov[i][j] = (
                    base_corr
                    * durations[i] * yield_vol
                    * durations[j] * yield_vol
                )

    return pd.DataFrame(cov, index=names, columns=names)


def mean_variance_optimize(expected_returns, cov_matrix, bond_names):
    """Mean-Variance optimization using PyPortfolioOpt.

    Args:
        expected_returns: dict  {bond_name: expected_return}
        cov_matrix:       pd.DataFrame (n x n)
        bond_names:       list[str]
    Returns:
        list of optimized weights
    """
    try:
        from pypfopt import EfficientFrontier

        mu = pd.Series(expected_returns)
        ef = EfficientFrontier(mu, cov_matrix, weight_bounds=(0.05, 0.80))

        try:
            ef.max_sharpe(risk_free_rate=0.02)
        except Exception:
            # Fallback: minimise volatility if max_sharpe fails
            ef = EfficientFrontier(mu, cov_matrix, weight_bounds=(0.05, 0.80))
            ef.min_volatility()

        weights = ef.clean_weights()
        return [weights.get(name, 0.0) for name in bond_names]

    except Exception:
        n = len(bond_names)
        return [1.0 / n] * n



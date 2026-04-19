import numpy as np
from scipy import stats


def historical_var(returns, confidence=0.95):
    """Historical Value at Risk at the given confidence level."""
    returns = np.asarray(returns)
    if len(returns) == 0:
        return 0.0
    return float(np.percentile(returns, (1 - confidence) * 100))


def parametric_var(returns, confidence=0.95):
    """Parametric (Gaussian) Value at Risk."""
    returns = np.asarray(returns)
    if len(returns) == 0:
        return 0.0
    mu = np.mean(returns)
    sigma = np.std(returns, ddof=1)
    if sigma < 1e-10:
        return 0.0
    z = stats.norm.ppf(1 - confidence)
    return float(mu + z * sigma)


def expected_shortfall(returns, confidence=0.95):
    """Conditional VaR — average loss beyond the VaR threshold."""
    returns = np.asarray(returns)
    if len(returns) == 0:
        return 0.0
    var = historical_var(returns, confidence)
    tail = returns[returns <= var]
    if len(tail) == 0:
        return var
    return float(np.mean(tail))


def compute_portfolio_returns(yield_history, durations, weights):
    """Approximate daily portfolio returns from yield changes.

    Uses duration approximation: dP/P ~ -D * dy
    """
    yield_history = np.asarray(yield_history, dtype=float)
    durations = np.asarray(durations, dtype=float)
    weights = np.asarray(weights, dtype=float)

    yield_changes = np.diff(yield_history, axis=0)
    bond_returns = -durations * yield_changes
    portfolio_returns = bond_returns @ weights
    return portfolio_returns


def compute_var_metrics(yield_history, durations, weights, confidence=0.95):
    """Compute all VaR metrics for a portfolio.

    Returns dict with historical_var, parametric_var, expected_shortfall.
    """
    portfolio_returns = compute_portfolio_returns(
        yield_history, durations, weights
    )
    return {
        "historical_var": historical_var(portfolio_returns, confidence),
        "parametric_var": parametric_var(portfolio_returns, confidence),
        "expected_shortfall": expected_shortfall(portfolio_returns, confidence),
        "n_observations": len(portfolio_returns),
        "confidence": confidence
    }

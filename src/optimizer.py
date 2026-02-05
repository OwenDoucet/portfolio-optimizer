import numpy as np
from scipy.optimize import minimize
from portfolio import portfolio_return, portfolio_risk
from helper import sector_constraints

def maximize_return_given_risk(mu, Sigma, target_risk, tickers, sectors, sector_max=None, bounds=None):
    if bounds is None:
        bounds = [(0,1)] * len(mu)
    weights_stage1 = maximize_with_sector_caps(mu, Sigma, tickers, sectors, sector_max, bounds)

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) -1}]

    if sector_max is not None:
        constraints += sector_constraints(sectors, tickers, sector_max)

    constraints.append({"type": "ineq", "fun": lambda w: target_risk - portfolio_risk(w, Sigma)})

    result = minimize(
        lambda w: -portfolio_return(w, mu),
        weights_stage1,
        bounds=bounds,
        constraints=constraints
    )
    return result.x

def maximize_with_sector_caps(mu, Sigma, tickers, sectors, sector_max, bounds=None):
    n = len(mu)
    w0 = np.ones(n) / n

    if bounds is None:
        bounds = [(0, 1)] * n

    # Only constraint: sum(weights) = 1 + sector caps
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

    if sector_max is not None:
        from helper import sector_constraints
        constraints += sector_constraints(sectors, tickers, sector_max)

    result = minimize(
        lambda w: -portfolio_return(w, mu),
        w0,
        bounds=bounds,
        constraints=constraints
    )
    return result.x
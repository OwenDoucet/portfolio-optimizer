import numpy as np
from scipy.optimize import minimize
from portfolio import portfolio_risk, portfolio_return
from helper import sector_constraints

def maximize_sharpe(mu, sigma, tickers, sectors, rf, sector_max=None, bounds=None):
    n = len(mu);
    w0 = np.ones(n) / n

    if bounds is None:
        bounds = [(0,1)] * n

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w)-1}]

    if sector_max is not None:
        constraints += sector_constraints(sectors, tickers, sector_max)

    def neg_sharpe(w):
        return - (portfolio_return(w, mu) - rf) / portfolio_risk(w, sigma)

    result = minimize(
        lambda w: neg_sharpe(w),
        w0,
        bounds=bounds,
        constraints=constraints
    )

    return result.x

import numpy as np
from portfolio import portfolio_risk, portfolio_return
def generate_frontier(mu, Sigma, n_portfolios=3000):
    n = len(mu)
    risks = []
    returns = []

    for _ in range(n_portfolios):
        w = np.random.random(n)
        w /= np.sum(w)

        risks.append(portfolio_risk(w, Sigma))
        returns.append(portfolio_return(w, mu))

    return pd.DataFrame({
        "Risk": risks,
        "Return": returns
    })

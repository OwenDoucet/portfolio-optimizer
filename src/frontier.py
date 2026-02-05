import numpy as np

def generate_efficient_frontier(mu, Sigma, n_portfolios=3000):
    n = len(mu)

    risks = []
    returns = []
    weights_list = []

    for _ in range(n_portfolios):
        w = np.random.random(n)
        w /= np.sum(w)

        r = np.dot(w, mu)
        risk = np.sqrt(w.T @ Sigma @ w)

        returns.append(r)
        risks.append(r)
        weights_list.append(w)

    return np.array(risks), np.array(returns), weights_list
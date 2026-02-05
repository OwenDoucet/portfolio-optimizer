import numpy as np

def compute_returns(prices):
    return prices.pct_change().dropna()

def expected_returns(returns):
    return returns.mean() * 252

def covariance_matrix(returns):
    return returns.cov() * 252

def portfolio_return(weights, mu):
    return np.dot(weights, mu)

def portfolio_risk(weights, Sigma):
    return np.sqrt(weights.T @ Sigma @ weights)
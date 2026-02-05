# helper.py
from collections import defaultdict
from yahooquery import Ticker
YQ_AVAILABLE = True

def get_sectors(tickers):
    """
    Returns a dictionary mapping tickers to their sector.
    Falls back to 'Unknown' if sector info is unavailable.
    Uses yahooquery if installed, else falls back to yfinance.
    """
    sectors = {}

    if YQ_AVAILABLE:
        tickers_obj = Ticker(tickers)
        for t in tickers:
            try:
                profile = tickers_obj.asset_profile.get(t, {})
                sectors[t] = profile.get("sector", "Unknown")
            except Exception:
                sectors[t] = "Unknown"
    else:
        for t in tickers:
            try:
                info = yf.Ticker(t).info
                sectors[t] = info.get("sector", "Unknown")
            except Exception:
                sectors[t] = "Unknown"

    return sectors


def build_sector_indices(tickers, sectors):
    sector_idx = defaultdict(list)
    for i, t in enumerate(tickers):
        sector = sectors.get(t, "Unknown")
        sector_idx[sector].append(i)
    return sector_idx


def sector_max_constraint(idx, max_weight):
    def constraint(w):
        return max_weight - sum(w[i] for i in idx)
    return constraint


def sector_constraints(sectors, tickers, sector_max):
    sector_idx = build_sector_indices(tickers, sectors)
    constraints = []

    for sector, max_weight in sector_max.items():
        idx = sector_idx.get(sector, [])
        if not idx:
            continue
        constraints.append({
            "type": "ineq",
            "fun": sector_max_constraint(idx, max_weight)
        })

    return constraints


def build_full_sector_caps(sectors, user_caps, default=1.0):
    full_caps = {}
    for sector in set(sectors.values()):
        full_caps[sector] = user_caps.get(sector, default)
    return full_caps


def get_active_sectors(tickers):
    sectors = get_sectors(tickers)
    active_sectors = set(sectors.values())
    if "Unknown" in sectors.values():
        active_sectors.add("Unknown")
    return sectors, active_sectors

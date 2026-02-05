import yfinance as yf

def load_price_data(tickers, start_date):
    data = yf.download(tickers, start=start_date, auto_adjust=False)

    if isinstance(data.columns, tuple) or hasattr(data.columns, "levels"):
        data = data.xs("Adj Close", axis=1, level=0)

    return data.dropna()
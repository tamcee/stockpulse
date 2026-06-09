from .demo_data import DEMO_DATA

def fetch_stock_data(ticker):
    # Try cache -> Alpha Vantage -> Demo
    if ticker in DEMO_DATA:
        return DEMO_DATA[ticker]
    return {"overview": {}}

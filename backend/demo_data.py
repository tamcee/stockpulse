"""
Search database for popular US and Indian stocks.
"""

# Ticker search database — top US and Indian stocks
TICKER_DATABASE = [
    # US Stocks
    {'ticker': 'AAPL', 'name': 'Apple Inc.'},
    {'ticker': 'MSFT', 'name': 'Microsoft Corporation'},
    {'ticker': 'GOOGL', 'name': 'Alphabet Inc.'},
    {'ticker': 'AMZN', 'name': 'Amazon.com Inc.'},
    {'ticker': 'TSLA', 'name': 'Tesla Inc.'},
    {'ticker': 'META', 'name': 'Meta Platforms Inc.'},
    {'ticker': 'NVDA', 'name': 'NVIDIA Corporation'},
    {'ticker': 'BRK.B', 'name': 'Berkshire Hathaway Inc.'},
    {'ticker': 'JPM', 'name': 'JPMorgan Chase & Co.'},
    {'ticker': 'V', 'name': 'Visa Inc.'},
    {'ticker': 'JNJ', 'name': 'Johnson & Johnson'},
    {'ticker': 'WMT', 'name': 'Walmart Inc.'},
    {'ticker': 'PG', 'name': 'Procter & Gamble Co.'},
    {'ticker': 'MA', 'name': 'Mastercard Inc.'},
    {'ticker': 'UNH', 'name': 'UnitedHealth Group Inc.'},
    {'ticker': 'HD', 'name': 'Home Depot Inc.'},
    {'ticker': 'DIS', 'name': 'Walt Disney Co.'},
    {'ticker': 'BAC', 'name': 'Bank of America Corp.'},
    {'ticker': 'NFLX', 'name': 'Netflix Inc.'},
    {'ticker': 'ADBE', 'name': 'Adobe Inc.'},
    
    # Indian Stocks (NSE)
    {'ticker': 'RELIANCE.NS', 'name': 'Reliance Industries Limited'},
    {'ticker': 'TCS.NS', 'name': 'Tata Consultancy Services Limited'},
    {'ticker': 'HDFCBANK.NS', 'name': 'HDFC Bank Limited'},
    {'ticker': 'ICICIBANK.NS', 'name': 'ICICI Bank Limited'},
    {'ticker': 'INFY.NS', 'name': 'Infosys Limited'},
    {'ticker': 'SBIN.NS', 'name': 'State Bank of India'},
    {'ticker': 'BHARTIARTL.NS', 'name': 'Bharti Airtel Limited'},
    {'ticker': 'ITC.NS', 'name': 'ITC Limited'},
    {'ticker': 'KOTAKBANK.NS', 'name': 'Kotak Mahindra Bank Limited'},
    {'ticker': 'LT.NS', 'name': 'Larsen & Toubro Limited'},
    {'ticker': 'HINDUNILVR.NS', 'name': 'Hindustan Unilever Limited'},
    {'ticker': 'AXISBANK.NS', 'name': 'Axis Bank Limited'},
    {'ticker': 'BAJFINANCE.NS', 'name': 'Bajaj Finance Limited'},
    {'ticker': 'MARUTI.NS', 'name': 'Maruti Suzuki India Limited'},
    {'ticker': 'ASIANPAINT.NS', 'name': 'Asian Paints Limited'},
    {'ticker': 'HCLTECH.NS', 'name': 'HCL Technologies Limited'},
    {'ticker': 'SUNPHARMA.NS', 'name': 'Sun Pharmaceutical Industries'},
    {'ticker': 'TATAMOTORS.NS', 'name': 'Tata Motors Limited'},
    {'ticker': 'TITAN.NS', 'name': 'Titan Company Limited'},
    {'ticker': 'WIPRO.NS', 'name': 'Wipro Limited'},
]

def search_tickers(query):
    """Search ticker database by name or symbol."""
    query = query.upper().strip()
    results = []
    for item in TICKER_DATABASE:
        if query in item['ticker'].upper() or query in item['name'].upper():
            results.append(item)
    return results[:10]

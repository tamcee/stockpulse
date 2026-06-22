"""
yfinance data fetcher with local caching.
"""
import yfinance as yf
import pandas as pd
from backend.models import get_cached_data, set_cached_data
from backend.demo_data import search_tickers

def search_stocks(query):
    """Search for stocks by name or ticker symbol."""
    return search_tickers(query)

def fetch_stock_data(ticker):
    """
    Fetch complete stock data (overview + 3 financial statements).
    Checks cache first, then uses yfinance.
    """
    ticker = ticker.upper()

    # Try cache first
    cached = _get_all_cached(ticker)
    if cached:
        return cached

    # Use yfinance
    try:
        yf_ticker = yf.Ticker(ticker)
        
        # We need info to exist
        info = yf_ticker.info
        if not info or ('symbol' not in info and 'shortName' not in info):
            print(f"yfinance returned empty info for {ticker}")
            return None

        # Format overview
        overview = {
            'Symbol': info.get('symbol', ticker),
            'Name': info.get('shortName', info.get('longName', ticker)),
            'Description': info.get('longBusinessSummary', ''),
            'Exchange': info.get('exchange', ''),
            'Currency': info.get('currency', 'USD'),
            'Country': info.get('country', ''),
            'Sector': info.get('sector', ''),
            'Industry': info.get('industry', ''),
            'MarketCapitalization': str(info.get('marketCap', '0')),
            'PERatio': str(info.get('trailingPE', info.get('forwardPE', '0'))),
            'EPS': str(info.get('trailingEps', '0')),
            'BookValue': str(info.get('bookValue', '0')),
            'DividendYield': str(info.get('dividendYield', '0')),
            'Beta': str(info.get('beta', '0')),
            'SharesOutstanding': str(info.get('sharesOutstanding', '0')),
            '52WeekHigh': str(info.get('fiftyTwoWeekHigh', '0')),
            '52WeekLow': str(info.get('fiftyTwoWeekLow', '0')),
            'PriceToBookRatio': str(info.get('priceToBook', '0')),
        }

        # Fetch and format financials
        income_df = yf_ticker.financials
        balance_df = yf_ticker.balance_sheet
        cashflow_df = yf_ticker.cashflow

        def parse_financials(df, mapping_dict):
            reports = []
            if df is not None and not df.empty:
                # df columns are dates
                for col in df.columns:
                    report = {'fiscalDateEnding': str(col.date()) if hasattr(col, 'date') else str(col)[:10]}
                    for out_key, in_key in mapping_dict.items():
                        if in_key in df.index:
                            val = df.loc[in_key, col]
                            report[out_key] = str(int(val)) if pd.notna(val) else '0'
                        else:
                            report[out_key] = '0'
                    reports.append(report)
            return {'annualReports': reports}

        income_map = {
            'totalRevenue': 'Total Revenue',
            'grossProfit': 'Gross Profit',
            'operatingIncome': 'Operating Income',
            'netIncome': 'Net Income',
            'costOfRevenue': 'Cost Of Revenue',
            'ebitda': 'Normalized EBITDA',
            'interestExpense': 'Interest Expense'
        }
        
        balance_map = {
            'totalAssets': 'Total Assets',
            'totalCurrentAssets': 'Current Assets',
            'totalCurrentLiabilities': 'Current Liabilities',
            'totalShareholderEquity': 'Stockholders Equity',
            'shortLongTermDebtTotal': 'Total Debt',
            'inventory': 'Inventory',
            'cashAndCashEquivalentsAtCarryingValue': 'Cash And Cash Equivalents'
        }
        
        cashflow_map = {
            'operatingCashflow': 'Operating Cash Flow',
            'capitalExpenditures': 'Capital Expenditure'
        }

        data = {
            'overview': overview,
            'income': parse_financials(income_df, income_map),
            'balance': parse_financials(balance_df, balance_map),
            'cashflow': parse_financials(cashflow_df, cashflow_map)
        }

        # Cache it
        _cache_all(ticker, data)
        return data

    except Exception as e:
        print(f"yfinance fetch failed for {ticker}: {e}")
        return None

def _get_all_cached(ticker):
    """Try to get all data from cache."""
    overview = get_cached_data(ticker, 'overview')
    income = get_cached_data(ticker, 'income')
    balance = get_cached_data(ticker, 'balance')
    cashflow = get_cached_data(ticker, 'cashflow')

    if overview and income and balance and cashflow:
        return {
            'overview': overview,
            'income': income,
            'balance': balance,
            'cashflow': cashflow,
        }
    return None

def _cache_all(ticker, data):
    """Cache all data types."""
    if data.get('overview'):
        set_cached_data(ticker, 'overview', data['overview'])
    if data.get('income'):
        set_cached_data(ticker, 'income', data['income'])
    if data.get('balance'):
        set_cached_data(ticker, 'balance', data['balance'])
    if data.get('cashflow'):
        set_cached_data(ticker, 'cashflow', data['cashflow'])

import pytest
from backend.analysis_engine import (
    safe_div,
    calculate_cagr,
    calculate_metrics,
    detect_red_flags,
    calculate_health_score,
    run_full_analysis,
    _build_historical
)

# Mock data
mock_overview = {
    'Symbol': 'TEST',
    'Name': 'Test Corp',
    'Description': 'A test company',
    'Sector': 'Technology',
    'Industry': 'Software',
    'MarketCapitalization': '1000000000', 
    'PERatio': '15.5',
    'PriceToBookRatio': '2.1',
    'PriceToSalesRatio': '4.0',
    'EVToEBITDA': '10.5',
    'Beta': '1.2',
    'DividendYield': '0.02',
    'EPS': '5.0',
}

mock_income = {
    'annualReports': [
        {'fiscalDateEnding': '2023-12-31', 'totalRevenue': '1200', 'netIncome': '150', 'grossProfit': '600', 'operatingIncome': '200', 'interestExpense': '10'},
        {'fiscalDateEnding': '2022-12-31', 'totalRevenue': '1000', 'netIncome': '100', 'grossProfit': '500', 'operatingIncome': '150', 'interestExpense': '10'},
        {'fiscalDateEnding': '2021-12-31', 'totalRevenue': '800',  'netIncome': '80',  'grossProfit': '400', 'operatingIncome': '100', 'interestExpense': '10'},
    ]
}

mock_balance = {
    'annualReports': [
        {'fiscalDateEnding': '2023-12-31', 'totalAssets': '5000', 'totalLiabilities': '2000', 'totalShareholderEquity': '3000', 'totalCurrentAssets': '1000', 'totalCurrentLiabilities': '500', 'inventory': '200', 'shortTermDebt': '100', 'longTermDebt': '500'},
        {'fiscalDateEnding': '2022-12-31', 'totalAssets': '4000', 'totalLiabilities': '1500', 'totalShareholderEquity': '2500', 'totalCurrentAssets': '800',  'totalCurrentLiabilities': '400', 'inventory': '150', 'shortTermDebt': '100', 'longTermDebt': '400'},
    ]
}

mock_cashflow = {
    'annualReports': [
        {'fiscalDateEnding': '2023-12-31', 'operatingCashflow': '300', 'capitalExpenditures': '100', 'dividendPayout': '50'},
        {'fiscalDateEnding': '2022-12-31', 'operatingCashflow': '250', 'capitalExpenditures': '80',  'dividendPayout': '40'},
        {'fiscalDateEnding': '2021-12-31', 'operatingCashflow': '200', 'capitalExpenditures': '70',  'dividendPayout': '30'},
    ]
}

def test_safe_div():
    """Test zero division and generic math."""
    assert safe_div(10, 2) == 5.0
    assert safe_div(10, 0) == 0.0
    assert safe_div(10, None) == 0.0
    assert safe_div("10", "2") == 5.0
    assert safe_div("invalid", "2") == 0.0

def test_calc_growth():
    """Test CAGR and standard growth calculations."""
    v = calculate_cagr(50, 100, 2)
    assert round(v, 1) == 41.4
    
    assert calculate_cagr(100, 0, 1) == 0

def test_calc_metrics_pe_ratio():
    """Test Case: PE ratio calculation with known data"""
    res = calculate_metrics(mock_overview, mock_income, mock_balance, mock_cashflow)
    metrics = res['metrics']
    assert metrics['peRatio'] == 15.5
    assert metrics['pbRatio'] == 2.1
    assert metrics['psRatio'] == round(1000000000 / 1200, 2)

def test_calc_metrics_profitability():
    """Test profitability calculations."""
    res = calculate_metrics(mock_overview, mock_income, mock_balance, mock_cashflow)
    metrics = res['metrics']
    assert metrics['grossMargin'] == 50.0 
    assert round(metrics['operatingMargin'], 1) == 16.7
    assert metrics['netMargin'] == 12.5 
    assert metrics['roe'] == 5.0 
    assert metrics['roa'] == 3.0

def test_calc_metrics_health():
    """Test balance sheet health limits."""
    res = calculate_metrics(mock_overview, mock_income, mock_balance, mock_cashflow)
    metrics = res['metrics']
    assert metrics['currentRatio'] == 2.0
    assert metrics['quickRatio'] == 1.6
    assert metrics['deRatio'] == 0.17  # 500 / 3000
    assert metrics['interestCoverage'] == 20.0

def test_calc_metrics_fcf():
    """Test cash flow calculations."""
    res = calculate_metrics(mock_overview, mock_income, mock_balance, mock_cashflow)
    metrics = res['metrics']
    assert metrics['fcf'] == 200.0
    assert metrics['fcfYield'] == 0.0  # round(200 / 1B * 100, 2) == 0.0

def test_red_flags_negative_fcf():
    """Test Case: Negative FCF red flag detection"""
    bad_cf = {
        'annualReports': [
            {'operatingCashflow': '50', 'capitalExpenditures': '100'}, 
            {'operatingCashflow': '40', 'capitalExpenditures': '80'},  
            {'operatingCashflow': '30', 'capitalExpenditures': '70'},  
        ]
    }
    res = calculate_metrics(mock_overview, mock_income, mock_balance, bad_cf)
    metrics = res['metrics']
    historical = res['historical']
    
    flags = detect_red_flags(metrics, historical)
    found = any('Negative Free Cash Flow' in f['title'] for f in flags)
    assert found is True

def test_red_flags_high_debt():
    """Test high debt flag."""
    bad_bal = {
        'annualReports': [
            {'totalLiabilities': '8000', 'longTermDebt': '8000', 'totalShareholderEquity': '1000'}
        ]
    }
    res = calculate_metrics(mock_overview, mock_income, bad_bal, mock_cashflow)
    metrics = res['metrics']
    historical = res['historical']
    
    flags = detect_red_flags(metrics, historical)
    assert any('High Debt Levels' in f['title'] for f in flags)

def test_health_score_bounds():
    """Test that health score never drops below 0 or goes above 100."""
    res = calculate_metrics(mock_overview, mock_income, mock_balance, mock_cashflow)
    metrics = res['metrics']
    metrics['grossMargin'] = 999
    metrics['revenueCagr'] = 999
    metrics['peRatio'] = 5
    score1 = calculate_health_score(metrics, [])
    assert score1['overall'] <= 100

    metrics['grossMargin'] = -999
    metrics['revenueCagr'] = -999
    score2 = calculate_health_score(metrics, [{'severity': 'high'}])
    assert score2['overall'] >= 0

def test_run_full_analysis():
    """Integration test of the analysis engine."""
    res = run_full_analysis(mock_overview, mock_income, mock_balance, mock_cashflow)
    assert 'company' in res
    assert 'metrics' in res
    assert 'historical' in res
    assert 'redFlags' in res
    assert 'healthScore' in res
    assert 'summary' in res
    assert res['company']['ticker'] == 'TEST'

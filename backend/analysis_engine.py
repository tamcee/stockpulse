"""
Financial Analysis Engine
Implements the three-stage analysis pipeline:
  Stage 1: Metric Calculation (20+ financial ratios)
  Stage 2: Red Flag Detection (pattern recognition)
  Stage 3: Health Score Synthesis (0-100 composite score)
"""


def safe_div(a, b, default=0):
    """Safe division that handles None and zero."""
    try:
        a = float(a) if a is not None else None
        b = float(b) if b is not None else None
        if a is None or b is None or b == 0:
            return default
        return a / b
    except (ValueError, TypeError):
        return default


def safe_float(val, default=0):
    """Safely convert to float."""
    try:
        if val is None or val == 'None' or val == '':
            return default
        return float(val)
    except (ValueError, TypeError):
        return default


def calculate_cagr(start_val, end_val, years):
    """Calculate Compound Annual Growth Rate."""
    try:
        start_val = float(start_val)
        end_val = float(end_val)
        if start_val <= 0 or end_val <= 0 or years <= 0:
            return 0
        return (pow(end_val / start_val, 1 / years) - 1) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


def extract_annual_reports(data, key='annualReports'):
    """Extract annual reports from API data, sorted newest first."""
    reports = data.get(key, [])
    if not reports:
        return []
    return sorted(reports, key=lambda x: x.get('fiscalDateEnding', ''), reverse=True)


# ============================================================
# STAGE 1: Metric Calculation
# ============================================================

def calculate_metrics(overview, income_data, balance_data, cashflow_data):
    """
    Calculate 20+ financial ratios from raw financial statement data.
    Returns a dict of current metrics and historical time-series.
    """
    income_reports = extract_annual_reports(income_data)
    balance_reports = extract_annual_reports(balance_data)
    cashflow_reports = extract_annual_reports(cashflow_data)

    if not income_reports or not balance_reports:
        return _empty_metrics()

    # Current period (most recent)
    inc = income_reports[0]
    bal = balance_reports[0]
    cf = cashflow_reports[0] if cashflow_reports else {}

    # ---- Profitability Ratios ----
    total_revenue = safe_float(inc.get('totalRevenue'))
    gross_profit = safe_float(inc.get('grossProfit'))
    operating_income = safe_float(inc.get('operatingIncome'))
    net_income = safe_float(inc.get('netIncome'))
    total_equity = safe_float(bal.get('totalShareholderEquity'))
    total_assets = safe_float(bal.get('totalAssets'))
    total_debt = safe_float(bal.get('shortLongTermDebtTotal', bal.get('longTermDebt', 0)))
    current_assets = safe_float(bal.get('totalCurrentAssets'))
    current_liabilities = safe_float(bal.get('totalCurrentLiabilities'))
    inventory = safe_float(bal.get('inventory'))
    interest_expense = safe_float(inc.get('interestExpense'))
    operating_cashflow = safe_float(cf.get('operatingCashflow'))
    capex = abs(safe_float(cf.get('capitalExpenditures')))
    cost_of_revenue = safe_float(inc.get('costOfRevenue'))

    gross_margin = safe_div(gross_profit, total_revenue) * 100
    operating_margin = safe_div(operating_income, total_revenue) * 100
    net_margin = safe_div(net_income, total_revenue) * 100
    roe = safe_div(net_income, total_equity) * 100
    roa = safe_div(net_income, total_assets) * 100

    # ROIC = NOPAT / Invested Capital
    tax_rate = 0.25  # approximate
    nopat = operating_income * (1 - tax_rate)
    invested_capital = total_equity + total_debt
    roic = safe_div(nopat, invested_capital) * 100

    # ---- Valuation Ratios ----
    market_cap = safe_float(overview.get('MarketCapitalization'))
    eps = safe_float(overview.get('EPS'))
    book_value = safe_float(overview.get('BookValue'))
    shares_outstanding = safe_float(overview.get('SharesOutstanding'))
    price = safe_div(market_cap, shares_outstanding) if shares_outstanding else 0

    pe_ratio = safe_float(overview.get('PERatio'))
    pb_ratio = safe_float(overview.get('PriceToBookRatio'))
    ps_ratio = safe_div(market_cap, total_revenue)
    ebitda = safe_float(inc.get('ebitda'))
    ev = market_cap + total_debt - safe_float(bal.get('cashAndCashEquivalentsAtCarryingValue', bal.get('cashAndShortTermInvestments', 0)))
    ev_ebitda = safe_div(ev, ebitda)
    fcf = operating_cashflow - capex
    fcf_yield = safe_div(fcf, market_cap) * 100

    # ---- Financial Health Ratios ----
    current_ratio = safe_div(current_assets, current_liabilities)
    quick_ratio = safe_div(current_assets - inventory, current_liabilities)
    de_ratio = safe_div(total_debt, total_equity)
    interest_coverage = safe_div(operating_income, interest_expense) if interest_expense > 0 else 99

    # ---- Efficiency Ratios ----
    asset_turnover = safe_div(total_revenue, total_assets)
    inventory_turnover = safe_div(cost_of_revenue, inventory) if inventory > 0 else 0

    # ---- Cash Flow ----
    ocf_margin = safe_div(operating_cashflow, total_revenue) * 100
    fcf_to_revenue = safe_div(fcf, total_revenue) * 100

    # ---- Growth (multi-year) ----
    revenue_history = [safe_float(r.get('totalRevenue')) for r in income_reports]
    net_income_history = [safe_float(r.get('netIncome')) for r in income_reports]
    eps_history = []

    years_available = len(income_reports)
    revenue_cagr = 0
    if years_available >= 2 and revenue_history[-1] > 0:
        revenue_cagr = calculate_cagr(revenue_history[-1], revenue_history[0], years_available - 1)

    yoy_revenue_growth = 0
    if len(revenue_history) >= 2 and revenue_history[1] > 0:
        yoy_revenue_growth = ((revenue_history[0] - revenue_history[1]) / abs(revenue_history[1])) * 100

    yoy_income_growth = 0
    if len(net_income_history) >= 2 and net_income_history[1] != 0:
        yoy_income_growth = ((net_income_history[0] - net_income_history[1]) / abs(net_income_history[1])) * 100

    # ---- Historical time series for charts ----
    historical = _build_historical(income_reports, balance_reports, cashflow_reports)

    current_metrics = {
        # Profitability
        'grossMargin': round(gross_margin, 2),
        'operatingMargin': round(operating_margin, 2),
        'netMargin': round(net_margin, 2),
        'roe': round(roe, 2),
        'roa': round(roa, 2),
        'roic': round(roic, 2),
        # Valuation
        'peRatio': round(pe_ratio, 2),
        'pbRatio': round(pb_ratio, 2),
        'psRatio': round(ps_ratio, 2),
        'evEbitda': round(ev_ebitda, 2),
        'fcfYield': round(fcf_yield, 2),
        # Financial Health
        'currentRatio': round(current_ratio, 2),
        'quickRatio': round(quick_ratio, 2),
        'deRatio': round(de_ratio, 2),
        'interestCoverage': round(min(interest_coverage, 99), 2),
        # Efficiency
        'assetTurnover': round(asset_turnover, 2),
        'inventoryTurnover': round(inventory_turnover, 2),
        # Cash Flow
        'operatingCashflowMargin': round(ocf_margin, 2),
        'fcf': round(fcf, 2),
        'fcfToRevenue': round(fcf_to_revenue, 2),
        # Growth
        'revenueCagr': round(revenue_cagr, 2),
        'yoyRevenueGrowth': round(yoy_revenue_growth, 2),
        'yoyIncomeGrowth': round(yoy_income_growth, 2),
        # Raw values for display
        'totalRevenue': total_revenue,
        'netIncome': net_income,
        'totalAssets': total_assets,
        'totalDebt': total_debt,
        'totalEquity': total_equity,
        'operatingCashflow': operating_cashflow,
        'eps': eps,
        'marketCap': market_cap,
    }

    return {
        'metrics': current_metrics,
        'historical': historical,
    }


def _build_historical(income_reports, balance_reports, cashflow_reports):
    """Build historical time-series arrays for charting."""
    years = []
    revenue = []
    net_income = []
    gross_margin = []
    operating_margin = []
    net_margin_hist = []
    total_debt_hist = []
    total_equity_hist = []
    operating_cf = []
    fcf_hist = []

    for i, inc in enumerate(reversed(income_reports)):
        year = inc.get('fiscalDateEnding', '')[:4]
        years.append(year)

        rev = safe_float(inc.get('totalRevenue'))
        ni = safe_float(inc.get('netIncome'))
        gp = safe_float(inc.get('grossProfit'))
        oi = safe_float(inc.get('operatingIncome'))

        revenue.append(rev)
        net_income.append(ni)
        gross_margin.append(round(safe_div(gp, rev) * 100, 2))
        operating_margin.append(round(safe_div(oi, rev) * 100, 2))
        net_margin_hist.append(round(safe_div(ni, rev) * 100, 2))

        # Balance sheet (match by index)
        if i < len(list(reversed(balance_reports))):
            bal = list(reversed(balance_reports))[i]
            td = safe_float(bal.get('shortLongTermDebtTotal', bal.get('longTermDebt', 0)))
            te = safe_float(bal.get('totalShareholderEquity'))
            total_debt_hist.append(td)
            total_equity_hist.append(te)
        else:
            total_debt_hist.append(0)
            total_equity_hist.append(0)

        # Cash flow (match by index)
        if i < len(list(reversed(cashflow_reports))):
            cf = list(reversed(cashflow_reports))[i]
            ocf = safe_float(cf.get('operatingCashflow'))
            capex = abs(safe_float(cf.get('capitalExpenditures')))
            operating_cf.append(ocf)
            fcf_hist.append(ocf - capex)
        else:
            operating_cf.append(0)
            fcf_hist.append(0)

    return {
        'years': years,
        'revenue': revenue,
        'netIncome': net_income,
        'grossMargin': gross_margin,
        'operatingMargin': operating_margin,
        'netMargin': net_margin_hist,
        'totalDebt': total_debt_hist,
        'totalEquity': total_equity_hist,
        'operatingCashflow': operating_cf,
        'fcf': fcf_hist,
    }


def _empty_metrics():
    """Return empty metrics structure."""
    return {
        'metrics': {},
        'historical': {
            'years': [], 'revenue': [], 'netIncome': [],
            'grossMargin': [], 'operatingMargin': [], 'netMargin': [],
            'totalDebt': [], 'totalEquity': [],
            'operatingCashflow': [], 'fcf': [],
        },
    }


# ============================================================
# STAGE 2: Red Flag Detection
# ============================================================

def detect_red_flags(metrics, historical):
    """
    Rule-based pattern recognition for financial red flags.
    Returns a list of red flag objects with severity and explanation.
    """
    flags = []
    h = historical
    m = metrics

    # 1. Revenue declining for 2+ consecutive years
    if len(h.get('revenue', [])) >= 3:
        rev = h['revenue']
        declining_years = 0
        for i in range(len(rev) - 1, 0, -1):
            if rev[i] < rev[i - 1]:
                declining_years += 1
            else:
                break
        if declining_years >= 2:
            flags.append({
                'type': 'REVENUE_DECLINE',
                'severity': 'high',
                'title': 'Revenue Declining',
                'description': f'Revenue has declined for {declining_years} consecutive years, indicating potential business deterioration.',
                'icon': '📉'
            })

    # 2. Negative net income
    if m.get('netIncome', 0) < 0:
        flags.append({
            'type': 'NEGATIVE_INCOME',
            'severity': 'high',
            'title': 'Negative Net Income',
            'description': 'The company is currently unprofitable. Sustained losses may indicate fundamental business challenges.',
            'icon': '🔴'
        })

    # 3. Negative FCF for 3+ years
    if len(h.get('fcf', [])) >= 3:
        recent_fcf = h['fcf'][-3:]
        if all(f < 0 for f in recent_fcf):
            flags.append({
                'type': 'NEGATIVE_FCF',
                'severity': 'high',
                'title': 'Persistent Negative Free Cash Flow',
                'description': 'Free cash flow has been negative for 3+ years. The company may struggle to self-fund operations.',
                'icon': '💸'
            })

    # 4. Debt-to-equity > 2.0
    de = m.get('deRatio', 0)
    if de > 2.0:
        flags.append({
            'type': 'HIGH_DEBT',
            'severity': 'medium' if de < 3.0 else 'high',
            'title': 'High Debt Levels',
            'description': f'Debt-to-equity ratio of {de:.1f}x exceeds the 2.0x threshold, indicating significant leverage risk.',
            'icon': '⚠️'
        })

    # 5. Interest coverage < 1.5
    ic = m.get('interestCoverage', 99)
    if 0 < ic < 1.5:
        flags.append({
            'type': 'LOW_INTEREST_COVERAGE',
            'severity': 'high',
            'title': 'Weak Interest Coverage',
            'description': f'Interest coverage ratio of {ic:.1f}x is dangerously low. The company may struggle to service its debt.',
            'icon': '🚨'
        })

    # 6. Gross margin declining > 5pp over 5 years
    gm = h.get('grossMargin', [])
    if len(gm) >= 5:
        gm_decline = gm[0] - gm[-1]  # oldest to newest
        if gm_decline < -5:
            flags.append({
                'type': 'MARGIN_EROSION',
                'severity': 'medium',
                'title': 'Gross Margin Erosion',
                'description': f'Gross margin has declined by {abs(gm_decline):.1f} percentage points over 5 years, suggesting competitive pressure.',
                'icon': '📊'
            })

    # Additional: Very high PE ratio
    pe = m.get('peRatio', 0)
    if pe > 50:
        flags.append({
            'type': 'HIGH_VALUATION',
            'severity': 'medium',
            'title': 'Elevated Valuation',
            'description': f'PE ratio of {pe:.1f}x is significantly above market average, suggesting the stock may be overvalued.',
            'icon': '💰'
        })

    return flags


# ============================================================
# STAGE 3: Health Score Synthesis
# ============================================================

def calculate_health_score(metrics, red_flags):
    """
    Synthesize a composite health score (0-100) across four dimensions:
      - Growth:           25% weight
      - Profitability:    30% weight
      - Financial Health: 30% weight
      - Valuation:        15% weight
    """
    m = metrics

    # ---- Growth Score (0-100) ----
    growth_score = 50  # baseline
    cagr = m.get('revenueCagr', 0)
    if cagr > 20:
        growth_score = 90
    elif cagr > 10:
        growth_score = 75
    elif cagr > 5:
        growth_score = 60
    elif cagr > 0:
        growth_score = 45
    else:
        growth_score = 20

    yoy = m.get('yoyRevenueGrowth', 0)
    if yoy > 15:
        growth_score = min(100, growth_score + 10)
    elif yoy < -5:
        growth_score = max(0, growth_score - 15)

    # ---- Profitability Score (0-100) ----
    prof_score = 50
    nm = m.get('netMargin', 0)
    if nm > 25:
        prof_score = 90
    elif nm > 15:
        prof_score = 75
    elif nm > 8:
        prof_score = 60
    elif nm > 0:
        prof_score = 40
    else:
        prof_score = 15

    roe_val = m.get('roe', 0)
    if roe_val > 20:
        prof_score = min(100, prof_score + 10)
    elif roe_val < 5:
        prof_score = max(0, prof_score - 10)

    # ---- Financial Health Score (0-100) ----
    health_sub = 50
    cr = m.get('currentRatio', 0)
    if cr > 2:
        health_sub = 80
    elif cr > 1.5:
        health_sub = 70
    elif cr > 1:
        health_sub = 55
    else:
        health_sub = 25

    de = m.get('deRatio', 0)
    if de < 0.5:
        health_sub = min(100, health_sub + 15)
    elif de > 2:
        health_sub = max(0, health_sub - 20)
    elif de > 1:
        health_sub = max(0, health_sub - 5)

    ic = m.get('interestCoverage', 99)
    if ic < 1.5:
        health_sub = max(0, health_sub - 20)
    elif ic > 5:
        health_sub = min(100, health_sub + 5)

    # ---- Valuation Score (0-100) ----
    val_score = 50
    pe = m.get('peRatio', 0)
    if pe <= 0:
        val_score = 30  # negative earnings
    elif pe < 15:
        val_score = 85
    elif pe < 25:
        val_score = 70
    elif pe < 35:
        val_score = 55
    elif pe < 50:
        val_score = 40
    else:
        val_score = 20

    fcf_y = m.get('fcfYield', 0)
    if fcf_y > 8:
        val_score = min(100, val_score + 10)
    elif fcf_y < 0:
        val_score = max(0, val_score - 10)

    # ---- Red flag penalty ----
    penalty = 0
    for flag in red_flags:
        if flag['severity'] == 'high':
            penalty += 5
        elif flag['severity'] == 'medium':
            penalty += 3

    # ---- Composite Score ----
    composite = (
        growth_score * 0.25 +
        prof_score * 0.30 +
        health_sub * 0.30 +
        val_score * 0.15
    ) - penalty

    composite = max(0, min(100, round(composite)))

    return {
        'overall': composite,
        'growth': round(growth_score),
        'profitability': round(prof_score),
        'financialHealth': round(health_sub),
        'valuation': round(val_score),
        'label': _score_label(composite),
        'color': _score_color(composite),
    }


def _score_label(score):
    if score >= 80:
        return 'Excellent'
    elif score >= 65:
        return 'Good'
    elif score >= 50:
        return 'Fair'
    elif score >= 35:
        return 'Weak'
    else:
        return 'Poor'


def _score_color(score):
    if score >= 80:
        return '#00e676'
    elif score >= 65:
        return '#69f0ae'
    elif score >= 50:
        return '#ffca28'
    elif score >= 35:
        return '#ff9800'
    else:
        return '#f44336'


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def run_full_analysis(overview, income_data, balance_data, cashflow_data):
    """
    Run the complete three-stage analysis pipeline.
    Returns a comprehensive analysis result.
    """
    # Stage 1: Calculate metrics
    result = calculate_metrics(overview, income_data, balance_data, cashflow_data)
    metrics = result['metrics']
    historical = result['historical']

    # Stage 2: Detect red flags
    red_flags = detect_red_flags(metrics, historical)

    # Stage 3: Health score synthesis
    health_score = calculate_health_score(metrics, red_flags)

    # Build company info from overview
    company_info = {
        'name': overview.get('Name', ''),
        'ticker': overview.get('Symbol', ''),
        'sector': overview.get('Sector', ''),
        'industry': overview.get('Industry', ''),
        'description': overview.get('Description', ''),
        'exchange': overview.get('Exchange', ''),
        'currency': overview.get('Currency', 'USD'),
        'country': overview.get('Country', ''),
        'marketCap': safe_float(overview.get('MarketCapitalization')),
        'peRatio': safe_float(overview.get('PERatio')),
        'eps': safe_float(overview.get('EPS')),
        'dividendYield': safe_float(overview.get('DividendYield')) * 100,
        'beta': safe_float(overview.get('Beta')),
        'fiftyTwoWeekHigh': safe_float(overview.get('52WeekHigh')),
        'fiftyTwoWeekLow': safe_float(overview.get('52WeekLow')),
    }

    # Generate plain-English summary
    summary = _generate_summary(company_info, health_score, metrics, red_flags)

    return {
        'company': company_info,
        'healthScore': health_score,
        'metrics': metrics,
        'historical': historical,
        'redFlags': red_flags,
        'summary': summary,
    }


def _generate_summary(company, score, metrics, flags):
    """Generate a plain-English analysis summary for Beginner Mode."""
    name = company.get('name', 'This company')
    sector = company.get('sector', 'its sector')
    overall = score['overall']

    summary = f"{name} receives an overall health score of {overall}/100, rated as '{score['label']}'.\n\n"

    # Growth
    cagr = metrics.get('revenueCagr', 0)
    if cagr > 10:
        summary += f"📈 **Strong Growth**: Revenue has grown at {cagr:.1f}% annually, showing healthy business expansion.\n\n"
    elif cagr > 0:
        summary += f"📊 **Moderate Growth**: Revenue has grown at {cagr:.1f}% annually.\n\n"
    else:
        summary += f"📉 **Declining Revenue**: Revenue has been shrinking, which is a concern.\n\n"

    # Profitability
    nm = metrics.get('netMargin', 0)
    if nm > 15:
        summary += f"💰 **Highly Profitable**: The company keeps {nm:.1f}% of every dollar as profit — well above average.\n\n"
    elif nm > 0:
        summary += f"💵 **Profitable**: The company has a net profit margin of {nm:.1f}%.\n\n"
    else:
        summary += f"🔴 **Unprofitable**: The company is currently losing money on operations.\n\n"

    # Debt
    de = metrics.get('deRatio', 0)
    if de < 0.5:
        summary += "🛡️ **Low Debt**: The company has very conservative debt levels — a sign of financial stability.\n\n"
    elif de < 1.5:
        summary += "⚖️ **Moderate Debt**: Debt levels are manageable but worth monitoring.\n\n"
    else:
        summary += f"⚠️ **High Debt**: With a debt-to-equity ratio of {de:.1f}x, the company carries significant leverage.\n\n"

    # Red flags
    if flags:
        summary += f"🚩 **{len(flags)} Warning Signal{'s' if len(flags) > 1 else ''}**: "
        flag_titles = [f['title'] for f in flags]
        summary += ', '.join(flag_titles) + '.\n'

    return summary


# ============================================================
# METRIC TOOLTIPS (Educational Layer)
# ============================================================

METRIC_TOOLTIPS = {
    'grossMargin': {
        'name': 'Gross Margin',
        'simple': 'How much profit a company makes from its products before other expenses. Higher is better.',
        'detailed': 'Gross Margin = (Revenue - Cost of Goods Sold) / Revenue × 100. Measures the efficiency of production and pricing. A high gross margin means the company has a strong pricing advantage or low production costs.',
        'good': '> 40%', 'average': '20-40%', 'bad': '< 20%'
    },
    'operatingMargin': {
        'name': 'Operating Margin',
        'simple': 'How much profit a company makes from its core business operations. Higher is better.',
        'detailed': 'Operating Margin = Operating Income / Revenue × 100. Includes all operating costs like R&D, sales, and admin. Shows how well management controls costs.',
        'good': '> 20%', 'average': '10-20%', 'bad': '< 10%'
    },
    'netMargin': {
        'name': 'Net Profit Margin',
        'simple': 'The percentage of revenue that becomes actual profit after ALL expenses. The bottom line.',
        'detailed': 'Net Margin = Net Income / Revenue × 100. This is what remains after taxes, interest, and all other expenses. It\'s the most comprehensive profitability measure.',
        'good': '> 15%', 'average': '5-15%', 'bad': '< 5%'
    },
    'roe': {
        'name': 'Return on Equity (ROE)',
        'simple': "How efficiently a company uses shareholders' money to generate profits. Higher means better returns for investors.",
        'detailed': "ROE = Net Income / Shareholders' Equity × 100. Measures how much profit a company generates with the money shareholders have invested. Consistently high ROE suggests a competitive moat.",
        'good': '> 15%', 'average': '8-15%', 'bad': '< 8%'
    },
    'roa': {
        'name': 'Return on Assets (ROA)',
        'simple': 'How efficiently a company uses all its assets to generate profits.',
        'detailed': 'ROA = Net Income / Total Assets × 100. Measures how productively a company uses everything it owns. Useful for comparing companies of different sizes.',
        'good': '> 10%', 'average': '5-10%', 'bad': '< 5%'
    },
    'roic': {
        'name': 'Return on Invested Capital (ROIC)',
        'simple': 'How well a company generates returns on money invested in the business.',
        'detailed': 'ROIC = NOPAT / Invested Capital × 100. Considered one of the best measures of business quality. A ROIC above the cost of capital means the company is creating value.',
        'good': '> 15%', 'average': '8-15%', 'bad': '< 8%'
    },
    'peRatio': {
        'name': 'Price-to-Earnings (PE) Ratio',
        'simple': 'How much investors are willing to pay per dollar of earnings. Lower may mean better value.',
        'detailed': 'PE = Stock Price / Earnings Per Share. A high PE may indicate growth expectations or overvaluation. A low PE may mean the stock is undervalued or has problems. Always compare within the same industry.',
        'good': '< 20', 'average': '20-35', 'bad': '> 35'
    },
    'pbRatio': {
        'name': 'Price-to-Book (PB) Ratio',
        'simple': 'Compares the stock price to the company\'s net asset value. Below 1 could mean the stock is undervalued.',
        'detailed': 'PB = Market Cap / Book Value. Measures how much you\'re paying compared to what the company owns minus what it owes. Particularly useful for financial companies and asset-heavy industries.',
        'good': '< 3', 'average': '3-5', 'bad': '> 5'
    },
    'psRatio': {
        'name': 'Price-to-Sales (PS) Ratio',
        'simple': 'How much investors pay per dollar of the company\'s revenue.',
        'detailed': 'PS = Market Cap / Total Revenue. Useful for evaluating companies that are not yet profitable. Lower values suggest better value relative to revenue generation.',
        'good': '< 3', 'average': '3-8', 'bad': '> 8'
    },
    'evEbitda': {
        'name': 'EV/EBITDA',
        'simple': 'A widely used valuation measure that accounts for debt. Lower values suggest better value.',
        'detailed': 'Enterprise Value / EBITDA. Considered more reliable than PE because it accounts for the company\'s debt and is not affected by different tax or depreciation strategies.',
        'good': '< 12', 'average': '12-20', 'bad': '> 20'
    },
    'currentRatio': {
        'name': 'Current Ratio',
        'simple': 'Can the company pay its short-term bills? Above 1 means yes.',
        'detailed': 'Current Ratio = Current Assets / Current Liabilities. Measures short-term liquidity. A ratio above 1 means the company can cover its near-term obligations.',
        'good': '> 1.5', 'average': '1-1.5', 'bad': '< 1'
    },
    'deRatio': {
        'name': 'Debt-to-Equity Ratio',
        'simple': 'How much the company relies on borrowed money versus its own. Lower is generally safer.',
        'detailed': "D/E = Total Debt / Shareholders' Equity. Shows the balance between debt financing and equity financing. High leverage increases risk but can amplify returns.",
        'good': '< 0.5', 'average': '0.5-1.5', 'bad': '> 1.5'
    },
    'interestCoverage': {
        'name': 'Interest Coverage Ratio',
        'simple': 'Can the company afford its debt payments? Higher numbers mean more safety.',
        'detailed': 'Interest Coverage = Operating Income / Interest Expense. Shows how many times the company can pay its interest charges from earnings. Below 1.5 is a serious red flag.',
        'good': '> 5', 'average': '2-5', 'bad': '< 2'
    },
    'fcfYield': {
        'name': 'Free Cash Flow Yield',
        'simple': 'How much actual cash the business generates relative to its price. Like a "real" earnings yield.',
        'detailed': 'FCF Yield = Free Cash Flow / Market Cap × 100. FCF is the cash left after all capital expenditures. High FCF yield may indicate undervaluation.',
        'good': '> 5%', 'average': '2-5%', 'bad': '< 2%'
    },
    'revenueCagr': {
        'name': 'Revenue CAGR',
        'simple': 'The average annual growth rate of revenue over multiple years. Shows the trend.',
        'detailed': 'Compound Annual Growth Rate of revenue smooths out year-to-year volatility and shows the underlying growth trajectory.',
        'good': '> 10%', 'average': '3-10%', 'bad': '< 3%'
    },
}

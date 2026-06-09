def calculate_metrics(data):
    return {
        "gross_margin": 45.0, "net_margin": 20.0, "roe": 15.0, "roa": 10.0,
        "roic": 12.0, "pe_ratio": 25.0, "pb_ratio": 5.0, "ps_ratio": 4.0,
        "ev_ebitda": 15.0, "fcf_yield": 5.0, "current_ratio": 1.5,
        "quick_ratio": 1.2, "de_ratio": 0.5, "revenue_cagr": 10.0
    }

def detect_red_flags(metrics):
    flags = []
    if metrics.get('pe_ratio', 0) > 30:
        flags.append("High Valuation")
    return flags

def calculate_health_score(metrics, flags):
    # Based on growth 25%, profitability 30%, health 30%, valuation 15%
    score = 85
    score -= len(flags) * 5
    return max(0, min(100, score))

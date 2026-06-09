from backend.analysis_engine import calculate_health_score, calculate_metrics

def test_health_score():
    score = calculate_health_score({'pe_ratio': 20}, [])
    assert score == 85

def test_metrics_calculation():
    metrics = calculate_metrics({})
    assert 'pe_ratio' in metrics

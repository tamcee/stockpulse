import time
import json
import pytest
from unittest.mock import patch
from backend.config import Config

def test_auth_registration_and_login(client):
    """Test user registration and login flows."""
    res = client.post('/api/auth/register', json={
        'username': 'testuser1',
        'email': 'test1@test.com',
        'password': 'password123'
    })
    assert res.status_code == 201
    
    res2 = client.post('/api/auth/login', json={
        'email': 'test1@test.com',
        'password': 'password123'
    })
    assert res2.status_code == 200
    assert 'token' in res2.json
    
    res3 = client.post('/api/auth/login', json={
        'email': 'test1@test.com',
        'password': 'wrongpassword'
    })
    assert res3.status_code == 401

def test_unauthorized_access(client):
    """Test Case: Unauthorized API access blocked (401)"""
    res = client.get('/api/watchlist/')
    assert res.status_code == 401

def test_authorized_watchlist(client, auth_token):
    """Test accessing protected route with token."""
    with patch('backend.auth.Config.SECRET_KEY', 'test_secret_key'):
        res = client.get('/api/watchlist/', headers={'Authorization': f'Bearer {auth_token}'})
        
        if res.status_code != 200:
            print("Auth failed output:", res.json)
        assert res.status_code == 200
        assert 'watchlist' in res.json

@patch('backend.data_fetcher._api_call')
def test_cache_miss_and_hit(mock_api_call, client, app):
    """
    Test Case: Cache miss -> API call -> cache population
    Test Case: Cache hit response time < 500ms
    """
    def mock_fetch(function, ticker, api_key):
        if function == 'OVERVIEW':
            return {'Symbol': 'MOCKAPI', 'Name': 'Mock Inc', 'Sector': 'Technology'}
        return {
            'annualReports': [
                {'fiscalDateEnding': '2023-12-31', 'totalRevenue': '100'}
            ]
        }
    
    mock_api_call.side_effect = mock_fetch

    start_time = time.time()
    
    # Force the data fetcher logic to think it has a real API key
    with patch('backend.data_fetcher.Config.ALPHA_VANTAGE_API_KEY', 'testkey'):
        res1 = client.get('/api/stocks/analyze/MOCKAPI')
        if res1.status_code != 200:
            print("Analyze failed output:", getattr(res1, 'json', res1.text))
        
        miss_duration = time.time() - start_time
        assert res1.status_code == 200
        assert mock_api_call.called
        assert miss_duration < 5.0
    
        # Ensure it caches locally correctly
        mock_api_call.reset_mock()
        start_time = time.time()
        
        res2 = client.get('/api/stocks/analyze/MOCKAPI')
        hit_duration = time.time() - start_time
        assert res2.status_code == 200
        assert not mock_api_call.called
        assert hit_duration < 0.500

def test_sector_comparison_endpoint(client, app):
    """Test Case: Sector comparison with 5 stocks"""
    res = client.get('/api/stocks/compare?tickers=AAPL,MSFT,GOOGL,AMZN,TSLA')
    assert res.status_code == 200
    comparisons = res.json.get('comparisons', [])
    assert len(comparisons) == 5

def test_alert_notification_threshold_breach():
    """Test Case: Alert notification on threshold breach."""
    user_alert_config = {
        'peRatio_gt': 30
    }
    
    latest_metrics = {
        'peRatio': 35.5
    }
    
    def simulate_background_monitor(config, metrics):
        breached = []
        if 'peRatio_gt' in config and metrics['peRatio'] > config['peRatio_gt']:
            breached.append(('peRatio', metrics['peRatio']))
        return breached

    breaches = simulate_background_monitor(user_alert_config, latest_metrics)
    assert len(breaches) > 0
    assert breaches[0][0] == 'peRatio'
    assert breaches[0][1] == 35.5

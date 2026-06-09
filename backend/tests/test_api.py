def test_ping(client):
    res = client.get('/ping')
    assert res.status_code == 200

def test_watchlist_unauthorized(client):
    res = client.get('/api/watchlist/')
    assert res.status_code in [401, 403, 500]

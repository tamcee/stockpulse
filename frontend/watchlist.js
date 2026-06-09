async function loadWatchlist() {
    const data = await api.request('/api/watchlist/');
    console.log("Watchlist loaded:", data.items);
}

async function addToWatchlist(ticker) {
    await api.request('/api/watchlist/', { method: 'POST', body: JSON.stringify({ticker}) });
}

async function removeFromWatchlist(ticker) {
    await api.request(`/api/watchlist/${ticker}`, { method: 'DELETE' });
}

async function setAlert(ticker, config) {
    await api.request(`/api/watchlist/${ticker}/alerts`, { method: 'PUT', body: JSON.stringify(config) });
}

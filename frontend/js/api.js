/**
 * API Client — Communicates with the Flask backend.
 * Handles authentication headers and error responses.
 */
const API = {
    BASE_URL: '',  // Same origin — Flask serves both

    /**
     * Make an authenticated API request.
     */
    async request(endpoint, options = {}) {
        const url = `${this.BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        // Attach JWT if available
        const token = localStorage.getItem('auth_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers,
            });

            const data = await response.json();

            if (!response.ok) {
                if (response.status === 401) {
                    // Token expired or invalid
                    localStorage.removeItem('auth_token');
                    localStorage.removeItem('auth_user');
                    if (typeof Auth !== 'undefined') Auth.updateUI();
                }
                throw new Error(data.error || `Request failed (${response.status})`);
            }

            return data;
        } catch (err) {
            if (err.message.includes('Failed to fetch')) {
                throw new Error('Server unavailable. Please ensure the backend is running.');
            }
            throw err;
        }
    },

    // ---- Stock Endpoints ----

    async searchStocks(query) {
        if (!query || query.length < 1) return { results: [] };
        return this.request(`/api/stocks/search?q=${encodeURIComponent(query)}`);
    },

    async analyzeStock(ticker) {
        return this.request(`/api/stocks/analyze/${encodeURIComponent(ticker)}`);
    },

    async compareStocks(tickers) {
        const tickerStr = tickers.join(',');
        return this.request(`/api/stocks/compare?tickers=${encodeURIComponent(tickerStr)}`);
    },

    async getTooltips() {
        return this.request('/api/stocks/tooltips');
    },

    // ---- Auth Endpoints ----

    async register(username, email, password) {
        return this.request('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password }),
        });
    },

    async login(email, password) {
        return this.request('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
    },

    async getCurrentUser() {
        return this.request('/api/auth/me');
    },

    // ---- Watchlist Endpoints ----

    async getWatchlist() {
        return this.request('/api/watchlist/');
    },

    async addToWatchlist(ticker, companyName) {
        return this.request('/api/watchlist/', {
            method: 'POST',
            body: JSON.stringify({ ticker, company_name: companyName }),
        });
    },

    async removeFromWatchlist(ticker) {
        return this.request(`/api/watchlist/${encodeURIComponent(ticker)}`, {
            method: 'DELETE',
        });
    },

    async updateAlerts(ticker, alertConfig) {
        return this.request(`/api/watchlist/${encodeURIComponent(ticker)}/alerts`, {
            method: 'PUT',
            body: JSON.stringify(alertConfig),
        });
    },
};

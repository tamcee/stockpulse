/**
 * Watchlist UI Module
 * Manages the watchlist view with localStorage fallback for unauthenticated users.
 */
const Watchlist = {
    localKey: 'watchlist_local',

    /**
     * Get watchlist items — from API if logged in, localStorage otherwise.
     */
    async getItems() {
        if (Auth.isLoggedIn()) {
            try {
                const data = await API.getWatchlist();
                return data.watchlist || [];
            } catch (e) {
                console.error('Failed to fetch watchlist:', e);
                return this._getLocal();
            }
        }
        return this._getLocal();
    },

    /**
     * Add a stock to the watchlist from the analysis view.
     */
    async addFromAnalysis(ticker, companyName) {
        if (Auth.isLoggedIn()) {
            try {
                await API.addToWatchlist(ticker, companyName);
                App.showToast(`${ticker} added to your watchlist!`, 'success');
            } catch (e) {
                if (e.message.includes('already')) {
                    App.showToast(`${ticker} is already in your watchlist.`, 'info');
                } else {
                    App.showToast(e.message, 'error');
                }
            }
        } else {
            // localStorage fallback
            const items = this._getLocal();
            if (items.find(i => i.ticker === ticker)) {
                App.showToast(`${ticker} is already in your watchlist.`, 'info');
                return;
            }
            items.push({ ticker, company_name: companyName, added_at: new Date().toISOString() });
            this._setLocal(items);
            App.showToast(`${ticker} added to watchlist! Sign in to sync across devices.`, 'success');
        }
    },

    /**
     * Remove a stock from watchlist.
     */
    async removeItem(ticker) {
        if (Auth.isLoggedIn()) {
            try {
                await API.removeFromWatchlist(ticker);
                App.showToast(`${ticker} removed from watchlist.`, 'info');
            } catch (e) {
                App.showToast(e.message, 'error');
            }
        } else {
            const items = this._getLocal().filter(i => i.ticker !== ticker);
            this._setLocal(items);
            App.showToast(`${ticker} removed from watchlist.`, 'info');
        }
        this.renderView();
    },

    /**
     * Render the watchlist page view.
     */
    async renderView() {
        const content = document.getElementById('pageContent');
        content.innerHTML = `
            <div class="page-header animate-in">
                <h1 class="page-title">📋 Watchlist</h1>
                <p class="page-subtitle">Track your favorite stocks and monitor key metrics.</p>
            </div>
            <div class="loading-container"><div class="loading-spinner"></div><div class="loading-text">Loading watchlist...</div></div>
        `;

        const items = await this.getItems();

        if (items.length === 0) {
            content.innerHTML = `
                <div class="page-header animate-in">
                    <h1 class="page-title">📋 Watchlist</h1>
                    <p class="page-subtitle">Track your favorite stocks and monitor key metrics.</p>
                </div>
                <div class="empty-state animate-in animate-in-delay-1">
                    <div class="empty-state-icon">📋</div>
                    <div class="empty-state-title">Your Watchlist is Empty</div>
                    <div class="empty-state-text">Search for a stock and click "Add to Watchlist" to start tracking companies that interest you.</div>
                    <br>
                    <button class="btn btn-primary" onclick="App.navigateTo('dashboard')">Explore Stocks</button>
                </div>
            `;
            return;
        }

        // Fetch analysis for each watchlist item
        let cardsHtml = '';
        for (const item of items) {
            try {
                const data = await API.analyzeStock(item.ticker);
                const hs = data.analysis?.healthScore;
                const m = data.analysis?.metrics;
                const scoreColor = hs ? Analysis.getScoreColor(hs.overall) : '#64748b';

                cardsHtml += `
                    <div class="card watchlist-card animate-in" onclick="App.loadStock('${item.ticker}')">
                        <button class="watchlist-remove" onclick="event.stopPropagation(); Watchlist.removeItem('${item.ticker}')" title="Remove">✕</button>
                        <div class="watchlist-card-header">
                            <div class="watchlist-ticker">${item.ticker}</div>
                            <div class="watchlist-score-mini" style="background:${scoreColor}22; color:${scoreColor};">
                                ${hs ? hs.overall + '/100' : 'N/A'}
                            </div>
                        </div>
                        <div class="watchlist-name">${item.company_name || data.analysis?.company?.name || ''}</div>
                        <div class="grid-2" style="gap:8px;">
                            <div>
                                <div style="font-size:11px; color:var(--text-muted);">Revenue</div>
                                <div style="font-size:14px; font-weight:700;">${m ? Analysis.formatCurrency(m.totalRevenue) : 'N/A'}</div>
                            </div>
                            <div>
                                <div style="font-size:11px; color:var(--text-muted);">Net Margin</div>
                                <div style="font-size:14px; font-weight:700;">${m ? m.netMargin.toFixed(1) + '%' : 'N/A'}</div>
                            </div>
                            <div>
                                <div style="font-size:11px; color:var(--text-muted);">PE Ratio</div>
                                <div style="font-size:14px; font-weight:700;">${m && m.peRatio ? m.peRatio.toFixed(1) : 'N/A'}</div>
                            </div>
                            <div>
                                <div style="font-size:11px; color:var(--text-muted);">D/E Ratio</div>
                                <div style="font-size:14px; font-weight:700;">${m ? m.deRatio.toFixed(2) : 'N/A'}</div>
                            </div>
                        </div>
                    </div>
                `;
            } catch (e) {
                cardsHtml += `
                    <div class="card watchlist-card">
                        <button class="watchlist-remove" onclick="event.stopPropagation(); Watchlist.removeItem('${item.ticker}')" title="Remove">✕</button>
                        <div class="watchlist-ticker">${item.ticker}</div>
                        <div class="watchlist-name">${item.company_name || ''}</div>
                        <div style="color:var(--text-muted); font-size:13px;">Unable to load data</div>
                    </div>
                `;
            }
        }

        content.innerHTML = `
            <div class="page-header animate-in">
                <h1 class="page-title">📋 Watchlist</h1>
                <p class="page-subtitle">Tracking ${items.length} stock${items.length > 1 ? 's' : ''}. Click a card to view full analysis.</p>
            </div>
            <div class="watchlist-grid">${cardsHtml}</div>
        `;
    },

    _getLocal() {
        try {
            return JSON.parse(localStorage.getItem(this.localKey)) || [];
        } catch { return []; }
    },

    _setLocal(items) {
        localStorage.setItem(this.localKey, JSON.stringify(items));
    },
};

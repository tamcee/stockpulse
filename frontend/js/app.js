/**
 * Main Application Controller
 * Manages navigation, search, mode toggle, and page rendering.
 */
const App = {
    currentView: 'dashboard',
    currentMode: 'beginner',
    searchTimeout: null,

    init() {
        // Restore mode
        this.currentMode = localStorage.getItem('analysis_mode') || 'beginner';

        // Init modules
        Auth.init();
        Analysis.loadTooltips();

        // Setup event listeners
        this._setupNavigation();
        this._setupSearch();
        this._setupModeToggle();
        this._setupMobileMenu();

        // Update mode toggle UI
        this._updateModeUI();

        // Load dashboard
        this.navigateTo('dashboard');
    },

    // ============================================================
    // NAVIGATION
    // ============================================================

    _setupNavigation() {
        document.querySelectorAll('.nav-item[data-view]').forEach(item => {
            item.addEventListener('click', () => {
                this.navigateTo(item.dataset.view);
                // Close mobile sidebar
                document.getElementById('sidebar').classList.remove('open');
                document.getElementById('sidebarOverlay').classList.remove('visible');
            });
        });

        document.getElementById('nav-api-settings').addEventListener('click', () => {
            this._showApiSettings();
        });
    },

    navigateTo(view) {
        this.currentView = view;

        // Update nav active state
        document.querySelectorAll('.nav-item[data-view]').forEach(item => {
            item.classList.toggle('active', item.dataset.view === view);
        });

        // Render view
        switch (view) {
            case 'dashboard': this._renderDashboard(); break;
            case 'analysis': this._renderAnalysisPlaceholder(); break;
            case 'compare': this._renderCompare(); break;
            case 'watchlist': Watchlist.renderView(); break;
        }
    },

    // ============================================================
    // SEARCH
    // ============================================================

    _setupSearch() {
        const input = document.getElementById('searchInput');
        const dropdown = document.getElementById('searchDropdown');

        input.addEventListener('input', () => {
            clearTimeout(this.searchTimeout);
            const query = input.value.trim();

            if (query.length < 1) {
                dropdown.classList.remove('visible');
                return;
            }

            this.searchTimeout = setTimeout(async () => {
                try {
                    const data = await API.searchStocks(query);
                    this._renderSearchResults(data.results);
                } catch (e) {
                    dropdown.classList.remove('visible');
                }
            }, 200);
        });

        input.addEventListener('focus', () => {
            if (input.value.trim().length >= 1) {
                dropdown.classList.add('visible');
            }
        });

        // Close dropdown on outside click
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                dropdown.classList.remove('visible');
            }
        });

        // Enter key shortcut
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const query = input.value.trim().toUpperCase();
                if (query) {
                    this.loadStock(query);
                    dropdown.classList.remove('visible');
                    input.blur();
                }
            }
        });
    },

    _renderSearchResults(results) {
        const dropdown = document.getElementById('searchDropdown');

        if (!results || results.length === 0) {
            dropdown.innerHTML = `
                <div style="padding:16px; text-align:center; color:var(--text-muted); font-size:13px;">
                    No results found. Try a ticker symbol (e.g., AAPL)
                </div>
            `;
            dropdown.classList.add('visible');
            return;
        }

        dropdown.innerHTML = results.map(r => `
            <div class="search-result-item" onclick="App.loadStock('${r.ticker}')">
                <span class="search-result-ticker">${r.ticker}</span>
                <span class="search-result-name">${r.name}</span>
            </div>
        `).join('');

        dropdown.classList.add('visible');
    },

    // ============================================================
    // STOCK LOADING
    // ============================================================

    async loadStock(ticker) {
        ticker = ticker.toUpperCase();

        // Close search dropdown
        document.getElementById('searchDropdown').classList.remove('visible');
        document.getElementById('searchInput').value = ticker;

        // Navigate to analysis view
        this.currentView = 'analysis';
        document.querySelectorAll('.nav-item[data-view]').forEach(item => {
            item.classList.toggle('active', item.dataset.view === 'analysis');
        });

        // Show loading
        const content = document.getElementById('pageContent');
        content.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">Analyzing ${ticker}...</div>
                <div style="font-size:12px; color:var(--text-muted); margin-top:8px;">Running financial analysis engine</div>
            </div>
        `;

        try {
            const data = await API.analyzeStock(ticker);

            if (this.currentMode === 'beginner') {
                Analysis.renderBeginnerView(data);
            } else {
                Analysis.renderAdvancedView(data);
            }

            if (data.isDemo) {
                this.showToast(`Showing demo data for ${ticker}. Set an API key for live data.`, 'info');
            }
        } catch (e) {
            content.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">❌</div>
                    <div class="empty-state-title">Unable to Analyze ${ticker}</div>
                    <div class="empty-state-text">${e.message}</div>
                    <br>
                    <button class="btn btn-primary" onclick="App.navigateTo('dashboard')">Back to Dashboard</button>
                </div>
            `;
        }
    },

    // ============================================================
    // MODE TOGGLE
    // ============================================================

    _setupModeToggle() {
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.currentMode = btn.dataset.mode;
                localStorage.setItem('analysis_mode', this.currentMode);
                this._updateModeUI();

                // Re-render current analysis if viewing one
                if (Analysis.currentData && this.currentView === 'analysis') {
                    if (this.currentMode === 'beginner') {
                        Analysis.renderBeginnerView(Analysis.currentData);
                    } else {
                        Analysis.renderAdvancedView(Analysis.currentData);
                    }
                }
            });
        });
    },

    _updateModeUI() {
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === this.currentMode);
        });
    },

    // ============================================================
    // MOBILE MENU
    // ============================================================

    _setupMobileMenu() {
        const toggle = document.getElementById('menuToggle');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');

        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('visible');
        });

        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('visible');
        });
    },

    // ============================================================
    // VIEWS
    // ============================================================

    _renderDashboard() {
        const content = document.getElementById('pageContent');

        const featuredStocks = [
            { ticker: 'AAPL', name: 'Apple Inc.', sector: 'Technology' },
            { ticker: 'MSFT', name: 'Microsoft Corp.', sector: 'Technology' },
            { ticker: 'GOOGL', name: 'Alphabet Inc.', sector: 'Technology' },
            { ticker: 'AMZN', name: 'Amazon.com Inc.', sector: 'Consumer Cyclical' },
            { ticker: 'TSLA', name: 'Tesla Inc.', sector: 'Consumer Cyclical' },
        ];

        content.innerHTML = `
            <div class="dashboard-hero animate-in">
                <div class="dashboard-hero-title">Intelligent Fundamental Stock Analysis</div>
                <div class="dashboard-hero-text">
                    Democratizing investment research with automated analysis, interactive visualizations,
                    and plain-English insights. Analyze any stock in seconds.
                </div>
                <button class="btn btn-primary" onclick="document.getElementById('searchInput').focus()">
                    Search a Stock to Begin
                </button>
            </div>

            <div class="page-header animate-in animate-in-delay-1">
                <h2 style="font-size:20px; font-weight:700; margin-bottom:4px;">Featured Stocks</h2>
                <p class="page-subtitle">Click any stock to view its full analysis. Demo data available instantly.</p>
            </div>

            <div class="featured-stocks animate-in animate-in-delay-2">
                ${featuredStocks.map(s => `
                    <div class="card featured-stock-card" onclick="App.loadStock('${s.ticker}')">
                        <div class="featured-stock-ticker">${s.ticker}</div>
                        <div class="featured-stock-name">${s.name}</div>
                        <span class="featured-stock-sector">${s.sector}</span>
                    </div>
                `).join('')}
            </div>

            <div class="grid-3 animate-in animate-in-delay-3" style="margin-top:32px;">
                <div class="card" style="text-align:center; padding:28px;">
                    <div style="font-size:16px; font-weight:700; margin-bottom:6px;">20+ Financial Ratios</div>
                    <div style="font-size:13px; color:var(--text-muted);">Automated calculation of profitability, growth, valuation, and health metrics.</div>
                </div>
                <div class="card" style="text-align:center; padding:28px;">
                    <div style="font-size:16px; font-weight:700; margin-bottom:6px;">Dual-Mode Interface</div>
                    <div style="font-size:13px; color:var(--text-muted);">Beginner mode with plain-English summaries or Advanced mode with full data.</div>
                </div>
                <div class="card" style="text-align:center; padding:28px;">
                    <div style="font-size:16px; font-weight:700; margin-bottom:6px;">Red Flag Detection</div>
                    <div style="font-size:13px; color:var(--text-muted);">Automatic pattern recognition to identify financial warning signals.</div>
                </div>
            </div>
        `;
    },

    _renderAnalysisPlaceholder() {
        if (Analysis.currentData) {
            if (this.currentMode === 'beginner') {
                Analysis.renderBeginnerView(Analysis.currentData);
            } else {
                Analysis.renderAdvancedView(Analysis.currentData);
            }
            return;
        }

        const content = document.getElementById('pageContent');
        content.innerHTML = `
            <div class="empty-state animate-in">
                <div class="empty-state-title">Search for a Stock</div>
                <div class="empty-state-text">Use the search bar above to find a company by name or ticker symbol. Try AAPL, MSFT, GOOGL, AMZN, or TSLA for instant demo data.</div>
            </div>
        `;
    },

    _renderCompare() {
        const content = document.getElementById('pageContent');
        content.innerHTML = `
            <div class="page-header animate-in">
                <h1 class="page-title">Sector Comparison</h1>
                <p class="page-subtitle">Compare up to 5 stocks side-by-side across key metrics.</p>
            </div>

            <div class="card animate-in animate-in-delay-1" style="margin-bottom:24px;">
                <div class="card-title" style="margin-bottom:16px;">Select Stocks to Compare</div>
                <div class="compare-input-group" id="compareChips"></div>
                <div style="display:flex; gap:10px; align-items:center;">
                    <input type="text" class="form-input" id="compareInput" placeholder="Enter ticker symbol (e.g. AAPL)" style="max-width:280px;">
                    <button class="btn btn-primary btn-sm" id="addCompareBtn">Add</button>
                    <button class="btn btn-secondary btn-sm" id="quickCompareBtn">Quick: FAANG</button>
                </div>
            </div>

            <div id="compareResults"></div>
        `;

        this._compareTickers = [];
        this._setupCompare();
    },

    _compareTickers: [],

    _setupCompare() {
        const input = document.getElementById('compareInput');
        const addBtn = document.getElementById('addCompareBtn');
        const quickBtn = document.getElementById('quickCompareBtn');

        const addTicker = () => {
            const ticker = input.value.trim().toUpperCase();
            if (!ticker) return;
            if (this._compareTickers.includes(ticker)) {
                this.showToast(`${ticker} already added.`, 'info');
                return;
            }
            if (this._compareTickers.length >= 5) {
                this.showToast('Maximum 5 stocks for comparison.', 'error');
                return;
            }
            this._compareTickers.push(ticker);
            input.value = '';
            this._updateCompareChips();
        };

        addBtn.addEventListener('click', addTicker);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') addTicker();
        });

        quickBtn.addEventListener('click', () => {
            this._compareTickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'];
            this._updateCompareChips();
            this._runComparison();
        });
    },

    _updateCompareChips() {
        const container = document.getElementById('compareChips');
        container.innerHTML = this._compareTickers.map(t => `
            <div class="ticker-chip">
                ${t}
                <button class="ticker-chip-remove" onclick="App._removeCompareTicker('${t}')">×</button>
            </div>
        `).join('');

        if (this._compareTickers.length >= 2) {
            container.innerHTML += `<button class="btn btn-primary btn-sm" onclick="App._runComparison()">Compare ${this._compareTickers.length} Stocks</button>`;
        }
    },

    _removeCompareTicker(ticker) {
        this._compareTickers = this._compareTickers.filter(t => t !== ticker);
        this._updateCompareChips();
    },

    async _runComparison() {
        const results = document.getElementById('compareResults');
        results.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">Comparing ${this._compareTickers.length} stocks...</div>
            </div>
        `;

        try {
            const data = await API.compareStocks(this._compareTickers);
            const comparisons = data.comparisons;

            if (!comparisons || comparisons.length === 0) {
                results.innerHTML = '<div class="empty-state"><div class="empty-state-title">No data found</div></div>';
                return;
            }

            results.innerHTML = `
                <div class="card animate-in" style="margin-bottom:24px;">
                    <div class="card-title" style="margin-bottom:16px;">Health Score Comparison</div>
                    <div class="chart-container" id="compareHealthChart" style="height:300px;"></div>
                </div>

                <div class="card animate-in animate-in-delay-1" style="margin-bottom:24px;">
                    <div class="card-title" style="margin-bottom:16px;">Profitability Comparison</div>
                    <div class="chart-container" id="compareProfChart" style="height:300px;"></div>
                </div>

                <div class="card animate-in animate-in-delay-2" style="margin-bottom:24px;">
                    <div class="card-title" style="margin-bottom:16px;">Valuation Comparison</div>
                    <div class="chart-container" id="compareValChart" style="height:300px;"></div>
                </div>

                <div class="card animate-in animate-in-delay-3">
                    <div class="card-title" style="margin-bottom:16px;">Detailed Comparison Table</div>
                    ${this._renderComparisonTable(comparisons)}
                </div>
            `;

            setTimeout(() => {
                Charts.createHealthComparisonChart('compareHealthChart', comparisons);

                Charts.createMultiComparisonChart('compareProfChart', comparisons, [
                    { key: 'grossMargin', label: 'Gross Margin', suffix: '%' },
                    { key: 'operatingMargin', label: 'Op. Margin', suffix: '%' },
                    { key: 'netMargin', label: 'Net Margin', suffix: '%' },
                    { key: 'roe', label: 'ROE', suffix: '%' },
                ]);

                Charts.createMultiComparisonChart('compareValChart', comparisons, [
                    { key: 'peRatio', label: 'PE Ratio', suffix: 'x' },
                    { key: 'pbRatio', label: 'PB Ratio', suffix: 'x' },
                    { key: 'evEbitda', label: 'EV/EBITDA', suffix: 'x' },
                    { key: 'fcfYield', label: 'FCF Yield', suffix: '%' },
                ]);
            }, 100);

        } catch (e) {
            results.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">❌</div>
                    <div class="empty-state-title">Comparison Failed</div>
                    <div class="empty-state-text">${e.message}</div>
                </div>
            `;
        }
    },

    _renderComparisonTable(comparisons) {
        const metricsList = [
            { label: 'Health Score', key: 'healthScore.overall', format: v => v + '/100', higherBetter: true },
            { label: 'Revenue', key: 'metrics.totalRevenue', format: v => Analysis.formatCurrency(v), higherBetter: true },
            { label: 'Net Margin', key: 'metrics.netMargin', format: v => v?.toFixed(1) + '%', higherBetter: true },
            { label: 'ROE', key: 'metrics.roe', format: v => v?.toFixed(1) + '%', higherBetter: true },
            { label: 'PE Ratio', key: 'metrics.peRatio', format: v => v?.toFixed(1) + 'x', higherBetter: false },
            { label: 'D/E Ratio', key: 'metrics.deRatio', format: v => v?.toFixed(2) + 'x', higherBetter: false },
            { label: 'Revenue CAGR', key: 'metrics.revenueCagr', format: v => v?.toFixed(1) + '%', higherBetter: true },
            { label: 'FCF Yield', key: 'metrics.fcfYield', format: v => v?.toFixed(1) + '%', higherBetter: true },
        ];

        const getValue = (comp, key) => {
            const parts = key.split('.');
            let val = comp.analysis;
            for (const p of parts) val = val?.[p];
            return val;
        };

        const cols = comparisons.length + 1;
        const gridCols = `grid-template-columns: 140px repeat(${comparisons.length}, 1fr)`;

        let headerHtml = `<div class="comparison-header" style="${gridCols};">
            <div>Metric</div>
            ${comparisons.map(c => `<div style="text-align:center;">${c.ticker}</div>`).join('')}
        </div>`;

        let rowsHtml = metricsList.map(metric => {
            const values = comparisons.map(c => getValue(c, metric.key));
            const numericValues = values.filter(v => v !== null && v !== undefined && !isNaN(v));
            const best = metric.higherBetter ? Math.max(...numericValues) : Math.min(...numericValues);

            return `<div class="comparison-row" style="${gridCols};">
                <div style="font-weight:600; font-size:13px;">${metric.label}</div>
                ${values.map(v => {
                    const isBest = v === best && numericValues.length > 1;
                    return `<div style="text-align:center; font-size:14px; font-weight:600;" class="${isBest ? 'comparison-best' : ''}">${v !== null && v !== undefined ? metric.format(v) : 'N/A'}</div>`;
                }).join('')}
            </div>`;
        }).join('');

        return `<div class="comparison-grid">${headerHtml}${rowsHtml}</div>`;
    },

    // ============================================================
    // API SETTINGS
    // ============================================================

    _showApiSettings() {
        const modal = document.getElementById('authModal');
        const title = document.getElementById('authModalTitle');
        const body = document.getElementById('authModalBody');

        title.textContent = 'API Settings';
        body.innerHTML = `
            <form id="apiSettingsForm">
                <div class="form-group">
                    <label class="form-label">Alpha Vantage API Key</label>
                    <input type="text" class="form-input" id="apiKeyInput" placeholder="Enter your API key" value="${localStorage.getItem('alpha_vantage_key') || ''}">
                    <div style="font-size:12px; color:var(--text-muted); margin-top:6px;">
                        Get a free key at <a href="https://www.alphavantage.co/support/#api-key" target="_blank">alphavantage.co</a>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%;">Save Settings</button>
                <p style="font-size:12px; color:var(--text-muted); margin-top:12px; text-align:center;">
                    Without an API key, the platform uses built-in demo data for 5 stocks (AAPL, MSFT, GOOGL, AMZN, TSLA).
                </p>
            </form>
        `;

        document.getElementById('apiSettingsForm').addEventListener('submit', (e) => {
            e.preventDefault();
            const key = document.getElementById('apiKeyInput').value.trim();
            if (key) {
                localStorage.setItem('alpha_vantage_key', key);
                this.showToast('API key saved!', 'success');
            } else {
                localStorage.removeItem('alpha_vantage_key');
                this.showToast('API key removed. Using demo data.', 'info');
            }
            modal.classList.remove('visible');
        });

        modal.classList.add('visible');
    },

    // ============================================================
    // TOASTS
    // ============================================================

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `${message}`;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(40px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    },
};

// ============================================================
// BOOTSTRAP
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

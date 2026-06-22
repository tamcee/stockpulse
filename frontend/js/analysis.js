/**
 * Analysis Display Module
 * Renders the stock analysis views for both Beginner and Advanced modes.
 */
const Analysis = {
    currentData: null,
    tooltips: null,

    async loadTooltips() {
        if (!this.tooltips) {
            try {
                const data = await API.getTooltips();
                this.tooltips = data.tooltips;
            } catch (e) {
                this.tooltips = {};
            }
        }
    },

    /**
     * Format currency numbers.
     */
    formatCurrency(num) {
        if (num === null || num === undefined) return 'N/A';
        const abs = Math.abs(num);
        const sign = num < 0 ? '-' : '';
        if (abs >= 1e12) return sign + '$' + (abs / 1e12).toFixed(2) + 'T';
        if (abs >= 1e9) return sign + '$' + (abs / 1e9).toFixed(2) + 'B';
        if (abs >= 1e6) return sign + '$' + (abs / 1e6).toFixed(2) + 'M';
        if (abs >= 1e3) return sign + '$' + (abs / 1e3).toFixed(1) + 'K';
        return sign + '$' + abs.toFixed(2);
    },

    formatPercent(num) {
        if (num === null || num === undefined) return 'N/A';
        return num.toFixed(2) + '%';
    },

    formatRatio(num) {
        if (num === null || num === undefined) return 'N/A';
        return num.toFixed(2) + 'x';
    },

    getScoreColor(score) {
        if (score >= 80) return '#00e676';
        if (score >= 65) return '#69f0ae';
        if (score >= 50) return '#ffca28';
        if (score >= 35) return '#ff9800';
        return '#f44336';
    },

    /**
     * Render the Beginner Mode analysis view.
     */
    renderBeginnerView(data) {
        this.currentData = data;
        const { company, healthScore, metrics, redFlags, summary } = data.analysis;

        const circumference = 2 * Math.PI * 85;
        const offset = circumference - (healthScore.overall / 100) * circumference;
        const scoreColor = this.getScoreColor(healthScore.overall);

        let html = `
            <div class="stock-header animate-in">
                <div class="stock-info">
                    <div class="stock-ticker-badge">${company.ticker} · ${company.exchange || 'NASDAQ'}</div>
                    <h1 class="stock-name">${company.name}</h1>
                    <div class="stock-meta">
                        <span>Sector: ${company.sector}</span>
                        <span>Industry: ${company.industry}</span>
                        <span>Mkt Cap: ${this.formatCurrency(company.marketCap)}</span>
                    </div>
                </div>
                <div style="display:flex; gap:8px;">
                    <button class="btn btn-primary btn-sm" onclick="Watchlist.addFromAnalysis('${company.ticker}', '${company.name.replace(/'/g, "\\'")}')">Add to Watchlist</button>
                </div>
            </div>

            <!-- Health Score -->
            <div class="grid-2 animate-in animate-in-delay-1" style="margin-bottom:28px;">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Financial Health Score</div>
                        <span class="tag ${healthScore.overall >= 65 ? 'tag-success' : healthScore.overall >= 50 ? 'tag-warning' : 'tag-danger'}">${healthScore.label}</span>
                    </div>
                    <div class="health-score-container">
                        <div class="health-score-circle">
                            <svg viewBox="0 0 200 200">
                                <circle class="track" cx="100" cy="100" r="85"/>
                                <circle class="progress" cx="100" cy="100" r="85"
                                    stroke="${scoreColor}"
                                    stroke-dasharray="${circumference}"
                                    stroke-dashoffset="${offset}" />
                            </svg>
                            <div class="health-score-value">
                                <div class="health-score-number" style="color:${scoreColor}">${healthScore.overall}</div>
                                <div class="health-score-max">/100</div>
                            </div>
                        </div>
                        <div class="sub-scores">
                            ${this._renderSubScore('Growth', healthScore.growth)}
                            ${this._renderSubScore('Profitability', healthScore.profitability)}
                            ${this._renderSubScore('Fin. Health', healthScore.financialHealth)}
                            ${this._renderSubScore('Valuation', healthScore.valuation)}
                        </div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-title" style="margin-bottom:16px;">Health Score Breakdown</div>
                    <div class="chart-container" id="radarChart" style="height:300px;"></div>
                </div>
            </div>

            <!-- Summary -->
            <div class="card animate-in animate-in-delay-2" style="margin-bottom:28px;">
                <div class="card-title" style="margin-bottom:16px;">Plain-English Analysis</div>
                <div class="summary-box">${this._formatSummary(summary)}</div>
            </div>

            <!-- Red Flags -->
            ${redFlags.length > 0 ? `
            <div class="card animate-in animate-in-delay-3" style="margin-bottom:28px;">
                <div class="card-header">
                    <div class="card-title">Warning Signals (${redFlags.length})</div>
                </div>
                ${redFlags.map(flag => `
                    <div class="red-flag severity-${flag.severity}">
                        <div class="red-flag-icon">${flag.icon}</div>
                        <div>
                            <div class="red-flag-title">${flag.title}</div>
                            <div class="red-flag-description">${flag.description}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
            ` : ''}

            <!-- Key Metrics (simplified) -->
            <div class="card animate-in animate-in-delay-3" style="margin-bottom:28px;">
                <div class="card-title" style="margin-bottom:16px;">Key Metrics at a Glance</div>
                <div class="grid-4">
                    ${this._renderStatCard('Revenue', this.formatCurrency(metrics.totalRevenue), metrics.yoyRevenueGrowth, '%')}
                    ${this._renderStatCard('Net Income', this.formatCurrency(metrics.netIncome), metrics.yoyIncomeGrowth, '%')}
                    ${this._renderStatCard('Profit Margin', this.formatPercent(metrics.netMargin))}
                    ${this._renderStatCard('PE Ratio', metrics.peRatio ? metrics.peRatio.toFixed(1) + 'x' : 'N/A')}
                </div>
            </div>

            <!-- Revenue Chart -->
            <div class="card animate-in animate-in-delay-3">
                <div class="card-title" style="margin-bottom:16px;">Revenue & Earnings Trend</div>
                <div class="chart-container" id="revenueTrendChart" style="height:320px;"></div>
            </div>
        `;

        document.getElementById('pageContent').innerHTML = html;

        // Render charts after DOM is ready
        setTimeout(() => {
            Charts.createHealthRadarChart('radarChart', healthScore);
            Charts.createRevenueTrendChart('revenueTrendChart', data.analysis.historical);
        }, 100);
    },

    /**
     * Render the Advanced Mode analysis view.
     */
    renderAdvancedView(data) {
        this.currentData = data;
        const { company, healthScore, metrics, historical, redFlags, summary } = data.analysis;
        const scoreColor = this.getScoreColor(healthScore.overall);

        let html = `
            <div class="stock-header animate-in">
                <div class="stock-info">
                    <div class="stock-ticker-badge">${company.ticker} · ${company.exchange || 'NASDAQ'}</div>
                    <h1 class="stock-name">${company.name}</h1>
                    <div class="stock-meta">
                        <span>Sector: ${company.sector}</span>
                        <span>Industry: ${company.industry}</span>
                        <span>Mkt Cap: ${this.formatCurrency(company.marketCap)}</span>
                        <span>PE: ${metrics.peRatio ? metrics.peRatio.toFixed(1) : 'N/A'}</span>
                        <span>EPS: $${company.eps?.toFixed(2) || 'N/A'}</span>
                        <span>Beta: ${company.beta?.toFixed(2) || 'N/A'}</span>
                    </div>
                </div>
                <div style="display:flex; gap:8px; align-items:center;">
                    <div style="text-align:center; padding: 8px 20px; background: rgba(15, 23, 42, 0.6); border-radius:var(--radius-md); border: 1px solid var(--border-color);">
                        <div style="font-size:32px; font-weight:800; color:${scoreColor};">${healthScore.overall}</div>
                        <div style="font-size:11px; color:var(--text-muted); text-transform:uppercase;">${healthScore.label}</div>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="Watchlist.addFromAnalysis('${company.ticker}', '${company.name.replace(/'/g, "\\'")}')">Add to Watchlist</button>
                </div>
            </div>

            <!-- Section Tabs -->
            <div class="section-tabs" id="analysisTabs">
                <button class="section-tab active" data-tab="overview">Overview</button>
                <button class="section-tab" data-tab="profitability">Profitability</button>
                <button class="section-tab" data-tab="financials">Financial Health</button>
                <button class="section-tab" data-tab="valuation">Valuation</button>
                <button class="section-tab" data-tab="cashflow">Cash Flow</button>
            </div>

            <div id="analysisTabContent"></div>
        `;

        document.getElementById('pageContent').innerHTML = html;

        // Tab navigation
        document.querySelectorAll('#analysisTabs .section-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('#analysisTabs .section-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this._renderAdvancedTab(tab.dataset.tab, data);
            });
        });

        // Render default tab
        this._renderAdvancedTab('overview', data);
    },

    _renderAdvancedTab(tab, data) {
        const { metrics, historical, redFlags, healthScore } = data.analysis;
        const container = document.getElementById('analysisTabContent');

        switch (tab) {
            case 'overview':
                container.innerHTML = `
                    <div class="grid-2" style="margin-bottom:24px;">
                        <div class="card">
                            <div class="card-title" style="margin-bottom:12px;">Health Score Radar</div>
                            <div class="chart-container" id="advRadarChart" style="height:280px;"></div>
                        </div>
                        <div class="card">
                            <div class="card-title" style="margin-bottom:12px;">Revenue & Net Income</div>
                            <div class="chart-container" id="advRevenueChart" style="height:280px;"></div>
                        </div>
                    </div>
                    ${redFlags.length > 0 ? `
                    <div class="card" style="margin-bottom:24px;">
                        <div class="card-header">
                            <div class="card-title">Red Flags (${redFlags.length})</div>
                        </div>
                        ${redFlags.map(f => `
                            <div class="red-flag severity-${f.severity}">
                                <div class="red-flag-icon">${f.icon}</div>
                                <div>
                                    <div class="red-flag-title">${f.title}</div>
                                    <div class="red-flag-description">${f.description}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>` : ''}
                    <div class="card">
                        <div class="card-title" style="margin-bottom:16px;">All Financial Ratios</div>
                        <div class="grid-2">
                            <div>${this._renderMetricGroup('Profitability', [
                                ['Gross Margin', 'grossMargin', '%'], ['Operating Margin', 'operatingMargin', '%'],
                                ['Net Margin', 'netMargin', '%'], ['ROE', 'roe', '%'], ['ROA', 'roa', '%'], ['ROIC', 'roic', '%'],
                            ], metrics)}</div>
                            <div>${this._renderMetricGroup('Growth', [
                                ['Revenue CAGR', 'revenueCagr', '%'], ['YoY Revenue', 'yoyRevenueGrowth', '%'],
                                ['YoY Net Income', 'yoyIncomeGrowth', '%'],
                            ], metrics)}
                            ${this._renderMetricGroup('Valuation', [
                                ['PE Ratio', 'peRatio', 'x'], ['PB Ratio', 'pbRatio', 'x'],
                                ['PS Ratio', 'psRatio', 'x'], ['EV/EBITDA', 'evEbitda', 'x'], ['FCF Yield', 'fcfYield', '%'],
                            ], metrics)}</div>
                        </div>
                    </div>
                `;
                setTimeout(() => {
                    Charts.createHealthRadarChart('advRadarChart', healthScore);
                    Charts.createRevenueTrendChart('advRevenueChart', historical);
                }, 100);
                break;

            case 'profitability':
                container.innerHTML = `
                    <div class="card" style="margin-bottom:24px;">
                        <div class="card-title" style="margin-bottom:12px;">Margin Trends</div>
                        <div class="chart-container" id="marginsChart" style="height:320px;"></div>
                    </div>
                    <div class="card">
                        <div class="card-title" style="margin-bottom:16px;">Profitability Metrics</div>
                        ${this._renderMetricTable([
                            ['Gross Margin', 'grossMargin', '%', '> 40% is strong'],
                            ['Operating Margin', 'operatingMargin', '%', '> 20% is excellent'],
                            ['Net Margin', 'netMargin', '%', '> 15% is highly profitable'],
                            ['Return on Equity', 'roe', '%', '> 15% indicates competitive moat'],
                            ['Return on Assets', 'roa', '%', '> 10% is strong'],
                            ['Return on Invested Capital', 'roic', '%', '> 15% creates shareholder value'],
                        ], metrics)}
                    </div>
                `;
                setTimeout(() => Charts.createMarginsChart('marginsChart', historical), 100);
                break;

            case 'financials':
                container.innerHTML = `
                    <div class="card" style="margin-bottom:24px;">
                        <div class="card-title" style="margin-bottom:12px;">Debt vs. Equity</div>
                        <div class="chart-container" id="debtChart" style="height:320px;"></div>
                    </div>
                    <div class="card">
                        <div class="card-title" style="margin-bottom:16px;">Financial Health Metrics</div>
                        ${this._renderMetricTable([
                            ['Current Ratio', 'currentRatio', 'x', '> 1.5 indicates good liquidity'],
                            ['Quick Ratio', 'quickRatio', 'x', '> 1 is adequate'],
                            ['Debt-to-Equity', 'deRatio', 'x', '< 0.5 is conservative'],
                            ['Interest Coverage', 'interestCoverage', 'x', '> 5 is very safe'],
                            ['Asset Turnover', 'assetTurnover', 'x', 'Higher is more efficient'],
                        ], metrics)}
                    </div>
                `;
                setTimeout(() => Charts.createDebtEquityChart('debtChart', historical), 100);
                break;

            case 'valuation':
                container.innerHTML = `
                    <div class="card">
                        <div class="card-title" style="margin-bottom:16px;">Valuation Metrics</div>
                        ${this._renderMetricTable([
                            ['PE Ratio', 'peRatio', 'x', '< 20 may be undervalued'],
                            ['PB Ratio', 'pbRatio', 'x', '< 3 is reasonable'],
                            ['PS Ratio', 'psRatio', 'x', '< 3 suggests value'],
                            ['EV/EBITDA', 'evEbitda', 'x', '< 12 indicates value'],
                            ['FCF Yield', 'fcfYield', '%', '> 5% is attractive'],
                            ['Dividend Yield', 'dividendYield', '%', 'Income for investors'],
                        ], metrics, data.analysis.company)}
                    </div>
                `;
                break;

            case 'cashflow':
                container.innerHTML = `
                    <div class="card" style="margin-bottom:24px;">
                        <div class="card-title" style="margin-bottom:12px;">Cash Flow Trends</div>
                        <div class="chart-container" id="cashflowChart" style="height:320px;"></div>
                    </div>
                    <div class="card">
                        <div class="card-title" style="margin-bottom:16px;">Cash Flow Metrics</div>
                        ${this._renderMetricTable([
                            ['Operating CF Margin', 'operatingCashflowMargin', '%', '> 15% is strong'],
                            ['Free Cash Flow', 'fcf', '$', 'Positive is essential'],
                            ['FCF/Revenue', 'fcfToRevenue', '%', '> 10% is excellent'],
                            ['Operating Cash Flow', 'operatingCashflow', '$', 'Higher is better'],
                        ], metrics)}
                    </div>
                `;
                setTimeout(() => Charts.createCashFlowChart('cashflowChart', historical), 100);
                break;
        }
    },

    // ---- Helper rendering functions ----

    _renderSubScore(label, score) {
        const color = this.getScoreColor(score);
        return `
            <div class="sub-score">
                <div class="sub-score-value" style="color:${color}">${score}</div>
                <div class="sub-score-label">${label}</div>
                <div class="sub-score-bar"><div class="sub-score-bar-fill" style="width:${score}%; background:${color};"></div></div>
            </div>
        `;
    },

    _renderStatCard(label, value, change, changeSuffix) {
        let changeHtml = '';
        if (change !== undefined && change !== null) {
            const isPositive = change >= 0;
            changeHtml = `<div class="stat-change ${isPositive ? 'positive' : 'negative'}">${isPositive ? '↑' : '↓'} ${Math.abs(change).toFixed(1)}${changeSuffix || ''} YoY</div>`;
        }
        return `
            <div class="card stat-card">
                <div class="stat-label">${label}</div>
                <div class="stat-value">${value}</div>
                ${changeHtml}
            </div>
        `;
    },

    _renderMetricGroup(title, metricsArr, values) {
        let rows = metricsArr.map(([name, key, suffix]) => {
            const val = values[key];
            let formatted = val !== undefined ? val.toFixed(2) + (suffix || '') : 'N/A';
            const tooltipKey = key;
            return `
                <div class="metric-row">
                    <div class="metric-name">
                        ${name}
                        <span class="metric-tooltip-trigger" onclick="Analysis.showTooltip(event, '${tooltipKey}')">?</span>
                    </div>
                    <div class="metric-value">${formatted}</div>
                </div>
            `;
        }).join('');

        return `
            <div style="margin-bottom:20px;">
                <div style="font-size:13px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px;">${title}</div>
                ${rows}
            </div>
        `;
    },

    _renderMetricTable(metricsArr, values, company) {
        return `
            <table class="financial-table">
                <thead>
                    <tr><th>Metric</th><th style="text-align:right;">Value</th><th>Benchmark</th></tr>
                </thead>
                <tbody>
                    ${metricsArr.map(([name, key, suffix, note]) => {
                        let val = values[key];
                        if (key === 'dividendYield' && company) val = company.dividendYield;
                        let formatted;
                        if (val === undefined || val === null) {
                            formatted = 'N/A';
                        } else if (suffix === '$') {
                            formatted = this.formatCurrency(val);
                        } else {
                            formatted = val.toFixed(2) + (suffix || '');
                        }
                        return `
                            <tr>
                                <td>
                                    ${name}
                                    <span class="metric-tooltip-trigger" onclick="Analysis.showTooltip(event, '${key}')" style="margin-left:6px;">?</span>
                                </td>
                                <td class="number">${formatted}</td>
                                <td style="font-size:12px; color:var(--text-muted);">${note}</td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
    },

    _formatSummary(summary) {
        if (!summary) return '';
        return summary
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>');
    },

    showTooltip(event, key) {
        const tooltip = document.getElementById('tooltipContainer');
        const data = this.tooltips ? this.tooltips[key] : null;

        if (!data) {
            tooltip.style.display = 'none';
            return;
        }

        const mode = App.currentMode;
        const description = mode === 'beginner' ? data.simple : data.detailed;

        tooltip.innerHTML = `
            <div class="tooltip-title">${data.name}</div>
            <div class="tooltip-body">${description}</div>
            <div class="tooltip-ranges">
                <span class="tooltip-range good">Good: ${data.good}</span>
                <span class="tooltip-range average">Avg: ${data.average}</span>
                <span class="tooltip-range bad">Bad: ${data.bad}</span>
            </div>
        `;

        // Position tooltip
        const rect = event.target.getBoundingClientRect();
        let left = rect.right + 10;
        let top = rect.top - 10;

        if (left + 340 > window.innerWidth) {
            left = rect.left - 350;
        }
        if (top + 200 > window.innerHeight) {
            top = window.innerHeight - 210;
        }

        tooltip.style.left = left + 'px';
        tooltip.style.top = top + 'px';
        tooltip.style.display = 'block';

        // Hide on click outside
        const hide = (e) => {
            if (!tooltip.contains(e.target) && e.target !== event.target) {
                tooltip.style.display = 'none';
                document.removeEventListener('click', hide);
            }
        };
        setTimeout(() => document.addEventListener('click', hide), 10);
    },
};

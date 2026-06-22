/**
 * Charts Module — Chart.js powered visualizations.
 * Creates interactive, responsive charts for financial data.
 */
const Charts = {
    instances: {},
    defaultColors: {
        primary: '#38bdf8',
        secondary: '#818cf8',
        tertiary: '#a78bfa',
        success: '#34d399',
        warning: '#fbbf24',
        danger: '#f87171',
        orange: '#fb923c',
        pink: '#f472b6',
    },

    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { intersect: false, mode: 'index' },
        plugins: {
            legend: {
                labels: { color: '#94a3b8', font: { family: 'Inter', size: 12 }, usePointStyle: true, pointStyle: 'circle', padding: 16 }
            },
            tooltip: {
                backgroundColor: 'rgba(17, 24, 39, 0.95)',
                titleColor: '#f1f5f9',
                bodyColor: '#94a3b8',
                borderColor: 'rgba(75, 85, 99, 0.4)',
                borderWidth: 1,
                cornerRadius: 8,
                padding: 12,
                titleFont: { family: 'Inter', weight: '600', size: 13 },
                bodyFont: { family: 'Inter', size: 12 },
                displayColors: true,
                boxPadding: 4,
            }
        },
        scales: {
            x: {
                grid: { color: 'rgba(75, 85, 99, 0.15)', drawBorder: false },
                ticks: { color: '#64748b', font: { family: 'Inter', size: 11 } },
                border: { display: false }
            },
            y: {
                grid: { color: 'rgba(75, 85, 99, 0.15)', drawBorder: false },
                ticks: { color: '#64748b', font: { family: 'Inter', size: 11 } },
                border: { display: false }
            }
        }
    },

    /**
     * Destroy an existing chart instance before creating a new one.
     */
    destroy(id) {
        if (this.instances[id]) {
            this.instances[id].destroy();
            delete this.instances[id];
        }
    },

    /**
     * Get or create a canvas element inside a container.
     */
    getCanvas(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return null;
        container.innerHTML = '<canvas></canvas>';
        const canvas = container.querySelector('canvas');
        canvas.style.maxHeight = '350px';
        return canvas;
    },

    /**
     * Format large numbers (e.g., 1,000,000 -> 1M)
     */
    formatNumber(num) {
        if (num === null || num === undefined) return 'N/A';
        const abs = Math.abs(num);
        if (abs >= 1e12) return (num / 1e12).toFixed(1) + 'T';
        if (abs >= 1e9) return (num / 1e9).toFixed(1) + 'B';
        if (abs >= 1e6) return (num / 1e6).toFixed(1) + 'M';
        if (abs >= 1e3) return (num / 1e3).toFixed(1) + 'K';
        return num.toFixed(1);
    },

    // ============================================================
    // CHART TYPES
    // ============================================================

    /**
     * Revenue & Net Income Multi-Year Trend
     */
    createRevenueTrendChart(containerId, historical) {
        const canvas = this.getCanvas(containerId);
        if (!canvas) return;
        this.destroy(containerId);

        const ctx = canvas.getContext('2d');

        // Create gradients
        const revenueGradient = ctx.createLinearGradient(0, 0, 0, 350);
        revenueGradient.addColorStop(0, 'rgba(56, 189, 248, 0.3)');
        revenueGradient.addColorStop(1, 'rgba(56, 189, 248, 0.02)');

        const incomeGradient = ctx.createLinearGradient(0, 0, 0, 350);
        incomeGradient.addColorStop(0, 'rgba(52, 211, 153, 0.3)');
        incomeGradient.addColorStop(1, 'rgba(52, 211, 153, 0.02)');

        this.instances[containerId] = new Chart(canvas, {
            type: 'line',
            data: {
                labels: historical.years,
                datasets: [
                    {
                        label: 'Revenue',
                        data: historical.revenue,
                        borderColor: this.defaultColors.primary,
                        backgroundColor: revenueGradient,
                        fill: true,
                        tension: 0.4,
                        borderWidth: 2.5,
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        pointBackgroundColor: this.defaultColors.primary,
                        pointBorderColor: '#0a0e1a',
                        pointBorderWidth: 2,
                    },
                    {
                        label: 'Net Income',
                        data: historical.netIncome,
                        borderColor: this.defaultColors.success,
                        backgroundColor: incomeGradient,
                        fill: true,
                        tension: 0.4,
                        borderWidth: 2.5,
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        pointBackgroundColor: this.defaultColors.success,
                        pointBorderColor: '#0a0e1a',
                        pointBorderWidth: 2,
                    }
                ]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: (ctx) => `${ctx.dataset.label}: $${this.formatNumber(ctx.raw)}`
                        }
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            callback: (val) => '$' + this.formatNumber(val)
                        }
                    }
                }
            }
        });
    },

    /**
     * Profitability Margins Trend
     */
    createMarginsChart(containerId, historical) {
        const canvas = this.getCanvas(containerId);
        if (!canvas) return;
        this.destroy(containerId);

        this.instances[containerId] = new Chart(canvas, {
            type: 'line',
            data: {
                labels: historical.years,
                datasets: [
                    {
                        label: 'Gross Margin',
                        data: historical.grossMargin,
                        borderColor: this.defaultColors.primary,
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        fill: false,
                        tension: 0.4,
                        borderWidth: 2.5,
                        pointRadius: 4,
                        pointBackgroundColor: this.defaultColors.primary,
                    },
                    {
                        label: 'Operating Margin',
                        data: historical.operatingMargin,
                        borderColor: this.defaultColors.secondary,
                        fill: false,
                        tension: 0.4,
                        borderWidth: 2.5,
                        pointRadius: 4,
                        pointBackgroundColor: this.defaultColors.secondary,
                    },
                    {
                        label: 'Net Margin',
                        data: historical.netMargin,
                        borderColor: this.defaultColors.success,
                        fill: false,
                        tension: 0.4,
                        borderWidth: 2.5,
                        pointRadius: 4,
                        pointBackgroundColor: this.defaultColors.success,
                    }
                ]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: { label: (ctx) => `${ctx.dataset.label}: ${ctx.raw.toFixed(1)}%` }
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            callback: (val) => val + '%'
                        }
                    }
                }
            }
        });
    },

    /**
     * Health Score Radar Chart
     */
    createHealthRadarChart(containerId, healthScore) {
        const canvas = this.getCanvas(containerId);
        if (!canvas) return;
        this.destroy(containerId);

        this.instances[containerId] = new Chart(canvas, {
            type: 'radar',
            data: {
                labels: ['Growth', 'Profitability', 'Financial Health', 'Valuation'],
                datasets: [{
                    label: 'Score',
                    data: [
                        healthScore.growth,
                        healthScore.profitability,
                        healthScore.financialHealth,
                        healthScore.valuation
                    ],
                    borderColor: this.defaultColors.primary,
                    backgroundColor: 'rgba(56, 189, 248, 0.15)',
                    borderWidth: 2.5,
                    pointRadius: 5,
                    pointBackgroundColor: this.defaultColors.primary,
                    pointBorderColor: '#0a0e1a',
                    pointBorderWidth: 2,
                    pointHoverRadius: 7,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: { label: (ctx) => `${ctx.label}: ${ctx.raw}/100` }
                    }
                },
                scales: {
                    r: {
                        min: 0,
                        max: 100,
                        ticks: {
                            stepSize: 25,
                            color: '#64748b',
                            backdropColor: 'transparent',
                            font: { family: 'Inter', size: 10 }
                        },
                        grid: { color: 'rgba(75, 85, 99, 0.2)' },
                        pointLabels: {
                            color: '#94a3b8',
                            font: { family: 'Inter', size: 12, weight: '600' }
                        },
                        angleLines: { color: 'rgba(75, 85, 99, 0.2)' }
                    }
                }
            }
        });
    },

    /**
     * Cash Flow Trend Chart
     */
    createCashFlowChart(containerId, historical) {
        const canvas = this.getCanvas(containerId);
        if (!canvas) return;
        this.destroy(containerId);

        this.instances[containerId] = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: historical.years,
                datasets: [
                    {
                        label: 'Operating Cash Flow',
                        data: historical.operatingCashflow,
                        backgroundColor: 'rgba(56, 189, 248, 0.7)',
                        borderRadius: 6,
                        borderSkipped: false,
                    },
                    {
                        label: 'Free Cash Flow',
                        data: historical.fcf,
                        backgroundColor: 'rgba(52, 211, 153, 0.7)',
                        borderRadius: 6,
                        borderSkipped: false,
                    }
                ]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: { label: (ctx) => `${ctx.dataset.label}: $${this.formatNumber(ctx.raw)}` }
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            callback: (val) => '$' + this.formatNumber(val)
                        }
                    }
                }
            }
        });
    },

    /**
     * Debt vs Equity Chart
     */
    createDebtEquityChart(containerId, historical) {
        const canvas = this.getCanvas(containerId);
        if (!canvas) return;
        this.destroy(containerId);

        this.instances[containerId] = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: historical.years,
                datasets: [
                    {
                        label: 'Total Debt',
                        data: historical.totalDebt,
                        backgroundColor: 'rgba(248, 113, 113, 0.7)',
                        borderRadius: 6,
                        borderSkipped: false,
                    },
                    {
                        label: 'Total Equity',
                        data: historical.totalEquity,
                        backgroundColor: 'rgba(56, 189, 248, 0.7)',
                        borderRadius: 6,
                        borderSkipped: false,
                    }
                ]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: { label: (ctx) => `${ctx.dataset.label}: $${this.formatNumber(ctx.raw)}` }
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            callback: (val) => '$' + this.formatNumber(val)
                        }
                    }
                }
            }
        });
    },

    /**
     * Sector Comparison Grouped Bar Chart
     */
    createComparisonChart(containerId, comparisonData, metricKey, metricLabel, suffix = '') {
        const canvas = this.getCanvas(containerId);
        if (!canvas) return;
        this.destroy(containerId);

        const colors = [
            this.defaultColors.primary,
            this.defaultColors.secondary,
            this.defaultColors.success,
            this.defaultColors.warning,
            this.defaultColors.pink,
        ];

        const datasets = comparisonData.map((item, i) => ({
            label: item.ticker,
            data: [item.value],
            backgroundColor: colors[i % colors.length] + 'cc',
            borderRadius: 8,
            borderSkipped: false,
            barPercentage: 0.7,
        }));

        this.instances[containerId] = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: [metricLabel],
                datasets,
            },
            options: {
                ...this.defaultOptions,
                indexAxis: 'y',
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: (ctx) => `${ctx.dataset.label}: ${ctx.raw.toFixed(2)}${suffix}`
                        }
                    }
                },
                scales: {
                    x: {
                        ...this.defaultOptions.scales.x,
                        ticks: {
                            ...this.defaultOptions.scales.x.ticks,
                            callback: (val) => val + suffix
                        }
                    },
                    y: { display: false }
                }
            }
        });
    },

    /**
     * Multi-metric comparison chart (grouped bars).
     */
    createMultiComparisonChart(containerId, comparisons, metrics) {
        const canvas = this.getCanvas(containerId);
        if (!canvas) return;
        this.destroy(containerId);

        const colors = [
            this.defaultColors.primary,
            this.defaultColors.secondary,
            this.defaultColors.success,
            this.defaultColors.warning,
            this.defaultColors.pink,
        ];

        const metricLabels = metrics.map(m => m.label);
        const datasets = comparisons.map((comp, i) => ({
            label: comp.ticker,
            data: metrics.map(m => {
                const val = comp.analysis?.metrics?.[m.key];
                return val !== undefined ? val : 0;
            }),
            backgroundColor: colors[i % colors.length] + 'cc',
            borderRadius: 6,
            borderSkipped: false,
        }));

        this.instances[containerId] = new Chart(canvas, {
            type: 'bar',
            data: { labels: metricLabels, datasets },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: (ctx) => {
                                const m = metrics[ctx.dataIndex];
                                return `${ctx.dataset.label}: ${ctx.raw.toFixed(2)}${m.suffix || ''}`;
                            }
                        }
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        beginAtZero: true,
                    }
                }
            }
        });
    },

    /**
     * Health Score Comparison Bar Chart
     */
    createHealthComparisonChart(containerId, comparisons) {
        const canvas = this.getCanvas(containerId);
        if (!canvas) return;
        this.destroy(containerId);

        const labels = comparisons.map(c => c.ticker);
        const scores = comparisons.map(c => c.analysis?.healthScore?.overall || 0);
        const bgColors = scores.map(s => {
            if (s >= 80) return 'rgba(52, 211, 153, 0.7)';
            if (s >= 65) return 'rgba(105, 240, 174, 0.7)';
            if (s >= 50) return 'rgba(255, 202, 40, 0.7)';
            if (s >= 35) return 'rgba(255, 152, 0, 0.7)';
            return 'rgba(244, 67, 54, 0.7)';
        });

        this.instances[containerId] = new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Health Score',
                    data: scores,
                    backgroundColor: bgColors,
                    borderRadius: 8,
                    borderSkipped: false,
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: { display: false },
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: { label: (ctx) => `Health Score: ${ctx.raw}/100` }
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        max: 100,
                        beginAtZero: true,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            callback: (val) => val + '/100'
                        }
                    }
                }
            }
        });
    },
};

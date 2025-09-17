/*
 * Kconvert - Chart Visualization Module
 * Real-time line chart visualization for currency exchange rates
 * 
 * Copyright (c) 2025 Team 6
 * All rights reserved.
 */

import {
    Chart,
    LineController,
    LineElement,
    PointElement,
    LinearScale,
    CategoryScale,
    Tooltip,
    Filler,
    Legend
} from 'chart.js';

// Register only what we need for a lighter bundle
Chart.register(
    LineController,
    LineElement,
    PointElement,
    LinearScale,
    CategoryScale,
    Tooltip,
    Filler,
    Legend
);

// Golden vertical crosshair plugin for elegant precision reading
const crosshairLinePlugin = {
    id: 'crosshairLine',
    afterDatasetsDraw(chart, args, opts) {
        const tooltip = chart.tooltip;
        if (!tooltip || !tooltip.getActiveElements || !tooltip.getActiveElements().length) return;
        const x = tooltip.caretX;
        const { top, bottom } = chart.chartArea;
        const ctx = chart.ctx;
        ctx.save();
        ctx.strokeStyle = (opts && opts.color) || '#f1c40f';
        ctx.lineWidth = (opts && opts.lineWidth) || 1;
        ctx.setLineDash((opts && opts.dash) || [4, 4]);
        ctx.beginPath();
        ctx.moveTo(x, top);
        ctx.lineTo(x, bottom);
        ctx.stroke();

        // Draw a small golden live dot at the active point for clarity
        const active = tooltip.getActiveElements()[0];
        if (active) {
            const meta = chart.getDatasetMeta(active.datasetIndex);
            const el = meta && meta.data && meta.data[active.index];
            if (el) {
                const px = el.x;
                const py = el.y;
                ctx.fillStyle = '#f1c40f';
                ctx.strokeStyle = '#ffffff';
                ctx.setLineDash([]);
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.arc(px, py, 4, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();
            }
        }
        ctx.restore();
    }
};

Chart.register(crosshairLinePlugin);

// Chart configuration and data management
class ExchangeRateChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.chart = null;
        this.currentRange = '12H';
        this.currentPair = { from: null, to: null };
        this.chartType = 'area'; // Default chart type: 'area', 'bar', 'line'
        
        // Chart data storage - starts empty
        this.chartData = {
            '12H': { labels: [], data: [], changeData: [] },
            '1D': { labels: [], data: [], changeData: [] },
            '1W': { labels: [], data: [], changeData: [] },
            '1M': { labels: [], data: [], changeData: [] },
            '1Y': { labels: [], data: [], changeData: [] },
            '2Y': { labels: [], data: [], changeData: [] },
            '5Y': { labels: [], data: [], changeData: [] },
            '10Y': { labels: [], data: [], changeData: [] }
        };
        
        this.initializeChart();
        this.setupEventListeners();
    }
    
    initializeChart() {
        const data = this.chartData[this.currentRange];
        
        // Create gradient for area fill
        const gradient = this.ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(241, 196, 15, 0.4)');
        gradient.addColorStop(0.5, 'rgba(241, 196, 15, 0.2)');
        gradient.addColorStop(1, 'rgba(241, 196, 15, 0.05)');
        
        // Create gradient for bar chart (positive/negative changes)
        const positiveGradient = this.ctx.createLinearGradient(0, 0, 0, 400);
        positiveGradient.addColorStop(0, 'rgba(34, 197, 94, 0.8)');
        positiveGradient.addColorStop(1, 'rgba(34, 197, 94, 0.3)');
        
        const negativeGradient = this.ctx.createLinearGradient(0, 0, 0, 400);
        negativeGradient.addColorStop(0, 'rgba(239, 68, 68, 0.8)');
        negativeGradient.addColorStop(1, 'rgba(239, 68, 68, 0.3)');
        
        const chartConfig = this.getChartConfig(data, gradient, positiveGradient, negativeGradient);
        this.chart = new Chart(this.ctx, chartConfig);
    }
    
    getChartConfig(data, gradient, positiveGradient, negativeGradient) {
        if (this.chartType === 'bar') {
            return this.getBarChartConfig(data, positiveGradient, negativeGradient);
        } else if (this.chartType === 'line') {
            return this.getLineChartConfig(data);
        } else {
            return this.getAreaChartConfig(data, gradient);
        }
    }
    
    getAreaChartConfig(data, gradient) {
        return {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: this.currentPair.from && this.currentPair.to ? `${this.currentPair.from} to ${this.currentPair.to}` : 'Exchange Rate',
                    data: data.data,
                    borderColor: '#f1c40f',
                    backgroundColor: gradient,
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#f1c40f',
                    pointRadius: 0,
                    pointHoverRadius: 7,
                    pointHoverBorderWidth: 3,
                    pointHoverBorderColor: '#ffffff',
                    pointHoverBackgroundColor: '#f1c40f'
                }]
            },
            options: this.getCommonOptions()
        };
    }
    
    getLineChartConfig(data) {
        return {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: this.currentPair.from && this.currentPair.to ? `${this.currentPair.from} to ${this.currentPair.to}` : 'Exchange Rate',
                    data: data.data,
                    borderColor: '#f1c40f',
                    backgroundColor: 'transparent',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointBackgroundColor: '#f1c40f',
                    pointRadius: 2,
                    pointHoverRadius: 8,
                    pointHoverBorderWidth: 3,
                    pointHoverBorderColor: '#ffffff',
                    pointHoverBackgroundColor: '#f1c40f'
                }]
            },
            options: this.getCommonOptions()
        };
    }
    
    getBarChartConfig(data, positiveGradient, negativeGradient) {
        const changeData = data.changeData || [];
        const backgroundColors = changeData.map(value => 
            value >= 0 ? positiveGradient : negativeGradient
        );
        const borderColors = changeData.map(value => 
            value >= 0 ? '#22c55e' : '#ef4444'
        );
        
        return {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Daily Change (%)',
                    data: changeData,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1.5,
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                ...this.getCommonOptions(),
                scales: {
                    ...this.getCommonOptions().scales,
                    y: {
                        ...this.getCommonOptions().scales.y,
                        title: {
                            display: false,
                            text: 'Change (%)',
                            color: '#94a3b8',
                            font: {
                                family: 'Inter',
                                size: 12,
                                weight: '500'
                            }
                        },
                        ticks: {
                            ...this.getCommonOptions().scales.y.ticks,
                            callback: function(value) {
                                return value.toFixed(2) + '%';
                            }
                        }
                    }
                }
            }
        };
    }
    
    getCommonOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            animation: {
                duration: 1200,
                easing: 'easeInOutCubic'
            },
            transitions: {
                active: {
                    animation: {
                        duration: 400,
                        easing: 'easeOutCubic'
                    }
                }
            },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false, // hidden by default when no data
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        titleColor: '#f1f5f9',
                        bodyColor: '#cbd5e1',
                        borderColor: '#f1c40f',
                        borderWidth: 1,
                        cornerRadius: 12,
                        displayColors: false,
                        padding: 12,
                        titleFont: {
                            family: 'Inter',
                            size: 13,
                            weight: '600'
                        },
                        bodyFont: {
                            family: 'Inter',
                            size: 12,
                            weight: '500'
                        },
                        callbacks: {
                            title: function(context) {
                                return `Time: ${context[0].label}`;
                            },
                            label: function(context) {
                                const value = context.parsed.y;
                                // Format with proper number formatting
                                const formatted = new Intl.NumberFormat('en-US', {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 6,
                                    useGrouping: true
                                }).format(value);
                                return `Rate: ${formatted}`;
                            }
                        }
                    },
                    crosshairLine: {
                        color: '#f1c40f',
                        lineWidth: 1.5,
                        dash: [6, 4]
                    }
                },
                layout: {
                    padding: {
                        top: 10,
                        right: 5,
                        bottom: 10,
                        left: 5
                    }
                },
                elements: {
                    line: {
                        borderCapStyle: 'round',
                        borderJoinStyle: 'round'
                    },
                    point: {
                        pointStyle: 'circle',
                        radius: 4,
                        hitRadius: 6,
                        hoverRadius: 6
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            // hidden by default when no data
                            display: false,
                            text: 'Time',
                            color: '#94a3b8',
                            font: {
                                family: 'Inter',
                                size: 12,
                                weight: '500'
                            }
                        },
                        grid: {
                            color: 'rgba(148, 163, 184, 0.08)',
                            drawBorder: false,
                            // hidden by default when no data
                            display: false
                        },
                        ticks: {
                            font: {
                                family: 'Inter',
                                size: 11
                            },
                            // hidden by default when no data
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            // hidden by default when no data
                            display: false,
                            text: this.currentPair.to ? `Value (${this.currentPair.to})` : 'Value',
                            color: '#94a3b8',
                            font: {
                                family: 'Inter',
                                size: 12,
                                weight: '500'
                            }
                        },
                        grid: {
                            color: 'rgba(148, 163, 184, 0.08)',
                            drawBorder: false,
                            // hidden by default when no data
                            display: false
                        },
                        ticks: {
                            color: '#94a3b8',
                            font: {
                                family: 'Inter',
                                size: 11
                            },
                            // hidden by default when no data
                            display: false,
                            callback: function(value) {
                                // Format Y-axis with proper number formatting
                                return new Intl.NumberFormat('en-US', {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 3,
                                    useGrouping: true
                                }).format(value);
                            }
                        }
                    }
                },
                animation: {
                    duration: 700,
                    easing: 'easeOutCubic'
                },
                // Per-property animations for a gentle spring-like effect
                animations: {
                    y: {
                        duration: 800,
                        easing: 'easeOutBack'
                    },
                    x: {
                        duration: 600,
                        easing: 'easeOutCubic'
                    }
                },
                // Slight emphasis when dataset becomes active (hover/tooltip)
                transitions: {
                    active: {
                        animation: { duration: 200 },
                        borderWidth: 4
                    }
                }
            }
        });
    }
    
    setupEventListeners() {
        // Time range button listeners
        const timeRangeBtns = document.querySelectorAll('.time-range-btn');
        timeRangeBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Remove active class from all buttons
                timeRangeBtns.forEach(b => b.classList.remove('active'));
                // Add active class to clicked button
                e.target.classList.add('active');
                
                // Update chart data
                this.currentRange = e.target.dataset.range;
                this.updateChart();
            });
        });
        
        // Chart type button listeners
        const chartTypeBtns = document.querySelectorAll('.chart-type-btn');
        chartTypeBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Remove active class from all buttons
                chartTypeBtns.forEach(b => b.classList.remove('active'));
                // Add active class to clicked button
                e.target.classList.add('active');
                
                // Update chart type
                this.chartType = e.target.dataset.type;
                this.recreateChart();
            });
        });
    }
    
    recreateChart() {
        if (this.chart) {
            this.chart.destroy();
        }
        this.initializeChart();
        this.updateChart();
    }
    
    switchChartType(type) {
        this.chartType = type;
        this.recreateChart();
    }
    
    calculateChangeData(data) {
        if (!data || data.length < 2) return [];
        
        const changes = [];
        for (let i = 1; i < data.length; i++) {
            const previous = data[i - 1];
            const current = data[i];
            if (previous && current && previous !== 0) {
                const change = ((current - previous) / previous) * 100;
                changes.push(change);
            } else {
                changes.push(0);
            }
        }
        // Add 0 for the first data point since there's no previous value
        return [0, ...changes];
    }
    
    updateChart() {
        const data = this.chartData[this.currentRange];
        
        // Update chart data with animation
        this.chart.data.labels = data.labels;
        this.chart.data.datasets[0].data = data.data;
        this.chart.data.datasets[0].label = `${this.currentPair.from} to ${this.currentPair.to}`;
        
        // Update titles and toggle axes visibility depending on data
        const hasData = (data.labels && data.labels.length > 0) && (data.data && data.data.length > 0);
        
        // Axis titles
        this.chart.options.scales.y.title.text = `Value (${this.currentPair.to})`;
        this.chart.options.scales.x.title.display = hasData;
        this.chart.options.scales.y.title.display = hasData;
        
        // Grid and ticks visibility
        this.chart.options.scales.x.grid.display = hasData;
        this.chart.options.scales.y.grid.display = hasData;
        this.chart.options.scales.x.ticks.display = hasData;
        this.chart.options.scales.y.ticks.display = hasData;
        
        // Tooltip visibility
        this.chart.options.plugins.tooltip.enabled = hasData;
        
        // Compose indicator line: 1 FROM -> TO BASE_RATE LIVE_RATE
        const fromDisplay = document.querySelector('.chart-from');
        const toDisplay = document.querySelector('.chart-to');
        const currentRateElement = document.querySelector('.chart-current-rate');
        if (fromDisplay && toDisplay) {
            const last = (data.data && data.data.length > 0) ? data.data[data.data.length - 1] : null;
            const baseText = (typeof this.baseRate === 'number' && !isNaN(this.baseRate)) ? this.baseRate.toFixed(6) : '';
            const liveText = (last !== null) ? ` ${last.toFixed(6)}` : '';
            // Ensure left shows '1 FROM' (arrow icon is provided by HTML)
            fromDisplay.textContent = `1 ${this.currentPair.from}`;
            // Right shows 'TO BASE_RATE LIVE_RATE'
            toDisplay.textContent = `${this.currentPair.to} ${baseText}${liveText}`.trim();
        }
        // Clear separate current-rate element to avoid duplicate numbers
        if (currentRateElement) currentRateElement.textContent = '';
        
        this.chart.update('active');
    }
    
    updateCurrencyPair(fromCurrency, toCurrency) {
        this.currentPair = { from: fromCurrency, to: toCurrency };
        
        // Update currency pair display with input amount if available
        const fromDisplay = document.querySelector('.chart-from');
        const toDisplay = document.querySelector('.chart-to');
        
        if (fromDisplay) {
            // Always show base indicator as 1 for precision; arrow icon comes from HTML
            const displayAmount = 1;
            fromDisplay.textContent = `${displayAmount} ${fromCurrency}`;
        }
        if (toDisplay) {
            // If we have a base rate from last conversion, include it; else show currency only
            if (typeof this.baseRate === 'number' && !isNaN(this.baseRate)) {
                toDisplay.textContent = `${toCurrency} ${this.baseRate.toFixed(6)}`;
            } else {
                toDisplay.textContent = toCurrency;
            }
        }
        
        // Update chart
        this.updateChart();
    }
    
    // Generate realistic historical data based on current rate
    generateHistoricalData(currentRate, timeRange) {
        const dataPoints = {
            '12H': { count: 12, interval: 'hour', label: (i) => `${23-i}:00` },
            '1D': { count: 24, interval: 'hour', label: (i) => `${23-i}:00` },
            '1W': { count: 7, interval: 'day', label: (i) => {
                const date = new Date();
                date.setDate(date.getDate() - (6-i));
                return date.toLocaleDateString('en-US', { weekday: 'short' });
            }},
            '1M': { count: 30, interval: 'day', label: (i) => {
                const date = new Date();
                date.setDate(date.getDate() - (29-i));
                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }},
            '1Y': { count: 12, interval: 'month', label: (i) => {
                const date = new Date();
                date.setMonth(date.getMonth() - (11-i));
                return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
            }},
            '2Y': { count: 24, interval: 'month', label: (i) => {
                const date = new Date();
                date.setMonth(date.getMonth() - (23-i));
                return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
            }},
            '5Y': { count: 60, interval: 'month', label: (i) => {
                const date = new Date();
                date.setMonth(date.getMonth() - (59-i));
                return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
            }},
            '10Y': { count: 120, interval: 'month', label: (i) => {
                const date = new Date();
                date.setMonth(date.getMonth() - (119-i));
                return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
            }}
        };
        
        const config = dataPoints[timeRange];
        if (!config) return { labels: [], data: [] };
        
        const labels = [];
        const data = [];
        
        // Generate realistic fluctuations around current rate
        const volatility = {
            '12H': 0.002, // 0.2% volatility
            '1D': 0.005,  // 0.5% volatility
            '1W': 0.015,  // 1.5% volatility
            '1M': 0.03,   // 3% volatility
            '1Y': 0.08,   // 8% volatility
            '2Y': 0.12,   // 12% volatility
            '5Y': 0.20,   // 20% volatility
            '10Y': 0.35   // 35% volatility
        }[timeRange];
        
        let previousRate = currentRate * (0.98 + Math.random() * 0.04); // Start within ±2%
        
        for (let i = 0; i < config.count; i++) {
            labels.push(config.label(i));
            
            // Generate realistic price movement
            const change = (Math.random() - 0.5) * volatility * 2;
            const trend = (currentRate - previousRate) * 0.1; // Slight trend toward current rate
            previousRate = previousRate * (1 + change + trend);
            
            // Ensure we end close to current rate for recent data
            if (i === config.count - 1) {
                previousRate = currentRate;
            }
            
            data.push(previousRate);
        }
        
        return { labels, data };
    }
    
    // Method to add conversion result to chart and generate historical data
    addConversionData(fromCurrency, toCurrency, exchangeRate, amount, convertedAmount) {
        // Update current pair
        this.currentPair = { from: fromCurrency, to: toCurrency };
        // Remember base rate for 1 unit display
        this.baseRate = exchangeRate;
        
        // Store the input amount for display
        this.inputAmount = amount;
        
        // Generate historical data for all time ranges based on current rate
        Object.keys(this.chartData).forEach(range => {
            const historicalData = this.generateHistoricalData(exchangeRate, range);
            this.chartData[range].labels = historicalData.labels;
            this.chartData[range].data = historicalData.data;
            this.chartData[range].changeData = this.calculateChangeData(historicalData.data);
        });
        
        // Update currency pair display with input amount
        const fromDisplay = document.querySelector('.chart-from');
        const toDisplay = document.querySelector('.chart-to');
        
        // Always show indicator as: 1 FROM (arrow icon in HTML) TO BASE_RATE (live rate appended by updateChart)
        if (fromDisplay) fromDisplay.textContent = `1 ${fromCurrency}`;
        if (toDisplay) toDisplay.textContent = `${toCurrency} ${(exchangeRate).toFixed(6)}`;
        
        this.updateChart();
        
        if (window.APP_CONFIG?.DEBUG_MODE) {
            console.log(`📊 Chart updated with historical data: ${amount} ${fromCurrency} = ${convertedAmount.toFixed(2)} ${toCurrency} (rate: ${exchangeRate.toFixed(6)})`);
        }
    }
    
    // Lightweight real-time simulation for demo/debug
    startRealTimeSimulation() {
        if (this.simulationInterval) return; // already running
        const tick = () => {
            try {
                const dataset = this.chartData[this.currentRange];
                if (!dataset) return;
                const last = dataset.data.length > 0 ? dataset.data[dataset.data.length - 1] : 1;
                const change = (Math.random() - 0.5) * 0.004; // ±0.4%
                const next = Math.max(0, last * (1 + change));
                const now = new Date();
                const label = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                dataset.labels.push(label);
                dataset.data.push(next);
                // Keep recent window reasonable
                const maxPoints = 60;
                if (dataset.labels.length > maxPoints) dataset.labels.shift();
                if (dataset.data.length > maxPoints) dataset.data.shift();
                this.updateChart();
            } catch (e) {
                // Fail-safe: stop simulation if anything goes wrong
                this.stopRealTimeSimulation();
            }
        };
        this.simulationInterval = setInterval(tick, 3000);
    }

    stopRealTimeSimulation() {
        if (this.simulationInterval) {
            clearInterval(this.simulationInterval);
            this.simulationInterval = null;
        }
    }

    // Clear all chart data
    clearChartData() {
        Object.keys(this.chartData).forEach(range => {
            this.chartData[range].labels = [];
            this.chartData[range].data = [];
        });
        this.updateChart();
    }
    
    destroy() {
        if (this.chart) {
            this.chart.destroy();
        }
    }
}

// Initialize chart when DOM is loaded
let exchangeChart = null;

function initializeExchangeChart() {
    const chartCanvas = document.getElementById('exchangeRateChart');
    if (chartCanvas && !exchangeChart) {
        exchangeChart = new ExchangeRateChart('exchangeRateChart');
        
        // Make chart globally accessible for reset function
        window.exchangeChart = exchangeChart;
        
        // Start real-time simulation for demo
        if (window.APP_CONFIG?.DEBUG_MODE) {
            console.log('🔄 Starting chart real-time simulation');
            exchangeChart.startRealTimeSimulation();
        }
    }
}

// Function to update chart when currency pair changes
function updateChartCurrencyPair(fromCurrency, toCurrency) {
    if (exchangeChart) {
        exchangeChart.updateCurrencyPair(fromCurrency, toCurrency);
    }
}

// Function to add conversion data to chart
function addChartConversionData(fromCurrency, toCurrency, exchangeRate, amount, convertedAmount) {
    if (exchangeChart) {
        exchangeChart.addConversionData(fromCurrency, toCurrency, exchangeRate, amount, convertedAmount);
    }
}

// Export functions for use in main.js
export { initializeExchangeChart, updateChartCurrencyPair, addChartConversionData, ExchangeRateChart };

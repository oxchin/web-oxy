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
    Legend,
    BarController,
    BarElement,
    Decimation
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
    Legend,
    BarController,
    BarElement,
    Decimation
);

// Premium purple vertical crosshair plugin for elegant precision reading
const crosshairLinePlugin = {
    id: 'crosshairLine',
    afterDatasetsDraw(chart, args, opts) {
        const tooltip = chart.tooltip;
        if (!tooltip || !tooltip.getActiveElements || !tooltip.getActiveElements().length) return;
        const x = tooltip.caretX;
        const { top, bottom } = chart.chartArea;
        const ctx = chart.ctx;
        ctx.save();
        ctx.strokeStyle = (opts && opts.color) || '#a78bfa';
        ctx.lineWidth = (opts && opts.lineWidth) || 1;
        ctx.setLineDash((opts && opts.dash) || [4, 4]);
        ctx.beginPath();
        ctx.moveTo(x, top);
        ctx.lineTo(x, bottom);
        ctx.stroke();

        // Draw a small premium purple live dot at the active point for clarity
        const active = tooltip.getActiveElements()[0];
        if (active) {
            const meta = chart.getDatasetMeta(active.datasetIndex);
            const el = meta && meta.data && meta.data[active.index];
            if (el) {
                const px = el.x;
                const py = el.y;
                ctx.fillStyle = '#a78bfa';
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

// Plugin to adjust axis label spacing (hide first X tick to avoid collision with Y label)
const axisLabelSpacingPlugin = {
    id: 'axisLabelSpacing',
    afterBuildTicks(scale, args, options) {
        if (!options || !scale) return;
        // Hide the first x-axis tick label if enabled
        if (scale.id === 'x' && options.hideFirstXLabel) {
            if (Array.isArray(scale.ticks) && scale.ticks.length > 0) {
                if (typeof scale.ticks[0] === 'object') {
                    scale.ticks[0].label = '';
                } else {
                    scale.ticks[0] = '';
                }
            }
        }
    }
};

Chart.register(axisLabelSpacingPlugin);

// Plugin to compress axis footprints to maximize chart area
const tightAxesPlugin = {
    id: 'tightAxes',
    afterFit(scale, args, options) {
        if (!options) return;
        // Reduce x-axis height and y-axis width by configured amounts
        if (scale.id === 'x' && typeof options.xReduce === 'number') {
            scale.height = Math.max(0, scale.height - options.xReduce);
        }
        if (scale.id === 'y' && typeof options.yReduce === 'number') {
            scale.width = Math.max(0, scale.width - options.yReduce);
        }
    }
};

Chart.register(tightAxesPlugin);

// Premium last price label at right edge
const lastPriceLabelPlugin = {
    id: 'lastPriceLabel',
    afterDatasetsDraw(chart, args, opts) {
        if (!opts || opts.enabled === false) return;
        const ds = chart.data && chart.data.datasets && chart.data.datasets[0];
        if (!ds || !Array.isArray(ds.data) || ds.data.length === 0) return;
        if (chart.config.type !== 'line') return; // show only for line/area charts
        const yScale = chart.scales && chart.scales.y;
        if (!yScale) return;
        const values = ds.data;
        const lastIndex = values.length - 1;
        const last = values[lastIndex];
        if (typeof last !== 'number' || !isFinite(last)) return;
        const prev = lastIndex > 0 && typeof values[lastIndex - 1] === 'number' ? values[lastIndex - 1] : last;
        const up = last >= prev;
        const y = yScale.getPixelForValue(last);
        const { top, bottom, right } = chart.chartArea;
        const ctx = chart.ctx;
        
        // Resolve options
        const bg = opts.background || 'rgba(15, 23, 42, 0.95)';
        const upColor = opts.upColor || '#22c55e';
        const downColor = opts.downColor || '#ef4444';
        const borderWidth = (typeof opts.borderWidth === 'number') ? opts.borderWidth : 1;
        const textColor = opts.textColor || '#ffffff';
        const padX = (typeof opts.paddingX === 'number') ? opts.paddingX : 10;
        const padY = (typeof opts.paddingY === 'number') ? opts.paddingY : 6;
        const radius = (typeof opts.radius === 'number') ? opts.radius : 8;
        const fontSize = (opts.font && opts.font.size) || 12;
        const fontWeight = (opts.font && opts.font.weight) || '700';
        const fontFamily = (opts.font && opts.font.family) || 'Inter';
        const shadowBlur = (typeof opts.shadowBlur === 'number') ? opts.shadowBlur : 6;
        const color = up ? upColor : downColor;
        
        // Compose text
        const valueText = new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 6, maximumFractionDigits: 6, useGrouping: true
        }).format(last);
        const text = `Last: ${valueText}`;
        
        // Measure and position
        ctx.save();
        ctx.font = `${fontWeight} ${fontSize}px ${fontFamily}`;
        const textWidth = ctx.measureText(text).width;
        const boxW = textWidth + padX * 2;
        const boxH = fontSize + padY * 2;
        const marginRight = 8;
        let boxX = right - boxW - marginRight;
        let boxY = y - boxH / 2;
        if (boxY < top + 4) boxY = top + 4;
        if (boxY + boxH > bottom - 4) boxY = bottom - boxH - 4;
        
        // Draw connector line from right edge to y
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.2;
        ctx.setLineDash([4, 3]);
        ctx.beginPath();
        ctx.moveTo(right, y);
        ctx.lineTo(boxX + boxW, y);
        ctx.stroke();
        ctx.setLineDash([]);
        
        // Draw rounded rect background with subtle shadow
        ctx.shadowBlur = shadowBlur;
        ctx.shadowColor = color;
        ctx.fillStyle = bg;
        ctx.strokeStyle = color;
        ctx.lineWidth = borderWidth;
        const r = radius;
        ctx.beginPath();
        ctx.moveTo(boxX + r, boxY);
        ctx.lineTo(boxX + boxW - r, boxY);
        ctx.quadraticCurveTo(boxX + boxW, boxY, boxX + boxW, boxY + r);
        ctx.lineTo(boxX + boxW, boxY + boxH - r);
        ctx.quadraticCurveTo(boxX + boxW, boxY + boxH, boxX + boxW - r, boxY + boxH);
        ctx.lineTo(boxX + r, boxY + boxH);
        ctx.quadraticCurveTo(boxX, boxY + boxH, boxX, boxY + boxH - r);
        ctx.lineTo(boxX, boxY + r);
        ctx.quadraticCurveTo(boxX, boxY, boxX + r, boxY);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        // Draw text
        ctx.shadowBlur = 0;
        ctx.fillStyle = textColor;
        ctx.fillText(text, boxX + padX, boxY + padY + fontSize * 0.82);
        
        // Optional delta badge under the price label (change since first value in view)
        if (opts.showDelta) {
            // Find first numeric value in dataset
            let open = last;
            for (let i = 0; i < values.length; i++) {
                const v = values[i];
                if (typeof v === 'number' && isFinite(v)) { open = v; break; }
            }
            if (open > 0) {
                const deltaPct = ((last - open) / open) * 100;
                const deltaUp = deltaPct >= 0;
                const deltaColor = deltaUp ? upColor : downColor;
                const sign = deltaUp ? '+' : '';
                const deltaText = `Δ ${sign}${deltaPct.toFixed(2)}%`;
                ctx.font = `${fontWeight} ${Math.max(11, fontSize - 1)}px ${fontFamily}`;
                const dtw = ctx.measureText(deltaText).width;
                const dbW = dtw + (padX - 2) * 2;
                const dbH = (fontSize - 1) + (padY - 2) * 2;
                const gap = 4;
                let dbX = boxX + (boxW - dbW) / 2;
                let dbY = boxY + boxH + gap;
                if (dbY + dbH > chart.chartArea.bottom - 4) {
                    // If no room below, draw above the price pill
                    dbY = boxY - dbH - gap;
                }
                // Draw badge
                ctx.fillStyle = bg;
                ctx.strokeStyle = deltaColor;
                ctx.lineWidth = borderWidth;
                const rr = Math.max(6, radius - 2);
                ctx.beginPath();
                ctx.moveTo(dbX + rr, dbY);
                ctx.lineTo(dbX + dbW - rr, dbY);
                ctx.quadraticCurveTo(dbX + dbW, dbY, dbX + dbW, dbY + rr);
                ctx.lineTo(dbX + dbW, dbY + dbH - rr);
                ctx.quadraticCurveTo(dbX + dbW, dbY + dbH, dbX + dbW - rr, dbY + dbH);
                ctx.lineTo(dbX + rr, dbY + dbH);
                ctx.quadraticCurveTo(dbX, dbY + dbH, dbX, dbY + dbH - rr);
                ctx.lineTo(dbX, dbY + rr);
                ctx.quadraticCurveTo(dbX, dbY, dbX + rr, dbY);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
                ctx.fillStyle = textColor;
                ctx.fillText(deltaText, dbX + (padX - 2), dbY + (padY - 2) + (fontSize - 1) * 0.82);
            }
        }
        ctx.restore();
    }
};

Chart.register(lastPriceLabelPlugin);

// Soft glow behind line/area for premium look
const lineGlowPlugin = {
    id: 'lineGlow',
    afterDatasetsDraw(chart, args, opts) {
        if (!opts || opts.enabled === false) return;
        const { ctx, data } = chart;
        const blur = opts.blur ?? 12;
        const width = opts.width ?? 6;
        const alpha = opts.alpha ?? 0.25;
        const color = opts.color || '#8b5cf6';
        (chart.getSortedVisibleDatasetMetas() || []).forEach(meta => {
            if (meta.type !== 'line') return;
            const points = meta.data || [];
            if (points.length < 2) return;
            ctx.save();
            ctx.shadowBlur = blur;
            ctx.shadowColor = color;
            ctx.strokeStyle = color;
            ctx.globalAlpha = alpha;
            ctx.lineWidth = width;
            ctx.lineJoin = 'round';
            ctx.lineCap = 'round';
            ctx.beginPath();
            for (let i = 0; i < points.length; i++) {
                const p = points[i];
                if (!p || typeof p.x !== 'number' || typeof p.y !== 'number') continue;
                if (i === 0) ctx.moveTo(p.x, p.y);
                else ctx.lineTo(p.x, p.y);
            }
            ctx.stroke();
            ctx.restore();
        });
    }
};

Chart.register(lineGlowPlugin);

// Markers for session High and Low
const minMaxMarkersPlugin = {
    id: 'minMaxMarkers',
    afterDatasetsDraw(chart, args, opts) {
        if (!opts || opts.enabled === false) return;
        const meta = chart.getDatasetMeta(0);
        if (!meta || meta.type !== 'line') return; // only for line/area
        const points = meta.data || [];
        if (points.length === 0) return;
        const ds = chart.data.datasets[0];
        const values = (ds && Array.isArray(ds.data)) ? ds.data : [];
        if (values.length === 0) return;
        let minIdx = 0, maxIdx = 0;
        for (let i = 1; i < values.length; i++) {
            const v = values[i];
            if (typeof v !== 'number' || !isFinite(v)) continue;
            if (v < values[minIdx]) minIdx = i;
            if (v > values[maxIdx]) maxIdx = i;
        }
        const drawTag = (idx, label, color) => {
            const p = points[idx];
            if (!p) return;
            const ctx = chart.ctx;
            const padX = opts.paddingX ?? 8;
            const padY = opts.paddingY ?? 4;
            const r = opts.radius ?? 6;
            const fs = (opts.font && opts.font.size) || 11;
            const fw = (opts.font && opts.font.weight) || '700';
            const ff = (opts.font && opts.font.family) || 'Inter';
            const bg = opts.background || 'rgba(15, 23, 42, 0.96)';
            const text = `${label}`;
            ctx.save();
            ctx.font = `${fw} ${fs}px ${ff}`;
            const tw = ctx.measureText(text).width;
            const th = fs + padY * 2;
            const bw = tw + padX * 2;
            const bh = th;
            let bx = p.x - bw / 2;
            let by = label === 'HIGH' ? (p.y - bh - 10) : (p.y + 10);
            const { left, right, top, bottom } = chart.chartArea;
            if (bx < left + 4) bx = left + 4;
            if (bx + bw > right - 4) bx = right - bw - 4;
            if (by < top + 4) by = top + 4;
            if (by + bh > bottom - 4) by = bottom - bh - 4;
            // Tag
            ctx.fillStyle = bg;
            ctx.strokeStyle = color;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(bx + r, by);
            ctx.lineTo(bx + bw - r, by);
            ctx.quadraticCurveTo(bx + bw, by, bx + bw, by + r);
            ctx.lineTo(bx + bw, by + bh - r);
            ctx.quadraticCurveTo(bx + bw, by + bh, bx + bw - r, by + bh);
            ctx.lineTo(bx + r, by + bh);
            ctx.quadraticCurveTo(bx, by + bh, bx, by + bh - r);
            ctx.lineTo(bx, by + r);
            ctx.quadraticCurveTo(bx, by, bx + r, by);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
            // Text
            ctx.fillStyle = '#ffffff';
            ctx.fillText(text, bx + padX, by + padY + fs * 0.82);
            ctx.restore();
        };
        drawTag(maxIdx, 'HIGH', '#22c55e');
        drawTag(minIdx, 'LOW', '#ef4444');
    }
};

Chart.register(minMaxMarkersPlugin);

// Hover Y-value pill on the left edge following the crosshair/tooltip
const hoverYLabelPlugin = {
    id: 'hoverYLabel',
    afterDatasetsDraw(chart, args, opts) {
        if (!opts || opts.enabled === false) return;
        const tooltip = chart.tooltip;
        if (!tooltip || !tooltip.getActiveElements || !tooltip.getActiveElements().length) return;
        const active = tooltip.getActiveElements()[0];
        const ds = chart.data && chart.data.datasets && chart.data.datasets[active.datasetIndex || 0];
        if (!ds || !Array.isArray(ds.data)) return;
        const idx = active.index;
        const value = ds.data[idx];
        if (typeof value !== 'number' || !isFinite(value)) return;
        const yScale = chart.scales && chart.scales.y;
        const y = yScale.getPixelForValue(value);
        const { left, right, top, bottom } = chart.chartArea;
        const ctx = chart.ctx;
        const bg = opts.background || 'rgba(15, 23, 42, 0.96)';
        const borderColor = opts.borderColor || '#8b5cf6';
        const textColor = opts.textColor || '#ffffff';
        const padX = (typeof opts.paddingX === 'number') ? opts.paddingX : 10;
        const padY = (typeof opts.paddingY === 'number') ? opts.paddingY : 6;
        const radius = (typeof opts.radius === 'number') ? opts.radius : 8;
        const fontSize = (opts.font && opts.font.size) || 12;
        const fontWeight = (opts.font && opts.font.weight) || '700';
        const fontFamily = (opts.font && opts.font.family) || 'Inter';
        const marginLeft = (typeof opts.marginLeft === 'number') ? opts.marginLeft : 8;
        const valueText = new Intl.NumberFormat('en-US', { minimumFractionDigits: 6, maximumFractionDigits: 6, useGrouping: true }).format(value);
        const text = valueText;
        ctx.save();
        ctx.font = `${fontWeight} ${fontSize}px ${fontFamily}`;
        const tw = ctx.measureText(text).width;
        const bw = tw + padX * 2;
        const bh = fontSize + padY * 2;
        let bx = left + marginLeft;
        let by = y - bh / 2;
        if (by < top + 4) by = top + 4;
        if (by + bh > bottom - 4) by = bottom - bh - 4;
        // connector from left to badge
        ctx.strokeStyle = borderColor;
        ctx.lineWidth = 1.2;
        ctx.setLineDash([4, 3]);
        ctx.beginPath();
        ctx.moveTo(left, y);
        ctx.lineTo(bx, y);
        ctx.stroke();
        ctx.setLineDash([]);
        // badge
        ctx.fillStyle = bg;
        ctx.strokeStyle = borderColor;
        ctx.lineWidth = 1;
        const r = radius;
        ctx.beginPath();
        ctx.moveTo(bx + r, by);
        ctx.lineTo(bx + bw - r, by);
        ctx.quadraticCurveTo(bx + bw, by, bx + bw, by + r);
        ctx.lineTo(bx + bw, by + bh - r);
        ctx.quadraticCurveTo(bx + bw, by + bh, bx + bw - r, by + bh);
        ctx.lineTo(bx + r, by + bh);
        ctx.quadraticCurveTo(bx, by + bh, bx, by + bh - r);
        ctx.lineTo(bx, by + r);
        ctx.quadraticCurveTo(bx, by, bx + r, by);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = textColor;
        ctx.fillText(text, bx + padX, by + padY + fontSize * 0.82);
        ctx.restore();
    }
};

Chart.register(hoverYLabelPlugin);

// UTC Time Utilities
function getUTCDate() {
    const now = new Date();
    return new Date(now.getTime() + (now.getTimezoneOffset() * 60000));
}

function formatUTCTime(options = {}) {
    const utcDate = getUTCDate();
    const defaultOptions = {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
        timeZone: 'UTC'
    };
    return utcDate.toLocaleTimeString('en-US', { ...defaultOptions, ...options });
}

// Chart configuration and data management
class ExchangeRateChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.chart = null;
        this.currentRange = '12H';
        this.currentPair = { from: null, to: null };
        this.chartType = 'area'; // Default chart type: 'area', 'bar', 'line'
        // Theme from CSS variables (scoped to container 3 when available)
        this.theme = this.getThemeColors();
        
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

    getThemeColors() {
        const scope = document.querySelector('.container--3') || document.documentElement;
        const cs = getComputedStyle(scope);
        const read = (name, fallback) => (cs.getPropertyValue(name) || '').trim() || fallback;
        return {
            line: read('--chart-purple-line', '#8b5cf6'),
            point: read('--chart-purple-point', '#a78bfa'),
            pointHover: read('--chart-purple-point-hover', '#c4b5fd'),
            fill0: read('--chart-purple-fill-0', 'rgba(139, 92, 246, 0.35)'),
            fill50: read('--chart-purple-fill-50', 'rgba(139, 92, 246, 0.18)'),
            fill100: read('--chart-purple-fill-100', 'rgba(139, 92, 246, 0.06)'),
            tooltipBorder: read('--chart-tooltip-border', '#8b5cf6'),
            crosshair: read('--chart-crosshair', '#a78bfa')
        };
    }
    
    initializeChart() {
        const data = this.chartData[this.currentRange];
        
        // Create premium purple gradient fill (deep royal purple → transparent)
        const gradient = this.ctx.createLinearGradient(0, 0, 0, 550);
        gradient.addColorStop(0, 'rgba(102, 51, 153, 0.8)');
        gradient.addColorStop(0.2, 'rgba(123, 63, 191, 0.6)');
        gradient.addColorStop(0.4, 'rgba(139, 92, 246, 0.4)');
        gradient.addColorStop(0.7, 'rgba(139, 92, 246, 0.15)');
        gradient.addColorStop(1, 'rgba(139, 92, 246, 0)');
        
        // Create futuristic cyan→purple line gradient
        const lineGradient = this.ctx.createLinearGradient(0, 0, this.canvas.width, 0);
        lineGradient.addColorStop(0, '#00e0ff'); // cyan start
        lineGradient.addColorStop(0.5, '#00a6fb'); // mid blue
        lineGradient.addColorStop(1, '#8b5cf6'); // purple end
        
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
        // Create sharp fintech line gradient (cyan→purple)
        const lineGradient = this.ctx.createLinearGradient(0, 0, this.canvas.width, 0);
        lineGradient.addColorStop(0, '#00d9ff'); // bright cyan
        lineGradient.addColorStop(0.3, '#3b82f6'); // royal blue
        lineGradient.addColorStop(0.7, '#7c3aed'); // deep purple
        lineGradient.addColorStop(1, '#9333ea'); // vibrant purple
        
        if (this.chartType === 'bar') {
            return this.getBarChartConfig(data, positiveGradient, negativeGradient);
        } else if (this.chartType === 'line') {
            return this.getLineChartConfig(data, lineGradient);
        } else {
            return this.getAreaChartConfig(data, gradient, lineGradient);
        }
    }
    
    getAreaChartConfig(data, gradient, lineGradient) {
        return {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: this.currentPair.from && this.currentPair.to ? `${this.currentPair.from} to ${this.currentPair.to}` : 'Exchange Rate',
                    data: data.data,
                    borderColor: lineGradient,
                    backgroundColor: gradient,
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 0,
                    pointHitRadius: 12,
                    pointHoverBorderWidth: 0,
                    pointBorderWidth: 0,
                    drawActiveElementsOnTop: true
                }]
            },
            options: this.getCommonOptions()
        };
    }
    
    getLineChartConfig(data, lineGradient) {
        return {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: this.currentPair.from && this.currentPair.to ? `${this.currentPair.from} to ${this.currentPair.to}` : 'Exchange Rate',
                    data: data.data,
                    borderColor: lineGradient,
                    backgroundColor: 'transparent',
                    borderWidth: 2.5,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 0,
                    pointHitRadius: 12,
                    pointHoverBorderWidth: 0,
                    pointBorderWidth: 0,
                    drawActiveElementsOnTop: true
                }]
            },
            options: this.getCommonOptions()
        };
    }
    
    getBarChartConfig(data, positiveGradient, negativeGradient) {
        const changeData = data.changeData || [];
        // Determine bounds ensuring 0 is always in view
        const minChange = changeData.length ? Math.min(0, ...changeData) : -1;
        const maxChange = changeData.length ? Math.max(0, ...changeData) : 1;
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
                    // Ensure colors always reflect direction: green up, red down
                    backgroundColor: (ctx) => {
                        const v = ctx.raw;
                        return (typeof v === 'number' && v >= 0) ? positiveGradient : negativeGradient;
                    },
                    borderColor: (ctx) => {
                        const v = ctx.raw;
                        return (typeof v === 'number' && v >= 0) ? '#22c55e' : '#ef4444';
                    },
                    borderWidth: 1.5,
                    borderRadius: 4,
                    borderSkipped: false,
                    barPercentage: 0.9,
                    categoryPercentage: 0.9
                }]
            },
            options: {
                ...this.getCommonOptions(),
                plugins: {
                    ...this.getCommonOptions().plugins,
                    tooltip: {
                        ...this.getCommonOptions().plugins.tooltip,
                        // For change% mode, show signed percent and color the label accordingly
                        callbacks: {
                            title: function(context) {
                                return `Time: ${context[0].label}`;
                            },
                            label: function(context) {
                                const v = context.parsed.y;
                                const sign = (typeof v === 'number' && v >= 0) ? '+' : '';
                                return `Change: ${sign}${v.toFixed(2)}%`;
                            },
                            labelTextColor: function(context) {
                                const v = context.parsed.y;
                                return (typeof v === 'number' && v >= 0) ? '#22c55e' : '#ef4444';
                            }
                        }
                    }
                },
                scales: {
                    ...this.getCommonOptions().scales,
                    y: {
                        ...this.getCommonOptions().scales.y,
                        // Keep 0 visible and highlight it as the baseline
                        suggestedMin: minChange - 0.5,
                        suggestedMax: maxChange + 0.5,
                        grid: {
                            color: (ctx) => ctx.tick && ctx.tick.value === 0 ? 'rgba(255, 255, 255, 0.35)' : 'rgba(255, 255, 255, 0.06)',
                            lineWidth: (ctx) => ctx.tick && ctx.tick.value === 0 ? 1.2 : 0.5,
                            drawBorder: true,
                            borderColor: 'rgba(255, 255, 255, 0.18)',
                            drawTicks: false,
                            display: true
                        },
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
            hover: {
                intersect: false,
                mode: 'nearest'
            },
            animation: {
                duration: 600,
                easing: 'easeInOutQuart',
                animateRotate: false,
                animateScale: true
            },
            transitions: {
                show: {
                    animations: {
                        x: {
                            from: 0
                        },
                        y: {
                            from: 0
                        }
                    }
                }
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
                    backgroundColor: 'rgba(15, 23, 42, 0.96)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#e2e8f0',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    cornerRadius: 10,
                    displayColors: false,
                    padding: 20,
                    caretSize: 7,
                    caretPadding: 8,
                    usePointStyle: false,
                    titleFont: {
                        family: 'Inter',
                        size: 15,
                        weight: '700'
                    },
                    titleMarginBottom: 6,
                    bodyFont: {
                        family: 'Inter',
                        size: 14,
                        weight: '600'
                    },
                    bodySpacing: 6,
                    callbacks: {
                        title: function(context) {
                            return `Time: ${context[0].label}`;
                        },
                        label: function(context) {
                            const value = context.parsed.y;
                            // Format with proper number formatting
                            const formatted = new Intl.NumberFormat('en-US', {
                                minimumFractionDigits: 6,
                                maximumFractionDigits: 6,
                                useGrouping: true
                            }).format(value);
                            return `Rate: ${formatted}`;
                        }
                    }
                },
                crosshairLine: {
                    color: this.theme.crosshair,
                    lineWidth: 1.5,
                    dash: [6, 4]
                },
                axisLabelSpacing: {
                    hideFirstXLabel: false
                },
                tightAxes: {
                    xReduce: 0,
                    yReduce: 0
                },
                lastPriceLabel: {
                    enabled: true,
                    background: 'rgba(15, 23, 42, 0.95)',
                    upColor: '#22c55e',
                    downColor: '#ef4444',
                    textColor: '#ffffff',
                    paddingX: 10,
                    paddingY: 6,
                    radius: 8,
                    borderWidth: 1,
                    shadowBlur: 8,
                    font: { family: 'Inter', size: 12, weight: '700' },
                    showDelta: true
                },
                lineGlow: {
                    enabled: false,
                    color: '#8b5cf6',
                    blur: 12,
                    width: 6,
                    alpha: 0.28
                },
                minMaxMarkers: {
                    enabled: true,
                    background: 'rgba(15, 23, 42, 0.96)',
                    paddingX: 8,
                    paddingY: 4,
                    radius: 6,
                    font: { family: 'Inter', size: 11, weight: '700' }
                },
                hoverYLabel: {
                    enabled: true,
                    background: 'rgba(15, 23, 42, 0.96)',
                    borderColor: '#8b5cf6',
                    textColor: '#ffffff',
                    paddingX: 10,
                    paddingY: 6,
                    radius: 8,
                    marginLeft: 8,
                    font: { family: 'Inter', size: 12, weight: '700' }
                }
            },
            layout: {
                padding: {
                    top: 0,
                    right: 0,
                    bottom: 16,
                    left: 0
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
                    type: 'category',
                    display: true,
                    offset: false,
                    bounds: 'ticks',
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
                        color: 'rgba(255, 255, 255, 0.06)',
                        drawBorder: true,
                        borderColor: 'rgba(255, 255, 255, 0.18)',
                        lineWidth: 0.5,
                        offset: false,
                        drawTicks: false,
                        // subtle professional gridlines
                        display: true
                    },
                    ticks: {
                        font: {
                            family: 'Inter',
                            size: 12,
                            weight: '600'
                        },
                        color: '#ffffff',
                        padding: 10,
                        autoSkipPadding: 28,
                        maxRotation: 0,
                        sampleSize: 8,
                        callback: function(value, index, ticks) {
                            // Use category scale mapping to turn index into the actual label
                            if (typeof this.getLabelForValue === 'function') {
                                return this.getLabelForValue(value);
                            }
                            const tick = ticks && ticks[index] ? ticks[index] : null;
                            return (tick && typeof tick.label !== 'undefined') ? tick.label : String(value);
                        },
                        // show time labels by default; autoskip keeps it readable
                        display: true
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
                        color: 'rgba(255, 255, 255, 0.06)',
                        drawBorder: true,
                        borderColor: 'rgba(255, 255, 255, 0.18)',
                        lineWidth: 0.5,
                        drawTicks: false,
                        // subtle professional gridlines
                        display: true
                    },
                    ticks: {
                        color: '#ffffff',
                        font: {
                            family: 'Inter',
                            size: 13,
                            weight: '700'
                        },
                        padding: 18,
                        // show Y-axis price labels for readability
                        display: true,
                        callback: function(value) {
                            // Format Y-axis with proper number formatting
                            return new Intl.NumberFormat('en-US', {
                                minimumFractionDigits: 6,
                                maximumFractionDigits: 6,
                                useGrouping: true
                            }).format(value);
                        }
                    }
                }
            }
        };
    }
    
    setupEventListeners() {
        // Time range button listeners
        const timeRangeBtns = document.querySelectorAll('.time-range-btn');
        timeRangeBtns.forEach(btn => {
            // Initialize aria-pressed based on initial state
            btn.setAttribute('aria-pressed', btn.classList.contains('active') ? 'true' : 'false');
            btn.addEventListener('click', (e) => {
                const el = e.currentTarget;
                // Remove active and reset aria-pressed
                timeRangeBtns.forEach(b => { b.classList.remove('active'); b.setAttribute('aria-pressed', 'false'); });
                // Add active to the correct element and set aria-pressed
                el.classList.add('active');
                el.setAttribute('aria-pressed', 'true');
                
                // Update chart data
                this.currentRange = el.dataset.range;
                this.updateChart();
            });
        });
        
        // Chart type button listeners
        const chartTypeBtns = document.querySelectorAll('.chart-type-btn');
        chartTypeBtns.forEach(btn => {
            // Initialize aria-pressed based on initial state
            btn.setAttribute('aria-pressed', btn.classList.contains('active') ? 'true' : 'false');
            btn.addEventListener('click', (e) => {
                const el = e.currentTarget;
                // Remove active from all and reset aria-pressed
                chartTypeBtns.forEach(b => { b.classList.remove('active'); b.setAttribute('aria-pressed', 'false'); });
                // Add to the correct button and set aria
                el.classList.add('active');
                el.setAttribute('aria-pressed', 'true');
                
                // Update chart type
                this.chartType = el.dataset.type;
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
        if (this.chartType === 'bar') {
            this.chart.data.datasets[0].data = data.changeData;
        } else {
            this.chart.data.datasets[0].data = data.data;
        }
        this.chart.data.datasets[0].label = `${this.currentPair.from} to ${this.currentPair.to}`;
        
        // Update titles and toggle axes visibility depending on data
        const hasData = (data.labels && data.labels.length > 0) && (data.data && data.data.length > 0);
        
        // Axis titles
        this.chart.options.scales.y.title.text = `Value (${this.currentPair.to})`;
        
        // Grid and ticks visibility - always show for better readability
        this.chart.options.scales.x.grid.display = true;
        this.chart.options.scales.y.grid.display = true;
        this.chart.options.scales.x.ticks.display = true;
        this.chart.options.scales.y.ticks.display = hasData; // show price labels when data is present
        
        // Tooltip visibility
        this.chart.options.plugins.tooltip.enabled = hasData;
        
        // Compose indicator line: 1 FROM -> TO BASE_RATE LIVE_RATE
        const fromDisplay = document.querySelector('.chart-from');
        const toDisplay = document.querySelector('.chart-to');
        const currentRateElement = document.querySelector('.chart-current-rate');
        if (fromDisplay && toDisplay) {
            const last = (data.data && data.data.length > 0) ? data.data[data.data.length - 1] : null;
            const chosenRate = (last !== null && !isNaN(last))
                ? last
                : (typeof this.baseRate === 'number' && !isNaN(this.baseRate) ? this.baseRate : 0);
            // Left shows '1 FROM ='
            fromDisplay.textContent = `1 ${this.currentPair.from} =`;
            // Right shows '<rate> TO' with 6 decimals and comma formatting
            const formattedRate = new Intl.NumberFormat('en-US', {
                minimumFractionDigits: 6,
                maximumFractionDigits: 6,
                useGrouping: true
            }).format(chosenRate);
            toDisplay.textContent = `${formattedRate} ${this.currentPair.to}`;
        }
        // Clear separate current-rate element (removed from HTML) to avoid duplicate numbers
        if (currentRateElement) currentRateElement.textContent = '';
        
        this.chart.update('active');
    }
    
    updateCurrencyPair(fromCurrency, toCurrency) {
        this.currentPair = { from: fromCurrency, to: toCurrency };
        
        // Update currency pair display with input amount
        const fromDisplay = document.querySelector('.chart-from');
        const toDisplay = document.querySelector('.chart-to');
        
        // Always show indicator as: 1 FROM (arrow icon in HTML) TO BASE_RATE (live rate appended by updateChart)
        if (fromDisplay) fromDisplay.textContent = `1 ${fromCurrency}`;
        if (toDisplay) toDisplay.textContent = `${toCurrency}`;
        
        this.updateChart();
        
        if (window.APP_CONFIG?.DEBUG_MODE) {
            console.log(`📊 Chart updated with historical data`);
        }
    }
    
    // Clear all chart data
    clearChartData() {
        Object.keys(this.chartData).forEach(range => {
            this.chartData[range].labels = [];
            this.chartData[range].data = [];
            this.chartData[range].changeData = [];
        });
        this.updateChart();
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
                const label = formatUTCTime();
                dataset.labels.push(label);
                dataset.data.push(next);
                dataset.changeData = this.calculateChangeData(dataset.data);
                // Keep recent window reasonable
                const maxPoints = 60;
                if (dataset.labels.length > maxPoints) dataset.labels.shift();
                if (dataset.data.length > maxPoints) dataset.data.shift();
                if (dataset.changeData.length > maxPoints) dataset.changeData.shift();
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

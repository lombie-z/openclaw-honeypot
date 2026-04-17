// Chart.js rendering for the experiment dashboard.
// Depends on global variables: classData, classes, asrMatrix

const COLORS = [
    '#58a6ff', '#f85149', '#d29922', '#bc8cff', '#f778ba', '#76e3ea',
];

let activeClasses = new Set(classes);
let charts = {};

function getColor(i) {
    return COLORS[i % COLORS.length];
}

function toggleClass() {
    activeClasses.clear();
    document.querySelectorAll('#class-toggles input:checked').forEach(cb => {
        activeClasses.add(cb.dataset.class);
    });
    // Toggle table rows
    document.querySelectorAll('[data-class]').forEach(el => {
        if (el.tagName === 'TR' || el.tagName === 'DIV') {
            el.style.display = activeClasses.has(el.dataset.class) ? '' : 'none';
        }
    });
    // Rebuild charts
    renderAllCharts();
}

function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + tabId).classList.add('active');
    event.target.classList.add('active');
}

function renderAllCharts() {
    renderASRChart();
    renderTokensChart();
    renderToolDistChart();
    renderThinkingChart();
    renderSafetyChart();
}

function destroyChart(id) {
    if (charts[id]) {
        charts[id].destroy();
        delete charts[id];
    }
}

function filterClasses() {
    return classes.filter(c => activeClasses.has(c));
}

function renderASRChart() {
    destroyChart('asr');
    const filtered = filterClasses();
    const ctx = document.getElementById('asr-chart');
    if (!ctx) return;

    charts['asr'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: filtered,
            datasets: [{
                label: 'ASR',
                data: filtered.map(c => (asrMatrix[c] || 0) * 100),
                backgroundColor: filtered.map((_, i) => getColor(classes.indexOf(filtered[i]))),
                borderRadius: 4,
            }],
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true, max: 100,
                    title: { display: true, text: 'ASR %', color: '#8b949e' },
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' },
                },
                x: { ticks: { color: '#8b949e' }, grid: { display: false } },
            },
        },
    });
}

function renderTokensChart() {
    destroyChart('tokens');
    const filtered = filterClasses();
    const ctx = document.getElementById('tokens-chart');
    if (!ctx) return;

    charts['tokens'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: filtered,
            datasets: [{
                label: 'Mean Total Tokens',
                data: filtered.map(c => classData[c]?.mean_total_tokens || 0),
                backgroundColor: filtered.map((_, i) => getColor(classes.indexOf(filtered[i]))),
                borderRadius: 4,
            }],
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Tokens', color: '#8b949e' },
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' },
                },
                x: { ticks: { color: '#8b949e' }, grid: { display: false } },
            },
        },
    });
}

function renderToolDistChart() {
    destroyChart('tool-dist');
    const filtered = filterClasses();
    const ctx = document.getElementById('tool-dist-chart');
    if (!ctx) return;

    // Collect all tool names across active classes
    const allTools = new Set();
    filtered.forEach(c => {
        Object.keys(classData[c]?.tool_distribution || {}).forEach(t => allTools.add(t));
    });
    const tools = [...allTools].sort();

    const datasets = filtered.map((c, i) => ({
        label: c,
        data: tools.map(t => classData[c]?.tool_distribution?.[t] || 0),
        backgroundColor: getColor(classes.indexOf(c)),
        borderRadius: 4,
    }));

    charts['tool-dist'] = new Chart(ctx, {
        type: 'bar',
        data: { labels: tools, datasets },
        options: {
            responsive: true,
            plugins: { legend: { labels: { color: '#e6edf3' } } },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Mean Count', color: '#8b949e' },
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' },
                },
                x: { ticks: { color: '#8b949e' }, grid: { display: false } },
            },
        },
    });
}

function renderThinkingChart() {
    destroyChart('thinking');
    const filtered = filterClasses();
    const ctx = document.getElementById('thinking-chart');
    if (!ctx) return;

    charts['thinking'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: filtered,
            datasets: [{
                label: 'Mean Thinking Chars',
                data: filtered.map(c => classData[c]?.mean_thinking_chars || 0),
                backgroundColor: filtered.map((_, i) => getColor(classes.indexOf(filtered[i]))),
                borderRadius: 4,
            }],
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Chars', color: '#8b949e' },
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' },
                },
                x: { ticks: { color: '#8b949e' }, grid: { display: false } },
            },
        },
    });
}

function renderSafetyChart() {
    destroyChart('safety');
    const filtered = filterClasses();
    const ctx = document.getElementById('safety-chart');
    if (!ctx) return;

    charts['safety'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: filtered,
            datasets: [{
                label: 'Safety Mention Rate',
                data: filtered.map(c => (classData[c]?.safety_mention_rate || 0) * 100),
                backgroundColor: filtered.map((_, i) => getColor(classes.indexOf(filtered[i]))),
                borderRadius: 4,
            }],
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true, max: 100,
                    title: { display: true, text: '%', color: '#8b949e' },
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' },
                },
                x: { ticks: { color: '#8b949e' }, grid: { display: false } },
            },
        },
    });
}

// Initial render
document.addEventListener('DOMContentLoaded', renderAllCharts);

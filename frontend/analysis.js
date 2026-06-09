function renderAnalysis(data) {
    const mode = localStorage.getItem('mode') || 'beginner';
    const container = document.getElementById('analysis-view');
    if (mode === 'advanced') {
        container.innerHTML = `<pre>${JSON.stringify(data.metrics, null, 2)}</pre>`;
    } else {
        container.innerHTML = `<h3>Health Score: ${data.score}</h3>`;
    }
}

function toggleMode() {
    const current = localStorage.getItem('mode') || 'beginner';
    localStorage.setItem('mode', current === 'beginner' ? 'advanced' : 'beginner');
}

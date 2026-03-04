/**
 * QR History — Saves generated QR codes to LocalStorage
 */
const QR_HISTORY_KEY = 'qr_studio_history';
const MAX_HISTORY = 50;

function getHistory() {
    try {
        return JSON.parse(localStorage.getItem(QR_HISTORY_KEY)) || [];
    } catch { return []; }
}

function saveToHistory(type, data, imageBase64) {
    const history = getHistory();
    history.unshift({
        id: Date.now(),
        type: type,
        data: data,
        image: imageBase64,
        date: new Date().toISOString(),
    });
    if (history.length > MAX_HISTORY) history.pop();
    localStorage.setItem(QR_HISTORY_KEY, JSON.stringify(history));
}

function deleteFromHistory(id) {
    const history = getHistory().filter(h => h.id !== id);
    localStorage.setItem(QR_HISTORY_KEY, JSON.stringify(history));
    renderHistoryPage();
}

function clearHistory() {
    localStorage.removeItem(QR_HISTORY_KEY);
    renderHistoryPage();
}

function renderHistoryPage() {
    const grid = document.getElementById('historyGrid');
    if (!grid) return;
    const history = getHistory();
    if (history.length === 0) {
        grid.innerHTML = `
      <div class="history-empty" style="grid-column:1/-1;">
        <div class="empty-icon">📭</div>
        <p>No QR codes yet. Generate your first one!</p>
        <a href="/" class="btn btn-primary mt-2">Create QR Code →</a>
      </div>`;
        return;
    }
    grid.innerHTML = history.map(item => `
    <div class="history-item">
      <img src="data:image/png;base64,${item.image}" alt="${item.type} QR Code">
      <div class="history-type">${item.type}</div>
      <div class="history-date">${new Date(item.date).toLocaleDateString()}</div>
      <div style="display:flex;gap:6px;justify-content:center;">
        <button class="btn btn-sm btn-primary" onclick="downloadHistoryQR('${item.image}', '${item.type}')">📥</button>
        <button class="btn btn-sm btn-secondary" onclick="deleteFromHistory(${item.id})">🗑️</button>
      </div>
    </div>
  `).join('');
}

function downloadHistoryQR(base64, type) {
    const a = document.createElement('a');
    a.href = 'data:image/png;base64,' + base64;
    a.download = `qr-${type}-${Date.now()}.png`;
    a.click();
}

// Auto-render if on history page
document.addEventListener('DOMContentLoaded', renderHistoryPage);

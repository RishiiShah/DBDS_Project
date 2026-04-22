document.addEventListener('DOMContentLoaded', () => {
  const countdownEl = document.querySelector('.countdown');
  const historyTable = document.getElementById('bid-history-table');
  const historyBody = document.getElementById('bid-history-body');
  const currentPriceEl = document.getElementById('current-price');

  function formatRemaining(msLeft) {
    const totalSeconds = Math.max(0, Math.floor(msLeft / 1000));
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }

  if (countdownEl) {
    const endTime = new Date(countdownEl.dataset.endTime);
    const tick = () => {
      const now = new Date();
      const remaining = endTime.getTime() - now.getTime();
      if (remaining <= 0) {
        countdownEl.textContent = '00:00:00';
        return;
      }
      countdownEl.textContent = formatRemaining(remaining);
    };
    tick();
    setInterval(tick, 1000);
  }

  async function refreshHistory() {
    if (!historyTable || !historyBody) return;
    const url = historyTable.dataset.historyUrl;
    if (!url) return;

    try {
      const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
      if (!res.ok) return;
      const bids = await res.json();

      historyBody.innerHTML = '';
      if (!Array.isArray(bids) || bids.length === 0) {
        historyBody.innerHTML = '<tr><td colspan="4" style="padding: 8px;">No bids yet.</td></tr>';
        return;
      }

      bids.forEach((bid, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td style="padding: 8px;">${bid.bidder}</td>
          <td style="padding: 8px;">
            <span class="role-badge ${bid.is_auto ? 'role-admin' : 'role-user'}">${bid.is_auto ? 'Auto' : 'Manual'}</span>
          </td>
          <td style="padding: 8px;">$${bid.amount}</td>
          <td style="padding: 8px;">${new Date(bid.created_at).toISOString().replace('T', ' ').slice(0, 19)} UTC</td>
        `;
        historyBody.appendChild(row);

        if (index === 0 && currentPriceEl) {
          currentPriceEl.textContent = `$${bid.amount}`;
        }
      });
    } catch (err) {
      console.error('Failed to refresh bid history.', err);
    }
  }

  if (historyTable) {
    setInterval(refreshHistory, 5000);
  }
});

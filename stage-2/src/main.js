/**
 * GhostProcess Frontend Application Core
 * Fast Single Page Router & Live Ledger Monitor
 */
import { api } from './api.js';
import { toast } from './components/toast.js';
import { modal } from './components/modal.js';
import { renderDashboard } from './views/dashboard.js';
import { renderWallets } from './views/wallets.js';
import { renderWalletDetail } from './views/wallet-detail.js';
import { renderTransfer } from './views/transfer.js';
import { renderAudit } from './views/audit.js';

// Active router state
let currentRoute = '';
const appRoot = document.getElementById('app-root');

// Client-Side Router
async function handleRouting() {
  const hash = window.location.hash || '#dashboard';
  const [routePart, queryPart] = hash.split('?');
  const searchParams = new URLSearchParams(queryPart || '');

  // Update navigation active states
  document.querySelectorAll('.nav-item').forEach(item => {
    const itemRoute = item.getAttribute('data-route');
    if (routePart.startsWith(`#${itemRoute}`)) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  currentRoute = routePart;

  if (routePart === '#dashboard' || routePart === '#' || routePart === '') {
    await renderDashboard(appRoot);
  } else if (routePart === '#wallets') {
    await renderWallets(appRoot);
  } else if (routePart.startsWith('#wallet/')) {
    const walletId = routePart.replace('#wallet/', '');
    await renderWalletDetail(appRoot, walletId);
  } else if (routePart === '#transfer') {
    await renderTransfer(appRoot, searchParams);
  } else if (routePart === '#audit') {
    await renderAudit(appRoot);
  } else {
    window.location.hash = '#dashboard';
  }
}

// Global System Health Poller
async function checkSystemHealth() {
  const dot = document.getElementById('health-dot');
  const label = document.getElementById('health-label');
  const stripZeroSum = document.getElementById('strip-zero-sum');

  try {
    const start = performance.now();
    const health = await api.getHealth();
    const latency = Math.round(performance.now() - start);

    if (dot) {
      dot.className = 'health-dot online';
    }
    if (label) {
      label.textContent = `API: Online (${latency}ms)`;
    }

    // Check ledger state in background to keep invariant strip updated
    const state = await api.exportState().catch(() => null);
    if (state && stripZeroSum) {
      const sum = state.ledger_sum || '0.00';
      const isZero = parseFloat(sum) === 0;
      stripZeroSum.textContent = `Σ = ${sum}`;
      stripZeroSum.style.color = isZero ? 'var(--success)' : 'var(--error)';
    }
  } catch (err) {
    if (dot) {
      dot.className = 'health-dot offline';
    }
    if (label) {
      label.textContent = 'API: Offline (Port 8000)';
    }
    if (stripZeroSum) {
      stripZeroSum.textContent = 'Σ = --';
      stripZeroSum.style.color = 'var(--text-muted)';
    }
  }
}

// Initial Setup
window.addEventListener('DOMContentLoaded', () => {
  window.addEventListener('hashchange', handleRouting);
  handleRouting();

  // Initial health check and recurrent 5-second interval
  checkSystemHealth();
  setInterval(checkSystemHealth, 5000);

  // Global Header Quick Actions
  const btnSeed = document.getElementById('btn-seed-data');
  if (btnSeed) {
    btnSeed.onclick = async () => {
      btnSeed.disabled = true;
      try {
        toast.info('Seeding Ledger Data...', 'Initializing benchmark wallets & transactions');
        await api.seedDemoData();
        toast.success('Ledger Seeded!', '4 Wallets and 3 atomic transfers created.');
        handleRouting();
      } catch (err) {
        toast.error('Seeding Failed', err.message);
      } finally {
        btnSeed.disabled = false;
      }
    };
  }

  const btnQuickTransfer = document.getElementById('btn-quick-transfer');
  if (btnQuickTransfer) {
    btnQuickTransfer.onclick = () => {
      window.location.hash = '#transfer';
    };
  }

  // Keyboard shortcut: Escape closes modal
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      modal.close();
    }
  });
});

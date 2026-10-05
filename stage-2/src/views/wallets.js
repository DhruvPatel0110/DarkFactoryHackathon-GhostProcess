/**
 * GhostProcess Wallets Grid View
 */
import { api } from '../api.js';
import { toast } from '../components/toast.js';
import { showCreateWalletModal } from './dashboard.js';

export async function renderWallets(root) {
  root.innerHTML = `
    <div class="view-loading-skeleton">
      <div class="shimmer-block" style="height: 60px; margin-bottom: 24px;"></div>
      <div class="shimmer-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
        <div class="shimmer-block" style="height: 180px;"></div>
        <div class="shimmer-block" style="height: 180px;"></div>
        <div class="shimmer-block" style="height: 180px;"></div>
      </div>
    </div>
  `;

  try {
    const wallets = await api.listWallets();

    root.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: var(--space-4); margin-bottom: var(--space-6);">
        <div>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span class="badge badge-accent">WALLETS REPOSITORY</span>
            <span class="badge badge-muted">${wallets.length} ACCOUNTS</span>
          </div>
          <h1>System Wallets</h1>
          <p>Every wallet balance is strictly derived from its underlying journal entries.</p>
        </div>
        <div style="display: flex; gap: var(--space-3); align-items: center;">
          <div style="position: relative; width: 260px;">
            <input type="text" id="wallets-search" placeholder="Search by name or UUID..." style="padding-left: 36px;">
            <svg style="position: absolute; left: 12px; top: 12px; color: var(--text-muted);" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </div>
          <button class="btn btn-primary" id="btn-open-create-wallet">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            <span>Create Wallet</span>
          </button>
        </div>
      </div>

      <div id="wallets-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: var(--space-5);">
        ${renderWalletCards(wallets)}
      </div>
    `;

    // Bind Search Filter
    const searchInput = document.getElementById('wallets-search');
    if (searchInput) {
      searchInput.oninput = () => {
        const query = searchInput.value.toLowerCase().trim();
        const filtered = wallets.filter(w => 
          (w.name && w.name.toLowerCase().includes(query)) ||
          w.id.toLowerCase().includes(query)
        );
        const grid = document.getElementById('wallets-grid');
        if (grid) grid.innerHTML = renderWalletCards(filtered);
        attachCardListeners();
      };
    }

    // Bind Create Button
    const createBtn = document.getElementById('btn-open-create-wallet');
    if (createBtn) {
      createBtn.onclick = () => {
        showCreateWalletModal(() => renderWallets(root));
      };
    }

    attachCardListeners();

  } catch (err) {
    root.innerHTML = `
      <div class="card" style="border-color: var(--error); text-align: center; padding: var(--space-8);">
        <h2>Failed to Load Wallets</h2>
        <p style="margin-top: 8px;">${err.message}</p>
        <button class="btn btn-secondary" style="margin-top: var(--space-4);" onclick="window.location.reload()">Retry</button>
      </div>
    `;
  }
}

function renderWalletCards(wallets) {
  if (wallets.length === 0) {
    return `
      <div class="card" style="grid-column: 1 / -1; text-align: center; padding: var(--space-12);">
        <h3 style="margin-bottom: 6px;">No Wallets Found</h3>
        <p style="margin-bottom: var(--space-4);">No active wallets matched your filter criteria or repository is empty.</p>
        <button class="btn btn-primary btn-sm" id="empty-create-btn">Create Your First Wallet</button>
      </div>
    `;
  }

  return wallets.map(w => {
    const balNum = parseFloat(w.balance || 0);
    const hasBalance = balNum > 0;
    return `
      <div class="card card-interactive" data-wallet-id="${w.id}">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-3);">
          <div>
            <h3 style="font-size: 1.1rem; color: var(--text-primary); margin-bottom: 2px;">
              ${escapeHtml(w.name || 'Unnamed Wallet')}
            </h3>
            <div style="display: flex; align-items: center; gap: 6px;">
              <span class="mono" style="font-size: 0.72rem; color: var(--text-muted);">${w.id.slice(0, 14)}...</span>
              <button class="btn-copy-id" data-copy="${w.id}" title="Copy Full UUID" style="background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 2px;">
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
              </button>
            </div>
          </div>
          <span class="badge ${hasBalance ? 'badge-success' : 'badge-muted'}">
            ${hasBalance ? 'FUNDED' : 'ZERO BAL'}
          </span>
        </div>

        <div style="background: var(--bg-primary); border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-4); margin-bottom: var(--space-4);">
          <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">Derived Balance</div>
          <div class="mono" style="font-size: 1.65rem; font-weight: 700; color: ${hasBalance ? 'var(--text-primary)' : 'var(--text-muted)'};">
            $${w.balance}
          </div>
        </div>

        <div style="display: flex; align-items: center; justify-content: space-between; gap: var(--space-2);">
          <a href="#wallet/${w.id}" class="btn btn-secondary btn-sm" style="flex: 1;">
            Detail History
          </a>
          <a href="#transfer?from=${w.id}" class="btn btn-primary btn-sm" style="flex: 1;">
            Send Funds
          </a>
        </div>
      </div>
    `;
  }).join('');
}

function attachCardListeners() {
  document.querySelectorAll('.btn-copy-id').forEach(btn => {
    btn.onclick = (e) => {
      e.stopPropagation();
      const val = btn.getAttribute('data-copy');
      navigator.clipboard.writeText(val);
      toast.info('Copied to Clipboard', `UUID: ${val}`);
    };
  });

  const emptyCreate = document.getElementById('empty-create-btn');
  if (emptyCreate) {
    emptyCreate.onclick = () => showCreateWalletModal();
  }
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

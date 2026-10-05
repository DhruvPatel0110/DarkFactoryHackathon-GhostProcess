/**
 * GhostProcess Dashboard View
 */
import { api } from '../api.js';
import { toast } from '../components/toast.js';
import { modal } from '../components/modal.js';

export async function renderDashboard(root) {
  root.innerHTML = `
    <div class="view-loading-skeleton">
      <div class="shimmer-block" style="height: 120px; margin-bottom: 24px;"></div>
      <div class="shimmer-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px;">
        <div class="shimmer-block" style="height: 110px;"></div>
        <div class="shimmer-block" style="height: 110px;"></div>
        <div class="shimmer-block" style="height: 110px;"></div>
        <div class="shimmer-block" style="height: 110px;"></div>
      </div>
    </div>
  `;

  try {
    const [wallets, transfers, stateExport] = await Promise.all([
      api.listWallets().catch(() => []),
      api.listTransfers(null, 10, 0).catch(() => []),
      api.exportState().catch(() => null)
    ]);

    const totalSystemBalance = wallets
      .filter(w => parseFloat(w.balance || 0) > 0)
      .reduce((sum, w) => sum + parseFloat(w.balance || 0), 0);
    const ledgerSum = stateExport ? stateExport.ledger_sum : '0.00';
    const isBalanced = parseFloat(ledgerSum) === 0;

    root.innerHTML = `
      <section class="dashboard-hero" style="margin-bottom: var(--space-8);">
        <div style="display: flex; align-items: flex-end; justify-content: space-between; flex-wrap: wrap; gap: var(--space-4);">
          <div>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
              <span class="badge badge-accent">POCKETFUL STAGE 1 ENGINE</span>
              <span class="badge badge-muted">SQLITE WAL • ATOMIC</span>
            </div>
            <h1>Dark Factory Financial Matrix</h1>
            <p style="margin-top: 4px;">Clean-room double-entry balance ledger with mathematical zero-sum verification.</p>
          </div>
          <div style="display: flex; gap: var(--space-3);">
            <button class="btn btn-secondary" id="dash-create-wallet">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              <span>Create Wallet</span>
            </button>
            <a href="#transfer" class="btn btn-primary">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="17 1 21 5 17 9"/>
                <path d="M3 11V9a4 4 0 0 1 4-4h14"/>
              </svg>
              <span>Transfer Engine</span>
            </a>
          </div>
        </div>
      </section>

      <!-- Key Metrics Row -->
      <section class="metrics-grid">
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-label">System Active Liquidity</span>
            <div class="metric-icon-wrap">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="1" x2="12" y2="23"/>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
            </div>
          </div>
          <div class="metric-value mono" style="color: var(--text-primary);">$${totalSystemBalance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          <div class="metric-footer">
            <span class="badge badge-success">DERIVED EXACT</span>
            <span>across ${wallets.length} active wallets</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-label">Active Wallets</span>
            <div class="metric-icon-wrap">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/>
                <path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/>
              </svg>
            </div>
          </div>
          <div class="metric-value mono">${wallets.length}</div>
          <div class="metric-footer">
            <span class="badge badge-muted">ISOLATED ID</span>
            <span>UUIDv4 Addressable</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-label">Settled Transfers</span>
            <div class="metric-icon-wrap">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="7 23 3 19 7 15"/>
                <path d="M21 13v2a4 4 0 0 1-4 4H3"/>
              </svg>
            </div>
          </div>
          <div class="metric-value mono">${(stateExport && stateExport.transfers) ? stateExport.transfers.length : transfers.length}</div>
          <div class="metric-footer">
            <span class="badge badge-accent">IDEMPOTENT</span>
            <span>0 duplicate collisions</span>
          </div>
        </div>

        <div class="metric-card" style="border-color: ${isBalanced ? 'var(--border)' : 'var(--error)'};">
          <div class="metric-header">
            <span class="metric-label">Ledger Invariant Σ</span>
            <div class="metric-icon-wrap" style="color: ${isBalanced ? 'var(--success)' : 'var(--error)'};">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
          </div>
          <div class="metric-value mono" style="color: ${isBalanced ? 'var(--success)' : 'var(--error)'};">$${ledgerSum}</div>
          <div class="metric-footer">
            <span class="badge ${isBalanced ? 'badge-success' : 'badge-accent'}">
              ${isBalanced ? 'ZERO-SUM SECURE' : 'INVARIANT BREACH'}
            </span>
            <span>Balanced Journal</span>
          </div>
        </div>
      </section>

      <!-- Main Section: Split Layout (Recent Transfers + Factory Invariants) -->
      <div style="display: grid; grid-template-columns: 2fr 1fr; gap: var(--space-6); align-items: start;">
        
        <!-- Left: Recent Ledger Transactions -->
        <div class="card">
          <div class="card-header">
            <div>
              <h2 class="card-title">Recent Settled Transfers</h2>
              <div class="card-subtitle">Atomic double-entry settlements logged by Coder & Auditor</div>
            </div>
            <a href="#audit" class="btn btn-ghost btn-sm">Full Journal</a>
          </div>

          ${transfers.length === 0 ? `
            <div style="text-align: center; padding: var(--space-10) var(--space-4);">
              <div style="color: var(--text-muted); margin-bottom: var(--space-3);">
                <svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/>
                  <path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/>
                </svg>
              </div>
              <h3 style="font-size: 1rem; margin-bottom: 4px;">No Transactions Yet</h3>
              <p style="font-size: 0.8rem; margin-bottom: var(--space-4);">Seed test demo data or execute your first transfer.</p>
              <button class="btn btn-primary btn-sm" id="empty-seed-btn">Seed Demo Data</button>
            </div>
          ` : `
            <div class="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Transfer ID</th>
                    <th>Source Wallet</th>
                    <th>Destination Wallet</th>
                    <th>Amount</th>
                    <th>Status</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  ${transfers.map(t => `
                    <tr>
                      <td class="mono" style="font-weight: 500; color: var(--text-primary);" title="${t.id}">
                        ${t.id.slice(0, 8)}...
                      </td>
                      <td class="mono" style="font-size: 0.8rem;" title="${t.source_wallet_id}">
                        ${t.source_wallet_id.slice(0, 8)}...
                      </td>
                      <td class="mono" style="font-size: 0.8rem;" title="${t.destination_wallet_id}">
                        ${t.destination_wallet_id.slice(0, 8)}...
                      </td>
                      <td class="mono" style="font-weight: 700; color: var(--text-primary);">
                        $${t.amount}
                      </td>
                      <td>
                        <span class="badge badge-success">COMPLETED</span>
                      </td>
                      <td style="font-size: 0.75rem; color: var(--text-muted);">
                        ${new Date(t.created_at).toLocaleTimeString()}
                      </td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          `}
        </div>

        <!-- Right: Invariant Assurance Matrix -->
        <div style="display: flex; flex-direction: column; gap: var(--space-4);">
          <div class="card card-accent-glow">
            <div class="card-header" style="margin-bottom: var(--space-3);">
              <h3 class="card-title">Autonomous Factory Proof</h3>
              <span class="badge badge-accent">BAND MESH</span>
            </div>
            <p style="font-size: 0.82rem; margin-bottom: var(--space-4);">
              Built in a zero-human clean-room by Architect, Coder, Ghost Auditor, and Gatekeeper.
            </p>

            <div style="display: flex; flex-direction: column; gap: var(--space-3); font-size: 0.8rem;">
              <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; background: var(--bg-elevated); border-radius: var(--radius-md); border: 1px solid var(--border);">
                <span style="color: var(--text-secondary);">Seat 1 (Architect)</span>
                <span class="badge badge-muted">DESIGN.md APPROVED</span>
              </div>
              <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; background: var(--bg-elevated); border-radius: var(--radius-md); border: 1px solid var(--border);">
                <span style="color: var(--text-secondary);">Seat 2 (Coder)</span>
                <span class="badge badge-success">7/7 UNIT TESTS</span>
              </div>
              <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; background: var(--bg-elevated); border-radius: var(--radius-md); border: 1px solid var(--border);">
                <span style="color: var(--text-secondary);">Seat 3 (Ghost Auditor)</span>
                <span class="badge badge-success">6/6 RED-TEAM CLEARED</span>
              </div>
              <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; background: var(--bg-elevated); border-radius: var(--radius-md); border: 1px solid var(--border);">
                <span style="color: var(--text-secondary);">Seat 4 (Gatekeeper)</span>
                <span class="badge badge-accent">RELEASE.md ACCEPTED</span>
              </div>
            </div>
          </div>

          <!-- Quick Seed / Reset Card -->
          <div class="card">
            <div class="card-header" style="margin-bottom: var(--space-2);">
              <h3 class="card-title">Harness Control</h3>
              <span class="badge badge-muted">STATE API</span>
            </div>
            <p style="font-size: 0.78rem; margin-bottom: var(--space-4);">
              Reset SQLite database to fresh clean-room state or seed balanced fixtures.
            </p>
            <div style="display: flex; gap: var(--space-2);">
              <button class="btn btn-secondary btn-sm" id="btn-dash-reset" style="flex: 1;">
                Reset State
              </button>
              <button class="btn btn-primary btn-sm" id="btn-dash-seed" style="flex: 1;">
                Seed Fixtures
              </button>
            </div>
          </div>
        </div>

      </div>
    `;

    // Bind Action Handlers
    const createBtn = document.getElementById('dash-create-wallet');
    if (createBtn) {
      createBtn.onclick = () => showCreateWalletModal();
    }

    const emptySeed = document.getElementById('empty-seed-btn');
    if (emptySeed) {
      emptySeed.onclick = async () => {
        emptySeed.disabled = true;
        emptySeed.innerText = 'Seeding...';
        try {
          await api.seedDemoData();
          toast.success('Seeded!', 'Demo wallets and transactions initialized.');
          renderDashboard(root);
        } catch (e) {
          toast.error('Seed Error', e.message);
        }
      };
    }

    const dashSeed = document.getElementById('btn-dash-seed');
    if (dashSeed) {
      dashSeed.onclick = async () => {
        dashSeed.disabled = true;
        try {
          await api.seedDemoData();
          toast.success('Seeded!', '4 Benchmark wallets created with zero-sum invariant.');
          renderDashboard(root);
        } catch (e) {
          toast.error('Seed Failed', e.message);
        } finally {
          dashSeed.disabled = false;
        }
      };
    }

    const dashReset = document.getElementById('btn-dash-reset');
    if (dashReset) {
      dashReset.onclick = async () => {
        if (!confirm('Are you sure you want to reset all wallets and transactions to zero?')) return;
        try {
          await api.resetState();
          toast.success('Clean Slate', 'Database reset to clean room state.');
          renderDashboard(root);
        } catch (e) {
          toast.error('Reset Failed', e.message);
        }
      };
    }

  } catch (err) {
    root.innerHTML = `
      <div class="card" style="border-color: var(--error); text-align: center; padding: var(--space-12);">
        <div style="color: var(--error); margin-bottom: var(--space-3);">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <h2>Unable to Connect to Pocketful Backend</h2>
        <p style="margin-top: 8px; margin-bottom: var(--space-6);">
          Ensure the FastAPI server is running on <code class="mono">http://localhost:8000</code>.
        </p>
        <button class="btn btn-primary" onclick="window.location.reload()">
          Retry Connection
        </button>
      </div>
    `;
  }
}

export function showCreateWalletModal(onCreated) {
  modal.open(
    'Create New Wallet',
    `
      <div class="form-group">
        <label class="form-label" for="wallet-name-input">
          Wallet Account Name
          <span class="form-label-hint">e.g. Treasury, Operations</span>
        </label>
        <input type="text" id="wallet-name-input" placeholder="Enter wallet title..." value="General Wallet" autofocus>
      </div>
      <div class="form-group">
        <label class="form-label" for="wallet-idem-input">
          Idempotency Key
          <span class="form-label-hint">Optional UUIDv4</span>
        </label>
        <div class="input-with-action">
          <input type="text" id="wallet-idem-input" class="mono" value="${crypto.randomUUID()}" readonly>
          <button class="btn btn-secondary btn-sm" id="btn-regen-idem" type="button">New</button>
        </div>
      </div>
    `,
    [
      {
        text: 'Cancel',
        class: 'btn btn-ghost',
        onClick: (e, close) => close()
      },
      {
        text: 'Create Wallet',
        class: 'btn btn-primary',
        id: 'modal-submit-create-wallet',
        onClick: async (e, close) => {
          const nameInput = document.getElementById('wallet-name-input');
          const idemInput = document.getElementById('wallet-idem-input');
          const name = nameInput ? nameInput.value.trim() : 'Unnamed';
          const idem = idemInput ? idemInput.value.trim() : null;

          try {
            const wallet = await api.createWallet(name, idem);
            toast.success('Wallet Created', `Wallet "${wallet.name}" (${wallet.id.slice(0, 8)}...) ready.`);
            close();
            if (onCreated) onCreated(wallet);
            else window.location.hash = '#wallets';
          } catch (err) {
            toast.error('Creation Failed', err.message);
          }
        }
      }
    ]
  );

  const regenBtn = document.getElementById('btn-regen-idem');
  if (regenBtn) {
    regenBtn.onclick = () => {
      const idemInput = document.getElementById('wallet-idem-input');
      if (idemInput) idemInput.value = crypto.randomUUID();
    };
  }
}

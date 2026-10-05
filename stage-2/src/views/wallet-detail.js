/**
 * GhostProcess Wallet Detail View
 */
import { api } from '../api.js';
import { toast } from '../components/toast.js';

export async function renderWalletDetail(root, walletId) {
  root.innerHTML = `
    <div class="view-loading-skeleton">
      <div class="shimmer-block" style="height: 180px; margin-bottom: 24px;"></div>
      <div class="shimmer-block" style="height: 320px;"></div>
    </div>
  `;

  try {
    const [wallet, transfers, stateExport] = await Promise.all([
      api.getWallet(walletId),
      api.listTransfers(walletId, 50, 0),
      api.exportState().catch(() => null)
    ]);

    // Filter journal entries for this wallet
    const journalEntries = (stateExport && stateExport.journal_entries)
      ? stateExport.journal_entries.filter(e => e.wallet_id === walletId)
      : [];

    let totalCredits = 0;
    let totalDebits = 0;
    journalEntries.forEach(e => {
      const amt = parseFloat(e.amount);
      if (amt >= 0) totalCredits += amt;
      else totalDebits += Math.abs(amt);
    });

    root.innerHTML = `
      <div style="margin-bottom: var(--space-6);">
        <a href="#wallets" class="btn btn-ghost btn-sm" style="margin-bottom: var(--space-4);">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="19" y1="12" x2="5" y2="12"/>
            <polyline points="12 19 5 12 12 5"/>
          </svg>
          <span>Back to Wallets</span>
        </a>

        <!-- Hero Card -->
        <div class="card" style="border-left: 4px solid var(--accent); padding: var(--space-8);">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: var(--space-4);">
            <div>
              <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                <span class="badge badge-accent">WALLET ACCOUNT</span>
                <span class="mono" style="font-size: 0.75rem; color: var(--text-muted);">${wallet.id}</span>
              </div>
              <h1 style="font-size: 2rem; margin-bottom: 4px;">${wallet.name || 'Unnamed Wallet'}</h1>
              <div style="font-size: 0.78rem; color: var(--text-muted);">
                Created: ${new Date(wallet.created_at).toLocaleString()}
              </div>
            </div>

            <div style="text-align: right;">
              <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Current Balance</div>
              <div class="mono" style="font-size: 2.5rem; font-weight: 800; color: var(--text-primary); line-height: 1.1;">
                $${wallet.balance}
              </div>
              <div style="display: flex; gap: var(--space-2); margin-top: var(--space-3); justify-content: flex-end;">
                <a href="#transfer?from=${wallet.id}" class="btn btn-primary btn-sm">
                  Send From Here
                </a>
                <a href="#transfer?to=${wallet.id}" class="btn btn-secondary btn-sm">
                  Receive Here
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Metrics Breakdown -->
      <div class="metrics-grid" style="grid-template-columns: repeat(3, 1fr); margin-bottom: var(--space-8);">
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-label">Cumulative Credits</span>
            <div class="metric-icon-wrap" style="color: var(--success);">+</div>
          </div>
          <div class="metric-value mono" style="color: var(--success); font-size: 1.5rem;">
            +$${totalCredits.toFixed(2)}
          </div>
          <div class="metric-footer">Incoming value</div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-label">Cumulative Debits</span>
            <div class="metric-icon-wrap" style="color: var(--accent);">-</div>
          </div>
          <div class="metric-value mono" style="color: var(--accent); font-size: 1.5rem;">
            -$${totalDebits.toFixed(2)}
          </div>
          <div class="metric-footer">Outgoing value</div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-label">Journal Entries Count</span>
            <div class="metric-icon-wrap">#</div>
          </div>
          <div class="metric-value mono" style="font-size: 1.5rem;">
            ${journalEntries.length}
          </div>
          <div class="metric-footer">Ledger transaction rows</div>
        </div>
      </div>

      <!-- Ledger Journal Entries Section -->
      <div class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Underlying Double-Entry Journal</h2>
            <div class="card-subtitle">Every balance calculation is derived from these atomic ledger postings</div>
          </div>
          <span class="badge badge-muted">${journalEntries.length} ENTRIES</span>
        </div>

        ${journalEntries.length === 0 ? `
          <div style="text-align: center; padding: var(--space-10) var(--space-4); color: var(--text-muted);">
            <p>No journal entries registered for this wallet yet.</p>
          </div>
        ` : `
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Entry ID</th>
                  <th>Transaction Ref</th>
                  <th>Entry Type</th>
                  <th>Signed Amount</th>
                  <th>Recorded At</th>
                </tr>
              </thead>
              <tbody>
                ${journalEntries.map(e => {
                  const isCredit = e.entry_type === 'CREDIT' || parseFloat(e.amount) >= 0;
                  return `
                    <tr>
                      <td class="mono" style="font-size: 0.8rem; color: var(--text-muted);">${e.id || 'N/A'}</td>
                      <td class="mono" style="font-size: 0.8rem; color: var(--text-primary); font-weight: 500;">
                        ${e.transaction_id}
                      </td>
                      <td>
                        <span class="badge ${isCredit ? 'badge-success' : 'badge-accent'}">
                          ${e.entry_type}
                        </span>
                      </td>
                      <td class="mono ${isCredit ? 'entry-credit' : 'entry-debit'}" style="font-weight: 700; font-size: 0.95rem;">
                        ${parseFloat(e.amount) > 0 ? `+${e.amount}` : e.amount}
                      </td>
                      <td style="font-size: 0.78rem; color: var(--text-muted);">
                        ${new Date(e.created_at).toLocaleString()}
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>
        `}
      </div>
    `;

  } catch (err) {
    root.innerHTML = `
      <div class="card" style="border-color: var(--error); text-align: center; padding: var(--space-8);">
        <h2>Wallet Not Found</h2>
        <p style="margin-top: 8px;">${err.message}</p>
        <a href="#wallets" class="btn btn-secondary" style="margin-top: var(--space-4);">Return to Wallets</a>
      </div>
    `;
  }
}

/**
 * GhostProcess Zero-Sum Audit Log View
 * The primary mathematical proof center for the Dark Factory
 */
import { api } from '../api.js';
import { toast } from '../components/toast.js';

export async function renderAudit(root) {
  root.innerHTML = `
    <div class="view-loading-skeleton">
      <div class="shimmer-block" style="height: 160px; margin-bottom: 24px;"></div>
      <div class="shimmer-block" style="height: 400px;"></div>
    </div>
  `;

  try {
    const stateExport = await api.exportState();
    const journal = stateExport.journal_entries || [];
    const ledgerSum = stateExport.ledger_sum || '0.00';
    const isZeroSum = parseFloat(ledgerSum) === 0;

    let debitsTotal = 0;
    let creditsTotal = 0;
    journal.forEach(entry => {
      const amt = parseFloat(entry.amount);
      if (amt < 0) debitsTotal += Math.abs(amt);
      else creditsTotal += amt;
    });

    root.innerHTML = `
      <div style="margin-bottom: var(--space-6);">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: var(--space-4);">
          <div>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
              <span class="badge badge-accent">INVARIANT ASSURANCE</span>
              <span class="badge badge-muted">GHOST AUDITOR RED-TEAM PROOF</span>
            </div>
            <h1>Zero-Sum Double-Entry Ledger</h1>
            <p>Every transaction balance change must sum strictly to 0.00 across all system wallets.</p>
          </div>

          <div style="display: flex; gap: var(--space-3);">
            <button class="btn btn-secondary" id="btn-verify-invariant">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <polyline points="9 12 11 14 15 10"/>
              </svg>
              <span>Recalculate Invariant</span>
            </button>
            <button class="btn btn-primary" id="btn-export-json">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              <span>Export Raw State JSON</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Hero Zero-Sum Invariant Monitor -->
      <div class="card" style="border: 2px solid ${isZeroSum ? 'rgba(22, 163, 74, 0.4)' : 'var(--error)'}; background: #0c0f0d; margin-bottom: var(--space-8); padding: var(--space-8);">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: var(--space-6);">
          
          <div style="display: flex; align-items: center; gap: var(--space-5);">
            <div style="width: 56px; height: 56px; border-radius: var(--radius-lg); background: ${isZeroSum ? 'rgba(22, 163, 74, 0.15)' : 'rgba(220, 38, 38, 0.15)'}; border: 1px solid ${isZeroSum ? 'var(--success)' : 'var(--error)'}; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 25px ${isZeroSum ? 'var(--success-glow)' : 'var(--accent-glow)'};">
              <svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="${isZeroSum ? 'var(--success)' : 'var(--error)'}" stroke-width="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                ${isZeroSum ? '<polyline points="9 12 11 14 15 10"/>' : '<line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>'}
              </svg>
            </div>
            <div>
              <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: ${isZeroSum ? 'var(--success)' : 'var(--error)'}; font-weight: 700;">
                ${isZeroSum ? 'GLOBAL ZERO-SUM INVARIANT HOLDS' : 'CRITICAL INVARIANT BREACH'}
              </div>
              <h2 style="font-size: 1.85rem; margin-top: 2px;">
                Σ(All Journal Postings) = <span class="mono" style="color: ${isZeroSum ? 'var(--success)' : 'var(--error)'};">$${ledgerSum}</span>
              </h2>
              <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px;">
                Verified across ${journal.length} entries & ${stateExport.wallets ? stateExport.wallets.length : 0} wallets.
              </div>
            </div>
          </div>

          <!-- Formula Matrix -->
          <div style="display: flex; gap: var(--space-4); background: #080808; padding: var(--space-4) var(--space-6); border-radius: var(--radius-md); border: 1px solid var(--border);">
            <div style="text-align: right;">
              <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Total Credits (+)</div>
              <div class="mono entry-credit" style="font-size: 1.15rem; font-weight: 700;">
                +$${creditsTotal.toFixed(2)}
              </div>
            </div>
            <div style="font-size: 1.2rem; color: var(--text-muted); display: flex; align-items: center;">-</div>
            <div style="text-align: right;">
              <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Total Debits (-)</div>
              <div class="mono entry-debit" style="font-size: 1.15rem; font-weight: 700;">
                $${debitsTotal.toFixed(2)}
              </div>
            </div>
            <div style="font-size: 1.2rem; color: var(--text-muted); display: flex; align-items: center;">=</div>
            <div style="text-align: right;">
              <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Net Delta</div>
              <div class="mono" style="font-size: 1.15rem; font-weight: 800; color: var(--success);">
                $${ledgerSum}
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- Journal Table Card -->
      <div class="card">
        <div class="card-header" style="flex-wrap: wrap; gap: var(--space-4);">
          <div>
            <h2 class="card-title">Atomic Double-Entry Journal</h2>
            <div class="card-subtitle">Complete chronological record of debits and credits</div>
          </div>

          <!-- Table Filters -->
          <div style="display: flex; gap: var(--space-2); align-items: center;">
            <select id="audit-filter-type" style="width: auto; padding: 6px 12px; font-size: 0.8rem;">
              <option value="ALL">All Entries (${journal.length})</option>
              <option value="CREDIT">Credits Only</option>
              <option value="DEBIT">Debits Only</option>
            </select>
            <input type="text" id="audit-search" placeholder="Filter transaction ref..." style="width: 200px; padding: 6px 12px; font-size: 0.8rem;">
          </div>
        </div>

        ${journal.length === 0 ? `
          <div style="text-align: center; padding: var(--space-12) var(--space-4); color: var(--text-muted);">
            <h3>Ledger is Currently Empty</h3>
            <p style="margin-top: 4px;">Seed sample fixtures or make transfers to populate journal entries.</p>
          </div>
        ` : `
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Entry UUID</th>
                  <th>Transaction ID</th>
                  <th>Target Wallet</th>
                  <th>Type</th>
                  <th>Signed Amount</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody id="journal-table-body">
                ${renderJournalRows(journal)}
              </tbody>
            </table>
          </div>
        `}
      </div>
    `;

    // Filter and Search
    const filterSelect = document.getElementById('audit-filter-type');
    const searchInput = document.getElementById('audit-search');

    function applyFilters() {
      const type = filterSelect ? filterSelect.value : 'ALL';
      const q = searchInput ? searchInput.value.toLowerCase().trim() : '';

      const filtered = journal.filter(e => {
        const matchesType = type === 'ALL' || e.entry_type === type;
        const matchesSearch = !q || 
          (e.transaction_id && e.transaction_id.toLowerCase().includes(q)) ||
          (e.wallet_id && e.wallet_id.toLowerCase().includes(q)) ||
          (e.id && e.id.toLowerCase().includes(q));
        return matchesType && matchesSearch;
      });

      const tbody = document.getElementById('journal-table-body');
      if (tbody) tbody.innerHTML = renderJournalRows(filtered);
    }

    if (filterSelect) filterSelect.onchange = applyFilters;
    if (searchInput) searchInput.oninput = applyFilters;

    // Recalculate Button
    const verifyBtn = document.getElementById('btn-verify-invariant');
    if (verifyBtn) {
      verifyBtn.onclick = async () => {
        verifyBtn.disabled = true;
        try {
          const fresh = await api.exportState();
          const freshSum = fresh.ledger_sum;
          if (parseFloat(freshSum) === 0) {
            toast.success('Zero-Sum Verified!', `Sum of ${fresh.journal_entries.length} entries = exactly $0.00.`);
          } else {
            toast.error('Invariant Failure', `Ledger sum is unbalanced: $${freshSum}`);
          }
          renderAudit(root);
        } catch (e) {
          toast.error('Audit Error', e.message);
        } finally {
          verifyBtn.disabled = false;
        }
      };
    }

    // Export Raw JSON
    const exportBtn = document.getElementById('btn-export-json');
    if (exportBtn) {
      exportBtn.onclick = () => {
        const blob = new Blob([JSON.stringify(stateExport, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ghostprocess-ledger-audit-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        toast.info('Exported State JSON', 'Saved snapshot of all wallets, transfers & journals.');
      };
    }

  } catch (err) {
    root.innerHTML = `
      <div class="card" style="border-color: var(--error); text-align: center; padding: var(--space-8);">
        <h2>Unable to Fetch Audit Records</h2>
        <p style="margin-top: 8px;">${err.message}</p>
        <button class="btn btn-secondary" style="margin-top: var(--space-4);" onclick="window.location.reload()">Retry</button>
      </div>
    `;
  }
}

function renderJournalRows(entries) {
  if (entries.length === 0) {
    return `
      <tr>
        <td colspan="6" style="text-align: center; padding: var(--space-6); color: var(--text-muted);">
          No journal entries matched filter criteria.
        </td>
      </tr>
    `;
  }

  return entries.map(e => {
    const isCredit = e.entry_type === 'CREDIT' || parseFloat(e.amount) >= 0;
    return `
      <tr>
        <td class="mono" style="font-size: 0.78rem; color: var(--text-muted);">${e.id || 'AUTO'}</td>
        <td class="mono" style="font-size: 0.8rem; font-weight: 600; color: var(--text-primary);">${e.transaction_id}</td>
        <td class="mono" style="font-size: 0.78rem;" title="${e.wallet_id}">
          <a href="#wallet/${e.wallet_id}" style="color: var(--text-secondary); text-decoration: none;">
            ${e.wallet_id.slice(0, 10)}...
          </a>
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
  }).join('');
}

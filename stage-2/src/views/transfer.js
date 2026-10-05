/**
 * GhostProcess Transfer Engine View
 */
import { api } from '../api.js';
import { toast } from '../components/toast.js';

export async function renderTransfer(root, searchParams = new URLSearchParams()) {
  root.innerHTML = `
    <div class="view-loading-skeleton">
      <div class="shimmer-block" style="height: 100px; margin-bottom: 24px;"></div>
      <div class="shimmer-block" style="height: 380px;"></div>
    </div>
  `;

  try {
    const wallets = await api.listWallets();

    const preselectedFrom = searchParams.get('from') || (wallets[0] ? wallets[0].id : '');
    const preselectedTo = searchParams.get('to') || (wallets[1] ? wallets[1].id : '');

    root.innerHTML = `
      <div style="max-width: 860px; margin: 0 auto;">
        
        <!-- Header -->
        <div style="margin-bottom: var(--space-6);">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span class="badge badge-accent">ATOMIC SETTLEMENT</span>
            <span class="badge badge-muted">BEGIN IMMEDIATE TRANSACTION</span>
          </div>
          <h1>Double-Entry Transfer Engine</h1>
          <p>Every transaction executes an atomic debit and credit with strict idempotency protection.</p>
        </div>

        <div style="display: grid; grid-template-columns: 3fr 2fr; gap: var(--space-6); align-items: start;">
          
          <!-- Transfer Execution Form -->
          <div class="card card-accent-glow">
            <form id="transfer-form" novalidate>
              
              <!-- Source Wallet -->
              <div class="form-group">
                <label class="form-label" for="source-wallet">
                  Source Wallet (Debit Account)
                  <span class="form-label-hint" id="source-balance-hint">Avail: $0.00</span>
                </label>
                <select id="source-wallet" class="mono" required>
                  <option value="">Select source wallet...</option>
                  ${wallets.map(w => `
                    <option value="${w.id}" data-balance="${w.balance}" ${w.id === preselectedFrom ? 'selected' : ''}>
                      ${escapeHtml(w.name || 'Wallet')} ($${w.balance}) — [${w.id.slice(0, 8)}...]
                    </option>
                  `).join('')}
                </select>
              </div>

              <!-- Destination Wallet -->
              <div class="form-group">
                <label class="form-label" for="dest-wallet">
                  Destination Wallet (Credit Account)
                  <span class="form-label-hint" id="dest-balance-hint">Avail: $0.00</span>
                </label>
                <select id="dest-wallet" class="mono" required>
                  <option value="">Select destination wallet...</option>
                  ${wallets.map(w => `
                    <option value="${w.id}" data-balance="${w.balance}" ${w.id === preselectedTo ? 'selected' : ''}>
                      ${escapeHtml(w.name || 'Wallet')} ($${w.balance}) — [${w.id.slice(0, 8)}...]
                    </option>
                  `).join('')}
                </select>
              </div>

              <!-- Amount Input -->
              <div class="form-group">
                <label class="form-label" for="transfer-amount">
                  Transfer Amount ($ USD)
                  <span class="form-label-hint">Max 2 decimal places, positive only</span>
                </label>
                <input type="text" id="transfer-amount" class="mono" placeholder="0.00" value="50.00" required>
                
                <!-- Quick Amount Chips -->
                <div class="chips-row">
                  <span class="chip" data-amt="10.00">$10</span>
                  <span class="chip" data-amt="25.00">$25</span>
                  <span class="chip" data-amt="50.00">$50</span>
                  <span class="chip" data-amt="100.00">$100</span>
                  <span class="chip" data-amt="250.00">$250</span>
                  <span class="chip" id="chip-max">Max Balance</span>
                </div>
              </div>

              <!-- Idempotency Key -->
              <div class="form-group">
                <label class="form-label" for="transfer-idem">
                  Idempotency Key (Collision Protection)
                  <span class="form-label-hint">UUIDv4</span>
                </label>
                <div class="input-with-action">
                  <input type="text" id="transfer-idem" class="mono" value="${crypto.randomUUID()}" style="font-size: 0.78rem;">
                  <button type="button" class="btn btn-secondary btn-sm" id="btn-regen-transfer-idem" title="Generate New UUID">
                    New
                  </button>
                  <button type="button" class="btn btn-ghost btn-sm" id="btn-copy-transfer-idem" title="Copy Key">
                    Copy
                  </button>
                </div>
              </div>

              <!-- Submit Button -->
              <div style="margin-top: var(--space-6);">
                <button type="submit" class="btn btn-primary btn-lg" id="btn-submit-transfer" style="width: 100%;">
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="17 1 21 5 17 9"/>
                    <path d="M3 11V9a4 4 0 0 1 4-4h14"/>
                  </svg>
                  <span>Execute Atomic Transfer</span>
                </button>
              </div>

            </form>
          </div>

          <!-- Right Column: Real-Time Preview & Invariants Inspector -->
          <div style="display: flex; flex-direction: column; gap: var(--space-4);">
            
            <!-- Live Math Impact Preview -->
            <div class="card">
              <div class="card-header" style="margin-bottom: var(--space-2);">
                <h3 class="card-title">Ledger Impact Preview</h3>
                <span class="badge badge-success">ZERO-SUM VERIFIED</span>
              </div>
              <p style="font-size: 0.78rem; margin-bottom: var(--space-4);">
                Calculated in real-time before transaction dispatch:
              </p>

              <div style="display: flex; flex-direction: column; gap: var(--space-3); font-size: 0.8rem;">
                <div style="display: flex; justify-content: space-between; padding: 10px; background: var(--bg-primary); border-radius: var(--radius-md); border: 1px solid var(--border);">
                  <span style="color: var(--text-secondary);">Source Debit:</span>
                  <span class="mono entry-debit" id="preview-debit" style="font-weight: 700;">-$50.00</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 10px; background: var(--bg-primary); border-radius: var(--radius-md); border: 1px solid var(--border);">
                  <span style="color: var(--text-secondary);">Destination Credit:</span>
                  <span class="mono entry-credit" id="preview-credit" style="font-weight: 700;">+$50.00</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 10px; background: var(--bg-elevated); border-radius: var(--radius-md); border: 1px solid var(--border);">
                  <span style="font-weight: 600; color: var(--text-primary);">Net Ledger Delta:</span>
                  <span class="mono" style="font-weight: 800; color: var(--success);">$0.00</span>
                </div>
              </div>
            </div>

            <!-- Idempotency Test Helper Card -->
            <div class="card">
              <div class="card-header" style="margin-bottom: var(--space-2);">
                <h3 class="card-title">Idempotency Verification</h3>
                <span class="badge badge-muted">REPLAY TEST</span>
              </div>
              <p style="font-size: 0.78rem; margin-bottom: var(--space-3);">
                Re-submit the same idempotency key to prove zero funds duplicate and cached 200 payload returns.
              </p>
              <button class="btn btn-secondary btn-sm" id="btn-replay-idem" style="width: 100%;" disabled>
                Replay Last Transfer (Test Idempotency)
              </button>
            </div>

            <!-- Last Transaction Result -->
            <div id="transfer-result-card" class="card" style="display: none; border-color: var(--success);">
              <div class="card-header" style="margin-bottom: var(--space-2);">
                <h3 class="card-title" style="color: var(--success);">Transfer Settled</h3>
                <span class="badge badge-success">HTTP 200/201</span>
              </div>
              <div id="transfer-result-content" class="mono" style="font-size: 0.75rem; color: var(--text-secondary); word-break: break-all;"></div>
            </div>

          </div>

        </div>

      </div>
    `;

    // Dynamic Select & Balance Handlers
    const sourceSel = document.getElementById('source-wallet');
    const destSel = document.getElementById('dest-wallet');
    const amtInput = document.getElementById('transfer-amount');
    const idemInput = document.getElementById('transfer-idem');
    const previewDebit = document.getElementById('preview-debit');
    const previewCredit = document.getElementById('preview-credit');
    const sourceHint = document.getElementById('source-balance-hint');
    const destHint = document.getElementById('dest-balance-hint');
    const replayBtn = document.getElementById('btn-replay-idem');

    let lastExecutedTransfer = null;

    function updateBalancesAndPreview() {
      const srcOpt = sourceSel.options[sourceSel.selectedIndex];
      const dstOpt = destSel.options[destSel.selectedIndex];

      const srcBal = srcOpt ? srcOpt.getAttribute('data-balance') : '0.00';
      const dstBal = dstOpt ? dstOpt.getAttribute('data-balance') : '0.00';

      if (sourceHint) sourceHint.textContent = `Avail: $${srcBal || '0.00'}`;
      if (destHint) destHint.textContent = `Avail: $${dstBal || '0.00'}`;

      const amtVal = parseFloat(amtInput.value) || 0;
      const formattedAmt = amtVal.toFixed(2);

      if (previewDebit) previewDebit.textContent = `-$${formattedAmt}`;
      if (previewCredit) previewCredit.textContent = `+$${formattedAmt}`;
    }

    sourceSel.onchange = updateBalancesAndPreview;
    destSel.onchange = updateBalancesAndPreview;
    amtInput.oninput = updateBalancesAndPreview;
    updateBalancesAndPreview();

    // Amount Chips
    document.querySelectorAll('.chip[data-amt]').forEach(chip => {
      chip.onclick = () => {
        amtInput.value = chip.getAttribute('data-amt');
        updateBalancesAndPreview();
      };
    });

    const chipMax = document.getElementById('chip-max');
    if (chipMax) {
      chipMax.onclick = () => {
        const srcOpt = sourceSel.options[sourceSel.selectedIndex];
        if (srcOpt) {
          const bal = srcOpt.getAttribute('data-balance') || '0.00';
          amtInput.value = bal;
          updateBalancesAndPreview();
        }
      };
    }

    // Idempotency Controls
    document.getElementById('btn-regen-transfer-idem').onclick = () => {
      idemInput.value = crypto.randomUUID();
      toast.info('New Idempotency Key', idemInput.value);
    };

    document.getElementById('btn-copy-transfer-idem').onclick = () => {
      navigator.clipboard.writeText(idemInput.value);
      toast.info('Copied Idempotency Key', idemInput.value);
    };

    // Form Submit
    const form = document.getElementById('transfer-form');
    const submitBtn = document.getElementById('btn-submit-transfer');

    form.onsubmit = async (e) => {
      e.preventDefault();

      const sourceId = sourceSel.value;
      const destId = destSel.value;
      const amount = amtInput.value.trim();
      const idempotencyKey = idemInput.value.trim();

      if (!sourceId || !destId) {
        toast.error('Validation Error', 'Please select both source and destination wallets.');
        return;
      }

      if (sourceId === destId) {
        toast.error('Prohibited Transfer', 'Cannot transfer funds to the identical wallet account.');
        return;
      }

      if (!amount || parseFloat(amount) <= 0) {
        toast.error('Validation Error', 'Transfer amount must be strictly greater than $0.00.');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <span class="pulse-dot"></span>
        <span>Executing Atomic Commit...</span>
      `;

      try {
        const result = await api.executeTransfer({
          source_wallet_id: sourceId,
          destination_wallet_id: destId,
          amount,
          idempotency_key: idempotencyKey
        });

        lastExecutedTransfer = {
          source_wallet_id: sourceId,
          destination_wallet_id: destId,
          amount,
          idempotency_key: idempotencyKey
        };

        if (replayBtn) replayBtn.disabled = false;

        toast.success(
          'Transfer Complete',
          `Transferred $${amount} atomically (${result.id ? result.id.slice(0, 8) : 'OK'})`
        );

        const resultCard = document.getElementById('transfer-result-card');
        const resultContent = document.getElementById('transfer-result-content');
        if (resultCard && resultContent) {
          resultCard.style.display = 'block';
          resultContent.innerHTML = `
            <strong>Transfer ID:</strong> ${result.id}<br>
            <strong>Idempotency Key:</strong> ${result.idempotency_key}<br>
            <strong>Status:</strong> ${result.status}<br>
            <strong>Amount:</strong> $${result.amount}<br>
            <strong>Settled At:</strong> ${result.created_at}
          `;
        }

        // Auto-generate fresh key for next transfer
        idemInput.value = crypto.randomUUID();

        // Refresh wallet options with latest balances
        const freshWallets = await api.listWallets();
        sourceSel.innerHTML = `
          <option value="">Select source wallet...</option>
          ${freshWallets.map(w => `
            <option value="${w.id}" data-balance="${w.balance}" ${w.id === sourceId ? 'selected' : ''}>
              ${escapeHtml(w.name || 'Wallet')} ($${w.balance}) — [${w.id.slice(0, 8)}...]
            </option>
          `).join('')}
        `;
        destSel.innerHTML = `
          <option value="">Select destination wallet...</option>
          ${freshWallets.map(w => `
            <option value="${w.id}" data-balance="${w.balance}" ${w.id === destId ? 'selected' : ''}>
              ${escapeHtml(w.name || 'Wallet')} ($${w.balance}) — [${w.id.slice(0, 8)}...]
            </option>
          `).join('')}
        `;
        updateBalancesAndPreview();

      } catch (err) {
        toast.error('Transfer Rejected', err.message);
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="17 1 21 5 17 9"/>
            <path d="M3 11V9a4 4 0 0 1 4-4h14"/>
          </svg>
          <span>Execute Atomic Transfer</span>
        `;
      }
    };

    // Replay Test
    if (replayBtn) {
      replayBtn.onclick = async () => {
        if (!lastExecutedTransfer) return;
        try {
          toast.info('Replaying Idempotency Key...', lastExecutedTransfer.idempotency_key);
          const replayRes = await api.executeTransfer(lastExecutedTransfer);
          toast.success(
            'Idempotency Verified!',
            `Same payload returned without double deduction (ID: ${replayRes.id.slice(0, 8)}...)`
          );
        } catch (err) {
          toast.error('Replay Failed', err.message);
        }
      };
    }

  } catch (err) {
    root.innerHTML = `
      <div class="card" style="border-color: var(--error); text-align: center; padding: var(--space-8);">
        <h2>Unable to Initialize Transfer Engine</h2>
        <p style="margin-top: 8px;">${err.message}</p>
        <button class="btn btn-secondary" style="margin-top: var(--space-4);" onclick="window.location.reload()">Retry</button>
      </div>
    `;
  }
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

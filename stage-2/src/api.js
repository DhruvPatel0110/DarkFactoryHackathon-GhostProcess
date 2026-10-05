/**
 * GhostProcess Pocketful API Client
 * Clean-Room communication with FastAPI Backend on port 8000
 */

export const DEFAULT_API_BASE = 'http://localhost:8000';

export function getApiBase() {
  return localStorage.getItem('ghostprocess_api_url') || DEFAULT_API_BASE;
}

export function setApiBase(url) {
  localStorage.setItem('ghostprocess_api_url', url);
}

async function request(path, options = {}) {
  const base = getApiBase();
  const url = `${base}${path}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  try {
    const res = await fetch(url, { ...options, headers });
    const contentType = res.headers.get('content-type') || '';
    let data;

    if (contentType.includes('application/json')) {
      data = await res.json();
    } else {
      data = await res.text();
    }

    if (!res.ok) {
      const err = new Error(
        (data && data.detail) ||
        (data && data.message) ||
        `HTTP ${res.status}: ${res.statusText}`
      );
      err.status = res.status;
      err.data = data;
      throw err;
    }

    return data;
  } catch (error) {
    if (error.status) throw error;
    // Network or connection refused error
    const netErr = new Error(`Connection error to ${base}: Ensure backend is running.`);
    netErr.status = 0;
    netErr.original = error;
    throw netErr;
  }
}

export const api = {
  // Health
  async getHealth() {
    return request('/health');
  },

  // Wallets
  async listWallets() {
    return request('/wallets');
  },

  async getWallet(walletId) {
    return request(`/wallets/${encodeURIComponent(walletId)}`);
  },

  async createWallet(name, idempotencyKey = null) {
    const body = { name };
    if (idempotencyKey) body.idempotency_key = idempotencyKey;
    return request('/wallets', {
      method: 'POST',
      body: JSON.stringify(body)
    });
  },

  // Transfers
  async executeTransfer({ source_wallet_id, destination_wallet_id, amount, idempotency_key }) {
    return request('/transfers', {
      method: 'POST',
      body: JSON.stringify({
        source_wallet_id,
        destination_wallet_id,
        amount,
        idempotency_key: idempotency_key || crypto.randomUUID()
      })
    });
  },

  async getTransfer(transferId) {
    return request(`/transfers/${encodeURIComponent(transferId)}`);
  },

  async listTransfers(walletId = null, limit = 50, offset = 0) {
    const params = new URLSearchParams({ limit, offset });
    if (walletId) params.append('wallet_id', walletId);
    return request(`/transfers?${params.toString()}`);
  },

  // State Management
  async exportState() {
    return request('/state/export');
  },

  async resetState() {
    return request('/state/reset', { method: 'POST' });
  },

  async importState(payload) {
    return request('/state/import', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  // Demo Seeder
  async seedDemoData() {
    // 1. Reset state to clean room
    await this.resetState();

    // 2. Create 4 benchmark wallets
    const wAlice = await this.createWallet("Alice Vault");
    const wBob = await this.createWallet("Bob Trading");
    const wCharlie = await this.createWallet("Charlie Liquidity");
    const wReserve = await this.createWallet("DarkFactory Reserve");

    // 3. Seed initial credit entries using state import for mathematical zero-sum setup
    // Initial balances: Reserve receives initial liquidity from external zero-sum journal entries
    const seedPayload = {
      wallets: [
        { id: wAlice.id, name: "Alice Vault" },
        { id: wBob.id, name: "Bob Trading" },
        { id: wCharlie.id, name: "Charlie Liquidity" },
        { id: wReserve.id, name: "DarkFactory Reserve" }
      ],
      journal_entries: [
        { transaction_id: "GENESIS-01", wallet_id: wReserve.id, amount: "-4500.00", entry_type: "DEBIT" },
        { transaction_id: "GENESIS-01", wallet_id: wAlice.id, amount: "1500.00", entry_type: "CREDIT" },
        { transaction_id: "GENESIS-01", wallet_id: wBob.id, amount: "1000.00", entry_type: "CREDIT" },
        { transaction_id: "GENESIS-01", wallet_id: wCharlie.id, amount: "2000.00", entry_type: "CREDIT" }
      ]
    };

    await this.importState(seedPayload);

    // 4. Perform live atomic transfers between wallets with idempotency keys
    await this.executeTransfer({
      source_wallet_id: wAlice.id,
      destination_wallet_id: wBob.id,
      amount: "150.00",
      idempotency_key: "demo-tx-001"
    });

    await this.executeTransfer({
      source_wallet_id: wCharlie.id,
      destination_wallet_id: wAlice.id,
      amount: "75.50",
      idempotency_key: "demo-tx-002"
    });

    await this.executeTransfer({
      source_wallet_id: wBob.id,
      destination_wallet_id: wReserve.id,
      amount: "25.00",
      idempotency_key: "demo-tx-003"
    });

    return {
      wallets: [wAlice, wBob, wCharlie, wReserve]
    };
  }
};

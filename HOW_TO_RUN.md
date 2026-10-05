# 🚀 How to Run GhostProcess
### Complete Step-by-Step Execution & Evaluation Guide

This guide is designed for hackathon judges and evaluators to test, audit, and run every layer of **GhostProcess** in under 2 minutes.

---

## ⚡ Quick Evaluation Matrix

| Goal | Command / Action | Time to Test |
| :--- | :--- | :--- |
| **Grade Docker Container** | `docker build` + `docker run --network none` | ~45 seconds |
| **Run All 13 Pytests** | `pytest stage-1/tests` & `stage-1/adversarial_tests` | ~5 seconds |
| **Launch Live Frontend UI** | `cd stage-2 && npm run dev` | ~15 seconds |
| **Re-Run Multi-Agent Factory** | `python agents/run_factory.py` | ~25 seconds |

---

## 🐳 Path 1: Running the Certified Backend Container (Zero-Network Safe)

Judges test the sealed Stage-1 container in complete offline isolation (`--network none`):

### 1. Build the Docker Image
```bash
docker build -t ghostprocess-pocketful stage-1
```

### 2. Run the Container in Sealed Isolation
```bash
docker run --rm -p 8000:8000 --network none ghostprocess-pocketful
```
*(The `--network none` flag strictly proves that the service runs autonomously with zero external network dependencies).*

### 3. Verify the Live Endpoints (In Another Terminal)

```bash
# 1. Health check (Returns 200 OK)
curl http://localhost:8000/health

# 2. Create Wallet A (Alice)
curl -X POST http://localhost:8000/wallets \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice Vault"}'

# 3. Create Wallet B (Bob)
curl -X POST http://localhost:8000/wallets \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob Trading"}'

# 4. Inspect the Global Ledger State & Zero-Sum Invariant
curl http://localhost:8000/state/export
```

---

## 🧪 Path 2: Running the Automated Test Suites (13/13 Passing)

The project includes **7 developer unit tests** (written by Seat 2: Coder) and **6 destructive adversarial tests** (written by Seat 3: Ghost Auditor).

### 1. Set Up Local Python Virtual Environment
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Developer Unit Tests (7/7 Passed)
```bash
pytest stage-1/tests -v
```
**Validates:** Wallet creation, derived balance computation, atomic transfers, self-transfer prohibition, sub-cent precision rejection (`10.001`), and idempotency replay.

### 3. Run the Blind Adversarial Red-Team Attacks (6/6 Cleared)
```bash
pytest stage-1/adversarial_tests -v
```
**Validates:** 10-thread simultaneous race conditions (double-spends), token collisions, scientific notation fuzzing, and global zero-sum ledger conservation ($\sum == 0.00$).

---

## 🖥️ Path 3: Running the Stage 2 Frontend UI (`stage-2/`)

GhostProcess includes a high-contrast Obsidian Black (`#0a0a0a`) and Crimson Red (`#dc2626`) web application.

### 1. Ensure Backend is Running on Port 8000
```bash
# In terminal 1:
python -m uvicorn app.main:app --app-dir stage-1 --host 127.0.0.1 --port 8000
```

### 2. Launch Vite Dev Server
```bash
# In terminal 2:
cd stage-2
npm install
npm run dev
```

### 3. Open Your Browser
Navigate to **`http://localhost:5173`**:
- **Click "Seed Demo"** in the top right to populate benchmark wallets with $4,500.00 circulating liquidity.
- **Go to "Wallets"** to inspect derived balances and click "Detail History".
- **Go to "Transfer Engine"** to execute atomic transfers and click **"Replay Last Transfer"** to verify idempotency protection in action.
- **Go to "Zero-Sum Audit"** to view the live $\sum = \$0.00$ invariant banner.

---

## 🤖 Path 4: Re-running the Full Autonomous Dark Factory

To watch all 4 seats (Architect, Coder, Ghost Auditor, Gatekeeper) negotiate, write code, attack, and certify in real-time:

### 1. Open BAND Desktop
- Launch **BAND Desktop**.
- Ensure the room `DarkFactory-GhostProcess` is active and you are signed in.

### 2. Configure Free AI Keys (Google AI Studio or Groq Cloud)
Create or check your `.env` file:
```env
GEMINI_API_KEY=your_free_gemini_key_here
GROQ_API_KEY=your_free_groq_key_here
```
*(Both providers have 100% free tiers with zero credit cards required).*

### 3. Dispatch Factory Run
```bash
python agents/run_factory.py
```
**What Happens Automatically:**
1. **Seat 1 (Architect)** ingests task $\to$ outputs [`DESIGN.md`](file:///e:/DarkFactory-GhostProcess/DESIGN.md) & [`WORK_ITEMS.md`](file:///e:/DarkFactory-GhostProcess/WORK_ITEMS.md) $\to$ tags `@Coder`.
2. **Seat 2 (Coder)** reads design $\to$ implements code in `stage-1/app/` $\to$ runs unit tests $\to$ writes [`HANDOFF.md`](file:///e:/DarkFactory-GhostProcess/HANDOFF.md) $\to$ tags `@Ghost-Auditor`.
3. **Seat 3 (Ghost Auditor)** executes blind attack vectors $\to$ writes [`AUDIT_REPORT.md`](file:///e:/DarkFactory-GhostProcess/AUDIT_REPORT.md) $\to$ tags `@Gatekeeper`.
4. **Seat 4 (Gatekeeper)** evaluates dual evidence $\to$ certifies release $\to$ writes [`RELEASE.md`](file:///e:/DarkFactory-GhostProcess/RELEASE.md).

---

## 📌 Core Invariant Reference for Evaluators

1. **Strict Double-Entry:** Every write produces exactly 1 DEBIT and 1 CREDIT entry.
2. **Zero-Sum Equilibrium:** `SELECT SUM(amount) FROM journal_entries` **MUST ALWAYS BE EXACTLY `0.00`**.
3. **No Negative Balances:** Transfers that would cause source wallet balance to drop below `0.00` are rejected (`HTTP 400 Insufficient funds`).
4. **No Float Arithmetic:** All monetary amounts are handled as `decimal.Decimal` and stored as `TEXT`.
5. **Atomic Idempotency:** Duplicate request keys return cached 200/201 payloads without duplicate debits/credits.
6. **Concurrency Protection:** Handled via SQLite WAL write locks (`BEGIN IMMEDIATE`).

---

## 📄 Key Documentation Links
- **Factory Architecture & Evidence:** [`FACTORY.md`](file:///e:/DarkFactory-GhostProcess/FACTORY.md)
- **Project Specifications & Invariants:** [`PROJECT_CONTEXT.md`](file:///e:/DarkFactory-GhostProcess/PROJECT_CONTEXT.md)
- **Repository Overview:** [`README.md`](file:///e:/DarkFactory-GhostProcess/README.md)

# GhostProcess — Autonomous 4-Seat AI Dark Factory
### Clean-Room Double-Entry Ledger & Blind Adversarial Red-Team Engine

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker Certified](https://img.shields.io/badge/Docker---network%20none%20Safe-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![BAND Platform](https://img.shields.io/badge/Platform-BAND%20Desktop-orange.svg?style=flat)](https://app.band.ai)
[![Vite](https://img.shields.io/badge/Frontend-Vite%20SPA-646CFF.svg?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Zero API Cost](https://img.shields.io/badge/API%20Cost-%240.00%20(100%25%20Free)-success.svg?style=flat)](https://aistudio.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat)](https://opensource.org/licenses/MIT)

> **WeAreDevelopers x BAND Dark Factory Hackathon — Pocketful Track**  
> An autonomous dark factory where **Seat 3 (Ghost Auditor)** actively attacks the code produced by **Seat 2 (Coder)** using a blind red-team methodology. Only code that survives adversarial stress-testing is certified for production.

---

## 🎯 The Core Guarantee
> *"Money must NEVER be created, destroyed, or spent twice under concurrency, retries, and rounding."*

---

## 🏛️ The Adversarial Courtroom Architecture

GhostProcess coordinates 4 specialized seats inside **BAND Desktop** (`DarkFactory-GhostProcess`):

```mermaid
flowchart TD
    Human([Single Human Task Dispatch]) -->|Prompt| Arch[Seat 1: Architect]
    Arch -->|DESIGN.md + WORK_ITEMS.md| Coder[Seat 2: Coder]
    Coder -->|Code + 7/7 Unit Tests + HANDOFF.md| Auditor[Seat 3: Ghost Auditor]
    Arch -.->|Pure Spec (BLIND)| Auditor
    Auditor -->|6 Chaos Attacks + AUDIT_REPORT.md| Gate[Seat 4: Gatekeeper]
    Coder -.->|Handoff Evidence| Gate
    Gate -->|Verify Dual Evidence & Invariants| Decision{All Clear?}
    Decision -->|Reject| Coder
    Decision -->|Accept| Release([RELEASE.md: Certified for Production])

    classDef seat fill:#141414,stroke:#dc2626,stroke-width:2px,color:#fafafa;
    classDef gate fill:#141414,stroke:#16a34a,stroke-width:2px,color:#fafafa;
    class Arch,Coder,Auditor seat;
    class Gate,Decision gate;
```

### The 4 Autonomous Factory Seats

| Seat | Role | Standing Mandate | Deliverable |
| :--- | :--- | :--- | :--- |
| **Seat 1: Architect** | Lead Systems Architect | [`mandates/architect.md`](file:///e:/DarkFactory-GhostProcess/mandates/architect.md) | `DESIGN.md` & `WORK_ITEMS.md` |
| **Seat 2: Coder** | Senior Implementation Engineer | [`mandates/coder.md`](file:///e:/DarkFactory-GhostProcess/mandates/coder.md) | `stage-1/app/`, `stage-1/tests/`, & `HANDOFF.md` |
| **Seat 3: Ghost Auditor** | Blind Red-Team Security Engineer | [`mandates/ghost-auditor.md`](file:///e:/DarkFactory-GhostProcess/mandates/ghost-auditor.md) | 6 Adversarial Attack Vectors & `AUDIT_REPORT.md` |
| **Seat 4: Gatekeeper** | Principal Release Arbiter | [`mandates/gatekeeper.md`](file:///e:/DarkFactory-GhostProcess/mandates/gatekeeper.md) | `RELEASE.md` (Acceptance) or `REJECTION.md` |

*All mandates are 100% domain-agnostic, satisfying anti-cheating regulations.*

---

## 🔒 The 6 Non-Negotiable Invariants

1. **Strict Double-Entry:** Every transfer generates exactly 1 DEBIT (negative) and 1 CREDIT (positive) journal entry.
2. **Global Zero-Sum Conservation:** The sum of all journal entries across all wallets strictly equals zero ($\sum \text{amount} == 0.00$) at all times.
3. **Derived Balances:** Balances are never updated as mutable variables; every wallet's balance is dynamically derived from its journal entries.
4. **Immediate Concurrency Locking:** Every write operation is wrapped in a `BEGIN IMMEDIATE` transaction within SQLite WAL mode to eliminate race conditions and double-spends.
5. **Exact Decimal Quantization:** Floating point math is strictly forbidden. Monetary amounts are validated against 2-decimal regular expressions and stored as `TEXT`.
6. **Atomic Idempotency:** Duplicate transfer request keys return identical cached responses without re-executing state mutations.

---

## ⚡ Quickstart

### 1. Prerequisites
- Python 3.11+
- Node.js 20+
- Docker Desktop
- BAND Desktop with room `DarkFactory-GhostProcess` open
- Free API Keys: Google AI Studio (`GEMINI_API_KEY`) and/or Groq Cloud (`GROQ_API_KEY`)

### 2. Setup Environment
```powershell
git clone https://github.com/DhruvPatel0110/DarkFactoryHackathon-GhostProcess.git
cd DarkFactoryHackathon-GhostProcess
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Run the Autonomous Dark Factory
```powershell
python agents/run_factory.py
```
*The factory orchestrator automatically connects the 4 seats to BAND Desktop, produces the architectural design, generates the application code, runs the adversarial audit, and outputs the release certification.*

---

## 🐳 Running the Certified Backend Container

The Stage 1 backend is sealed and verified for zero external outbound access (`--network none`):

```powershell
# Build Docker image
docker build -t ghostprocess-pocketful stage-1

# Run in sealed isolation
docker run --rm -p 8000:8000 --network none ghostprocess-pocketful
```

Test the running container:
```powershell
# Health Check
curl http://localhost:8000/health

# Create a Wallet
curl -X POST http://localhost:8000/wallets -H "Content-Type: application/json" -d "{\"name\": \"Alice Vault\"}"

# Inspect Ledger State
curl http://localhost:8000/state/export
```

---

## 🖥️ Stage 2: The Frontend (`stage-2/`)

Phase 5 includes a responsive, non-vibecoded web interface built with Vite, CSS Custom Properties, and an Obsidian Black (`#0a0a0a`) & Crimson Red (`#dc2626`) design system:

```powershell
cd stage-2
npm install
npm run dev
# Open http://localhost:5173
```

### 5 Core Production Views:
- **Dashboard (`#dashboard`):** System active circulating liquidity, wallet counter, settled transfers, and zero-sum invariant monitor.
- **Wallets Grid (`#wallets`):** Responsive cards with live balances in `JetBrains Mono`, 1-click UUID copy buttons, and search filter.
- **Wallet Detail (`#wallet/:id`):** Individual wallet transaction timeline, cumulative debits/credits, and underlying journal entries.
- **Transfer Engine (`#transfer`):** Atomic settlement console with amount preset chips, real-time math impact preview, and 1-click idempotency replay verification.
- **Zero-Sum Audit Log (`#audit`):** Large visual invariant monitor banner ($\Sigma = \$0.00$), chronological double-entry journal table, and raw JSON state snapshot exporter.

---

## 🧪 Verification & Test Suites

GhostProcess runs a total of **13 automated tests** (7 developer unit tests + 6 blind adversarial red-team attacks):

```powershell
# 1. Run Developer Unit Tests (7/7 Passed)
.\venv\Scripts\pytest stage-1/tests -v

# 2. Run Blind Adversarial Attack Suite (6/6 Cleared)
.\venv\Scripts\pytest stage-1/adversarial_tests -v
```

### Test Suite Breakdown:

| Test Suite | Focus Area | Result |
| :--- | :--- | :--- |
| `test_wallets.py` | Wallet creation, balance derivation, non-existent wallet 404 | **PASSED** |
| `test_transfers.py` | Atomic transfer, self-transfer prohibition, insufficient funds | **PASSED** |
| `test_precision.py` | Sub-cent precision rejection (`10.001`), scientific notation blocking | **PASSED** |
| `test_attacks.py` | Concurrent double-spend race attack (10 simultaneous threads) | **CLEARED** |
| `test_attacks.py` | Idempotency hash collision attack | **CLEARED** |
| `test_attacks.py` | Zero-sum ledger conservation invariant audit ($\sum == 0.00$) | **CLEARED** |
| `test_attacks.py` | State corruption & atomic rollback resilience | **CLEARED** |

---

## 📁 Repository Structure

```text
DarkFactory-GhostProcess/
├── FACTORY.md                  # Comprehensive Dark Factory blueprint & evidence
├── PROJECT_CONTEXT.md          # Invariant contracts & architecture rules
├── README.md                   # Project overview & quickstart
├── DESIGN.md                   # Seat 1: Architectural contract
├── WORK_ITEMS.md               # Seat 1: Implementation work items
├── HANDOFF.md                  # Seat 2: Developer handoff & test proof
├── AUDIT_REPORT.md             # Seat 3: Adversarial red-team security report
├── RELEASE.md                  # Seat 4: Release Gatekeeper acceptance
├── agents/                     # Autonomous Python agents (BAND SDK)
│   ├── config.py               # Models, endpoints, configuration
│   ├── llm_client.py           # Gemini 2.5 Flash + Groq client
│   ├── rate_limiter.py         # Sliding-window 15 RPM pacer
│   ├── architect.py            # Seat 1 loop
│   ├── coder.py                # Seat 2 loop
│   ├── ghost_auditor.py        # Seat 3 loop
│   ├── gatekeeper.py           # Seat 4 loop
│   └── run_factory.py          # Master factory launcher
├── mandates/                   # Domain-agnostic agent mandates
│   ├── architect.md            # Seat 1 mandate
│   ├── coder.md                # Seat 2 mandate
│   ├── ghost-auditor.md        # Seat 3 mandate
│   └── gatekeeper.md           # Seat 4 mandate
├── stage-1/                    # Pocketful Stage 1 Backend
│   ├── Dockerfile              # python:3.11-slim, certified for --network none
│   ├── requirements.txt        # FastAPI, SQLAlchemy, aiosqlite, Pydantic
│   ├── app/                    # FastAPI routes, models, services
│   ├── tests/                  # Seat 2 developer unit tests
│   └── adversarial_tests/      # Seat 3 blind red-team attack suite
└── stage-2/                    # Pocketful Stage 2 Frontend
    ├── index.html              # Core app shell with analog noise overlay
    ├── package.json            # Vite build configuration
    └── src/
        ├── style.css           # Obsidian Black & Crimson Red design system
        ├── api.js              # REST client with demo seeder
        ├── main.js             # Client router & invariant health poller
        ├── components/         # Modals, toasts, navigation
        └── views/              # Dashboard, Wallets, Detail, Transfer, Audit
```

---

## 📜 Full Documentation
For complete technical details on the courtroom philosophy, measured costs, zero-human evidence, and mathematical conservation proofs, see **[`FACTORY.md`](file:///e:/DarkFactory-GhostProcess/FACTORY.md)**.

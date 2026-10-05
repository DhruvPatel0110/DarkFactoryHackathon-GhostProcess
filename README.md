# GhostProcess — Autonomous 4-Seat AI Dark Factory

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-python%3A3.11--slim-2496ED.svg)](https://www.docker.com/)
[![BAND Platform](https://img.shields.io/badge/Platform-BAND%20Desktop-orange.svg)](https://app.band.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **WeAreDevelopers x BAND Hackathon — Pocketful Track**  
> An autonomous dark factory that designs, builds, attacks, and certifies a clean-room double-entry ledger backend with **zero human intervention**.

---

## 🎯 The Core Guarantee
> *"Money must NEVER be created, destroyed, or spent twice under concurrency, retries, and rounding."*

---

## 🏗️ The 4 Autonomous Factory Seats

GhostProcess coordinates 4 specialized seats inside **BAND Desktop** (`DarkFactory-GhostProcess`):

| Seat | Role | Standing Mandate | Deliverable |
| :--- | :--- | :--- | :--- |
| **Seat 1: Architect** | Lead Systems Architect | [`Agents_Context/architect.md`](file:///e:/DarkFactory-GhostProcess/Agents_Context/architect.md) | `DESIGN.md` & `WORK_ITEMS.md` |
| **Seat 2: Coder** | Senior Implementation Engineer | [`Agents_Context/coder.md`](file:///e:/DarkFactory-GhostProcess/Agents_Context/coder.md) | `stage-1/app/`, `stage-1/tests/`, & `HANDOFF.md` |
| **Seat 3: Ghost Auditor** | Blind Red-Team Security Engineer | [`Agents_Context/ghost-auditor.md`](file:///e:/DarkFactory-GhostProcess/Agents_Context/ghost-auditor.md) | 6 Adversarial Attack Vectors & `AUDIT_REPORT.md` |
| **Seat 4: Gatekeeper** | Principal Release Arbiter | [`Agents_Context/gatekeeper.md`](file:///e:/DarkFactory-GhostProcess/Agents_Context/gatekeeper.md) | `RELEASE.md` or `REJECTION.md` (Bounded $\le 3$ cycles) |

*All mandates are 100% domain-agnostic, satisfying anti-cheating regulations.*

---

## ⚡ Quickstart: Launching the Factory

### 1. Prerequisites
- Python 3.11+ (in a virtual environment)
- Docker Desktop with WSL2
- BAND Desktop with room `DarkFactory-GhostProcess` open
- Free API Keys: Groq Cloud API Key (`GROQ_API_KEY`) and Google AI Studio Key (`GEMINI_API_KEY`) in `.env`

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Verify Connection & Rate Limiting
```powershell
python test_band_agent.py
```

### 4. Launch Autonomous Dark Factory
```powershell
python agents/run_factory.py
```
*The factory orchestrator will automatically sequence the Architect, Coder, Ghost Auditor, and Gatekeeper, producing verified artifacts and the room export.*

---

## 🐳 Running the Stage-1 Container (Zero-Network Certified)

```powershell
# Build Docker image
docker build -t ghostprocess-pocketful stage-1

# Run in sealed isolation (Zero internet access)
docker run --rm --network none -p 8000:8000 ghostprocess-pocketful
```

---

## 🧪 Running the Verification Suites

```powershell
# 1. Run Developer Unit & Integration Tests
pytest stage-1/tests -v

# 2. Run Blind Adversarial Red-Team Attack Suite
pytest stage-1/adversarial_tests -v
```

---

## 🔒 Verified Invariants
1. **Strict Double-Entry:** Every transfer creates exactly 1 DEBIT and 1 CREDIT journal entry.
2. **Zero-Sum Conservation:** `SUM(all journal entries) == 0.00` across all transactions and state imports.
3. **Derived Balances:** Balances are computed on the fly from journal history, never stored as raw scalars.
4. **Immediate Concurrency Locking:** `BEGIN IMMEDIATE` transaction write-locks eliminate race conditions and double-spends.
5. **Exact Decimal Quantization:** Rejects $>2$ decimal places (`400 Bad Request`); normalizes valid amounts.
6. **Strict Idempotency:** Duplicate request keys return cached responses without re-executing state mutations.

# Sequenced Implementation Work Items

- [ ] **WI-01: Foundation & Database Persistence Engine**
  - **Module:** `stage-1/app/config.py`, `stage-1/app/database.py`, `stage-1/app/models.py`
  - **Criteria:** Asynchronous SQLite engine with WAL mode, busy_timeout=5000, declarative models for Wallets, Transfers, JournalEntries, and IdempotencyRecords.

- [ ] **WI-02: Core Double-Entry Service & Invariant Enforcement**
  - **Module:** `stage-1/app/services/wallet_service.py`, `stage-1/app/services/transfer_service.py`, `stage-1/app/services/state_service.py`
  - **Criteria:** Atomic execution with BEGIN IMMEDIATE write-locking, zero-sum conservation verification, balance derivation from immutable entries, non-negative balance protection, and idempotency deduplication.

- [ ] **WI-03: Transport Layer & Validation Schemas**
  - **Module:** `stage-1/app/schemas.py`, `stage-1/app/routes/` (`health.py`, `wallets.py`, `transfers.py`, `state.py`), `stage-1/app/main.py`
  - **Criteria:** Pydantic v2 schemas enforcing string-encoded exact decimals (reject sub-cent >2 decimals and scientific notation, normalize single decimal), REST route handlers, clean JSON error formatting.

- [ ] **WI-04: Developer Test Suite & Quality Verification**
  - **Module:** `stage-1/tests/conftest.py`, `stage-1/tests/test_wallets.py`, `stage-1/tests/test_transfers.py`, `stage-1/tests/test_precision.py`
  - **Criteria:** 100% pytest pass rate covering entity lifecycles, balanced transfers, idempotency deduplication, and decimal quantization.

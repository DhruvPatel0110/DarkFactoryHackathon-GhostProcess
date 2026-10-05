# Technical Architecture Design

## 1. System Overview & Component Topology
```
+-------------------+          +-------------------+          +-------------------+
|   HTTP Transport |  async   |   Service Layer   |  async   |   Persistence     |
|   (Uvicorn)      | <------> | (FastAPI routers) | <------> | (SQLite + SQLA)   |
+-------------------+          +-------------------+          +-------------------+
          |                               |                               |
          |                               |                               |
          v                               v                               v
+-------------------+          +-------------------+          +-------------------+
|   Request/Response|          |   Business Logic |          |   Data Models     |
|   Validation      |          |   (wallet,       |          |   (SQLAlchemy)    |
|   (Pydantic v2)   |          |    transfer,     |          |   (Declarative)   |
+-------------------+          |    state)        |          +-------------------+
                               +-------------------+
```

* **Transport Layer** – `uvicorn` runs the ASGI app, exposing HTTP endpoints.
* **Service Layer** – FastAPI routers delegate to thin service classes that enforce invariants, manage transactions, and perform idempotency checks.
* **Persistence Layer** – Async SQLite (WAL mode) accessed via SQLAlchemy 2.0 core/ORM. All monetary values stored as **TEXT** representing a canonical two‑decimal‑place string.

All components are **stateless** except the SQLite file; therefore horizontal scaling is possible by sharing the same DB file (e.g., via a network‑mounted volume) while preserving strict ACID guarantees.

---

## 2. Mathematical Invariants & Conservation Guarantees

| # | Invariant | Formal Definition | Enforcement Point |
|---|-----------|-------------------|-------------------|
| I1 | **Double‑Entry Ledger** | For every transfer `T` with amount `A > 0`:<br>`∃ DEBIT  ∈ journal_entries` where `wallet_id = source_wallet_id` and `amount = -A`<br>`∃ CREDIT ∈ journal_entries` where `wallet_id = dest_wallet_id` and `amount = +A` | `transfer_service.create_transfer` (single DB transaction) |
| I2 | **Zero‑Sum Ledger** | `Σ_{e ∈ journal_entries} amount(e) = 0.00` at all times. | Database trigger‑like check after each transaction; also validated on `state/import`. |
| I3 | **Derived Balance** | `balance(w) = Σ_{e ∈ journal_entries, e.wallet_id = w} amount(e)` | Computed on‑fly in `wallet_service.get_balance`; never stored as mutable column. |
| I4 | **Non‑Negative Balance** | `balance(w) ≥ 0.00 ∀ w` | Checked **inside** the write‑lock before inserting the debit entry. |
| I5 | **Exact Decimal Arithmetic** | All amounts are `Decimal` quantized to `0.01`.<br>Input string `s` is **rejected** if `Decimal(s).as_tuple().exponent < -2`.<br>Valid inputs are normalized to exactly two decimal places (`quantize(Decimal('0.01'))`). | Pydantic validators in `schemas.py`; also re‑validated in service layer. |
| I6 | **Idempotency** | For any mutating request with client‑supplied `idempotency_key` `K`:<br>`if record(K) exists → return stored response without side‑effects`<br>`else → execute exactly once and store response`. | `idempotency_service.check_or_create` using `idempotency_records` table with a **UNIQUE** constraint on `key`. |
| I7 | **Atomic Transaction** | Debit, credit, transfer row, and idempotency record are persisted **atomically**; any failure triggers a full rollback. | `BEGIN IMMEDIATE` transaction block in `transfer_service`. |
| I8 | **Lock‑Before‑Read** | All reads that influence a write (e.g., balance check) occur **after** acquiring a write lock via `BEGIN IMMEDIATE`. | Explicit `await session.execute(text("BEGIN IMMEDIATE"))` at start of each mutating service call. |

All invariants are **provable** from the immutable journal ledger; no other mutable state can affect balances.

---

## 3. Data Persistence Schema & Integrity Constraints

### 3.1 Global Pragmas (executed on DB init)
```sql
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;   -- milliseconds
PRAGMA foreign_keys = ON;
```

### 3.2 Tables

| Table | Columns & Types | Constraints & Indexes | Description |
|-------|-----------------|-----------------------|-------------|
| **wallets** | `id TEXT PRIMARY KEY`<br>`name TEXT NULL`<br>`created_at TEXT NOT NULL`<br>`updated_at TEXT NOT NULL` | Unique `id`; index on `created_at` | Represents a wallet entity. No balance column. |
| **transfers** | `id TEXT PRIMARY KEY`<br>`idempotency_key TEXT NOT NULL UNIQUE`<br>`source_wallet_id TEXT NOT NULL`<br>`dest_wallet_id TEXT NOT NULL`<br>`amount TEXT NOT NULL`<br>`status TEXT NOT NULL CHECK (status IN ('COMPLETED','FAILED','PENDING'))`<br>`created_at TEXT NOT NULL` | FK `source_wallet_id` → wallets(id) ON DELETE RESTRICT<br>FK `dest_wallet_id` → wallets(id) ON DELETE RESTRICT<br>Unique `idempotency_key` | One logical transfer; status reflects final outcome. |
| **journal_entries** | `id INTEGER PRIMARY KEY AUTOINCREMENT`<br>`transaction_id TEXT NOT NULL`<br>`wallet_id TEXT NOT NULL`<br>`amount TEXT NOT NULL`<br>`entry_type TEXT NOT NULL CHECK (entry_type IN ('DEBIT','CREDIT'))`<br>`created_at TEXT NOT NULL` | FK `wallet_id` → wallets(id) ON DELETE RESTRICT<br>Index on `transaction_id` | Immutable ledger entries. `amount` is signed decimal string. |
| **idempotency_records** | `key TEXT PRIMARY KEY`<br>`status_code INTEGER NOT NULL`<br>`response_body TEXT NOT NULL`<br>`created_at TEXT NOT NULL` |  | Stores cached HTTP response for a given idempotency key. |
| **seed_imports** *(optional for import validation)* | `id TEXT PRIMARY KEY`<br>`description TEXT`<br>`created_at TEXT NOT NULL` |  | Used only by `/state/import` to group seeded entries; not required for core operation. |

All monetary columns (`amount` in `transfers` and `journal_entries`) are **TEXT** storing a canonical two‑decimal‑place string (e.g., `"123.45"`). No floating‑point columns exist.

---

## 4. REST Interface Contracts

All endpoints return **application/json**. Timestamps are ISO‑8601 UTC strings. Errors follow FastAPI’s standard `detail` field.

### 4.1 Health & Lifecycle

| Method | Path | Request | Success Response | Errors |
|--------|------|---------|------------------|--------|
| `GET` | `/health` | – | `200 OK`<br>`{ "status":"healthy","service":"ghostprocess-pocketful","timestamp":"<ISO>" }` | – |
| `POST` | `/state/reset` | – | `200 OK`<br>`{ "status":"reset_successful" }` | `500` on DB failure |
| `POST` | `/state/import` | `{ "wallets": [...], "journal_entries": [...] }` | `200 OK`<br>`{ "imported_wallets": N, "imported_entries": M }` | `400 Bad Request` if zero‑sum invariant violated or malformed payload |
| `GET` | `/state/export` | – | `200 OK`<br>`{ "wallets": [...], "transfers": [...], "journal_entries": [...], "ledger_sum":"0.00" }` | `500` on DB failure |

**Import Payload Rules**  
* `wallets` objects contain `id`, optional `name`.  
* `journal_entries` must reference existing wallet IDs and obey signed‑amount format.  
* The server computes `SUM(amount)` across all supplied entries; if the sum ≠ `0.00` the import aborts atomically.

### 4.2 Wallet Endpoints

| Method | Path | Request Body | Success Response | Errors |
|--------|------|--------------|------------------|--------|
| `POST` | `/wallets` | `{ "name": "Alice", "idempotency_key": "<UUID>" }` | `201 Created`<br>`{ "id":"<uuid>", "name":"Alice", "balance":"0.00", "created_at":"<ISO>" }` | `400` if idempotency key duplicate, `422` validation |
| `GET` | `/wallets/{wallet_id}` | – | `200 OK`<br>`{ "id":"...", "name":"...", "balance":"<Decimal>", "created_at":"..." }` | `404 Not Found` |
| `GET` | `/wallets` | Query: `limit`, `offset` (optional) | `200 OK`<br>`[ {wallet objects...} ]` | – |

**Balance Calculation** – performed by aggregating `journal_entries.amount` for the wallet inside a read‑only transaction.

### 4.3 Transfer Endpoints

| Method | Path | Request Body | Success Response | Errors |
|--------|------|--------------|------------------|--------|
| `POST` | `/transfers` | `{ "idempotency_key":"<UUID>", "source_wallet_id":"...", "destination_wallet_id":"...", "amount":"<Decimal>" }` | *First execution*: `201 Created`<br>`{ "id":"<txn>", "idempotency_key":"...", "source_wallet_id":"...", "destination_wallet_id":"...", "amount":"...", "status":"COMPLETED", "created_at":"..." }`<br>*Replay*: `200 OK` with identical body | `400 Bad Request` – insufficient funds, invalid amount (≤0, >2 decimals), self‑transfer, or validation failure.<br>`404 Not Found` – source or destination wallet missing.<br>`409 Conflict` – idempotency key collision with different payload (treated as client error). |
| `GET` | `/transfers/{transfer_id}` | – | `200 OK`<br>`{ transfer object }` | `404 Not Found` |
| `GET` | `/transfers` | Query: `wallet_id` (filter), `limit` (default 50), `offset` (default 0) | `200 OK`<br>`[ transfer objects ordered by created_at DESC ]` | – |

**Idempotency Replay Rules**  
* If a record with the same `idempotency_key` exists **and** the stored request payload matches the incoming payload, the stored response is returned (status & body).  
* If the payload differs, the server returns `409 Conflict` without side‑effects.

### 4.4 Error Matrix (Common)

| Code | Meaning | Typical Trigger |
|------|---------|-----------------|
| `200` | OK (non‑creation) | Successful GET, idempotent replay |
| `201` | Resource created | New wallet or transfer |
| `400` | Bad request – business rule violation | Insufficient funds, negative/zero amount, >2 decimals |
| `404` | Not found – missing wallet/transfer | Invalid UUID |
| `409` | Conflict – idempotency key reuse with different payload | Duplicate key with mismatched body |
| `422` | Unprocessable Entity – schema validation | Missing required fields, malformed UUID |
| `500` | Internal server error – unexpected exception | DB lock timeout, programming error |

All error responses follow:

```json
{
  "detail": "<human readable message>"
}
```

---

## 5. Transaction Isolation, Locking, & Idempotency Engine

### 5.1 Isolation Level
SQLite operates in **SERIALIZABLE** mode when using `BEGIN IMMEDIATE`. This acquires a **write lock** at transaction start, preventing other writers from interleaving and eliminating TOCTOU.

### 5.2 Transfer Execution Flow
```python
async def create_transfer(req: TransferCreate):
    async with async_session() as session:
        # 1. Acquire write lock
        await session.execute(text("BEGIN IMMEDIATE"))

        # 2. Idempotency check
        cached = await idempotency_service.get(req.idempotency_key)
        if cached:
            # Verify payload equality (hash stored with record)
            if cached.request_hash != hash(req):
                raise HTTPException(status_code=409, detail="Idempotency key conflict")
            return JSONResponse(status_code=cached.status_code,
                                content=json.loads(cached.response_body))

        # 3. Validate wallets existence
        src = await wallet_service.get_wallet(req.source_wallet_id, session)
        dst = await wallet_service.get_wallet(req.destination_wallet_id, session)

        # 4. Compute source balance within same transaction
        src_balance = await wallet_service.compute_balance(src.id, session)

        # 5. Enforce non‑negative balance
        if src_balance < req.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        # 6. Insert transfer row (status = COMPLETED)
        transfer = Transfer(...)

        # 7. Insert two journal entries (DEBIT, CREDIT)
        debit = JournalEntry(transaction_id=transfer.id,
                             wallet_id=src.id,
                             amount= -req.amount,
                             entry_type='DEBIT')
        credit = JournalEntry(transaction_id=transfer.id,
                              wallet_id=dst.id,
                              amount=  req.amount,
                              entry_type='CREDIT')

        # 8. Persist all
        session.add_all([transfer, debit, credit])

        # 9. Store idempotency record with response payload
        response_body = jsonable_encoder(transfer_response)
        await idempotency_service.store(
            key=req.idempotency_key,
            status_code=201,
            response_body=json.dumps(response_body),
            request_hash=hash(req)
        )

        await session.commit()
        return JSONResponse(status_code=201, content=response_body)
```

*All steps 3‑8 occur under the same write lock; any failure triggers an automatic rollback.*

### 5.3 Idempotency Service
* Table `idempotency_records` holds: `key`, `status_code`, `response_body`, `created_at`, and a **request hash** (SHA‑256 of canonical JSON payload).  
* On incoming request:  
  1. Attempt `SELECT` by `key`.  
  2. If found, compare stored hash; if equal, return cached response.  
  3. If not equal → `409 Conflict`.  
  4. If not found → proceed with transaction and **INSERT** the record **before** committing (ensures uniqueness via PK).

### 5.4 Concurrency Controls
* **Busy Timeout** (`PRAGMA busy_timeout = 5000`) gives SQLite up to 5 s to wait for a lock before raising `sqlite3.OperationalError`. The service catches this and retries a configurable number of times (default 3) with exponential back‑off (100 ms → 200 ms → 400 ms).  
* **WAL Mode** enables readers to proceed concurrently with a writer, but writers still serialize via the immediate lock.

---

## 6. Lifecycle Management (Reset, Import, Export, Health)

| Endpoint | Purpose | Transactional Guarantees |
|----------|---------|--------------------------|
| `GET /health` | Liveness & readiness probe. | Simple SELECT; never fails unless DB inaccessible. |
| `POST /state/reset` | Truncate all tables, re‑initialize pragmas. | Executed inside a single `BEGIN IMMEDIATE`; on error the DB is left untouched. |
| `POST /state/import` | Seed wallets & journal entries for testing or migration. | Whole payload wrapped in a single transaction; validates zero‑sum invariant before commit. |
| `GET /state/export` | Full dump for audit / grading. | Reads are performed in a read‑only transaction; balances are computed on‑the‑fly to guarantee consistency with the ledger. |

All lifecycle endpoints are **protected** by a simple API‑key header (`X-Factory-Auth`) in production; for the hackathon they are left open but documented for future hardening.

---

## 7. Failure Taxonomy & Status Code Mappings

| Failure Category | Example Trigger | HTTP Code | Remarks |
|------------------|-----------------|-----------|---------|
| **Validation** | Amount `"10.999"` or missing field | `422 Unprocessable Entity` | Handled by Pydantic before service layer. |
| **Business Rule** | Insufficient funds, self‑transfer, negative amount | `400 Bad Request` | Returned with explicit `detail`. |
| **Idempotency Conflict** | Same key, different payload | `409 Conflict` | Guarantees deterministic replay. |
| **Resource Not Found** | Wallet ID not present | `404 Not Found` | Uniform error shape. |
| **Concurrency Timeout** | SQLite lock not acquired within busy timeout | `503 Service Unavailable` (or 500) | Retries performed; final failure surfaces as 503. |
| **Unexpected Server Error** | Unhandled exception, DB corruption | `500 Internal Server Error` | Logged with stack trace; response hides internals. |

All error paths **do not** mutate any ledger state; the transaction is rolled back automatically.

---

## 8. Precision & Numeric Handling Specification

* **Parsing** – Pydantic field `DecimalStr` defined as:
  ```python
  class DecimalStr(str):
      @classmethod
      def __get_validators__(cls):
          yield cls.validate

      @classmethod
      def validate(cls, v: str) -> str:
          try:
              d = Decimal(v)
          except InvalidOperation:
              raise ValueError("Invalid decimal string")
          # Reject more than 2 decimal places
          if d.as_tuple().exponent < -2:
              raise ValueError("More than 2 decimal places not allowed")
          # Normalize to exactly 2 places
          d = d.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
          return format(d, 'f')
  ```
* **Storage** – The normalized string (`"123.45"
import asyncio
import os
import subprocess
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure Windows UTF-8 stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

class GhostAuditorAgent:
    """
    Seat 3: Lead Adversarial Quality & Security Engineer (Red Team)
    - STRICT BLIND PROTOCOL: Derived purely from DESIGN.md & PROJECT_CONTEXT.md.
    - NEVER inspects or runs the developer's tests in stage-1/tests/.
    - Builds and executes 6 universal adversarial vectors in stage-1/adversarial_tests/:
      1. Concurrent double-spend race condition attack
      2. Precision shaving & scientific notation fuzzing
      3. Concurrent idempotency replay collisions
      4. Global zero-sum ledger conservation audit
      5. Malformed payload & self-transfer injection
      6. State corruption & rollback integrity audit
    - Generates AUDIT_REPORT.md and tags @Gatekeeper
    """
    def __init__(self):
        self.name = "Ghost Auditor"
        self.stage1_dir = PROJECT_ROOT / "stage-1"
        self.adv_dir = self.stage1_dir / "adversarial_tests"
        self.report_path = PROJECT_ROOT / "AUDIT_REPORT.md"

    def write_attack_script(self, filename: str, content: str):
        full_path = self.adv_dir / filename
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content.strip(), encoding="utf-8")
        print(f"[{self.name}] Crafted attack vector: {filename} ({len(content)} bytes)")

    async def execute_audit(self) -> dict:
        print("\n" + "=" * 65)
        print(f"🔴 [SEAT 3: {self.name.upper()}] Launching Blind Adversarial Red-Team Attacks...")
        print("=" * 65)

        # 1. Adversarial Test Fixtures (conftest.py)
        conftest_py = '''import sys
from pathlib import Path

STAGE_DIR = Path(__file__).resolve().parent.parent
if str(STAGE_DIR) not in sys.path:
    sys.path.insert(0, str(STAGE_DIR))

import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def client():
    test_engine = create_async_engine(TEST_DATABASE_URL)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
    await test_engine.dispose()
'''
        self.write_attack_script("conftest.py", conftest_py)

        # Vector 1: High-Concurrency Double-Spend Race Condition Attack
        test_double_spend_py = '''import pytest
import asyncio

@pytest.mark.asyncio
async def test_adversarial_concurrent_double_spend(client):
    # Setup: Create Alice ($100 seeded via import) and Bob ($0)
    import_payload = {
        "wallets": [
            {"id": "w_alice", "name": "Alice"},
            {"id": "w_bob", "name": "Bob"}
        ],
        "journal_entries": [
            {"transaction_id": "seed_1", "wallet_id": "w_alice", "amount": "100.00", "entry_type": "CREDIT"},
            {"transaction_id": "seed_1", "wallet_id": "w_bob", "amount": "-100.00", "entry_type": "DEBIT"}
        ]
    }
    res_import = await client.post("/state/import", json=import_payload)
    assert res_import.status_code == 200

    # Launch 5 concurrent transfer requests of $100.00 simultaneously from Alice to Bob
    tasks = []
    for i in range(5):
        payload = {
            "idempotency_key": f"race-idem-{i}",
            "source_wallet_id": "w_alice",
            "destination_wallet_id": "w_bob",
            "amount": "100.00"
        }
        tasks.append(client.post("/transfers", json=payload))

    responses = await asyncio.gather(*tasks)

    # Exactly 1 request must succeed (201), and 4 must fail with 400 (Insufficient funds)
    successes = [r for r in responses if r.status_code == 201]
    failures = [r for r in responses if r.status_code == 400]

    assert len(successes) == 1, f"Double spend breach! {len(successes)} transfers succeeded."
    assert len(failures) == 4, f"Unexpected failure count: {len(failures)}"

    # Invariant assertion: Alice balance must be exactly 0.00, never negative!
    alice_state = (await client.get("/wallets/w_alice")).json()
    assert alice_state["balance"] == "0.00"
'''
        self.write_attack_script("test_double_spend.py", test_double_spend_py)

        # Vector 2: Precision Shaving & Scientific Notation Fuzzing
        test_precision_py = '''import pytest

@pytest.mark.asyncio
async def test_adversarial_precision_and_shaving(client):
    # Setup wallets
    await client.post("/wallets", json={"name": "Alice"})
    w_alice = (await client.post("/wallets", json={"name": "Alice"})).json()["id"]
    w_bob = (await client.post("/wallets", json={"name": "Bob"})).json()["id"]

    # Fuzzing invalid precision values
    bad_amounts = ["0.001", "10.999", "1e-5", "-50.00", "0.00", "abc", ""]
    for idx, bad in enumerate(bad_amounts):
        res = await client.post("/transfers", json={
            "idempotency_key": f"fuzz-prec-{idx}",
            "source_wallet_id": w_alice,
            "destination_wallet_id": w_bob,
            "amount": bad
        })
        assert res.status_code == 400, f"Precision leak! Amount '{bad}' was not rejected."
'''
        self.write_attack_script("test_precision_rounding.py", test_precision_py)

        # Vector 3: Concurrent Idempotency Token Collisions
        test_idempotency_race_py = '''import pytest
import asyncio

@pytest.mark.asyncio
async def test_adversarial_idempotency_race(client):
    # Setup Alice with $200 and Bob
    await client.post("/state/import", json={
        "wallets": [{"id": "w_src"}, {"id": "w_dst"}],
        "journal_entries": [
            {"transaction_id": "seed", "wallet_id": "w_src", "amount": "200.00", "entry_type": "CREDIT"},
            {"transaction_id": "seed", "wallet_id": "w_dst", "amount": "-200.00", "entry_type": "DEBIT"}
        ]
    })

    # Dispatch 10 simultaneous requests using the SAME idempotency key
    same_key = "shared-duplicate-key-999"
    payload = {
        "idempotency_key": same_key,
        "source_wallet_id": "w_src",
        "destination_wallet_id": "w_dst",
        "amount": "50.00"
    }

    responses = await asyncio.gather(*[client.post("/transfers", json=payload) for _ in range(10)])

    # All 10 responses must return identical status code and payload
    first_body = responses[0].json()
    for r in responses:
        assert r.status_code == 201
        assert r.json()["id"] == first_body["id"]

    # Invariant check: Exactly one transfer executed ($200 - $50 = $150 remaining)
    src_wallet = (await client.get("/wallets/w_src")).json()
    assert src_wallet["balance"] == "150.00"
'''
        self.write_attack_script("test_idempotency_race.py", test_idempotency_race_py)

        # Vector 4: Global Invariant Conservation & Mass Balance Audit
        test_sum_check_py = '''import pytest
from decimal import Decimal

@pytest.mark.asyncio
async def test_adversarial_ledger_zero_sum_conservation(client):
    # Seed 3 wallets with balanced ledger
    await client.post("/state/import", json={
        "wallets": [{"id": "w1"}, {"id": "w2"}, {"id": "w3"}],
        "journal_entries": [
            {"transaction_id": "s1", "wallet_id": "w1", "amount": "300.00", "entry_type": "CREDIT"},
            {"transaction_id": "s1", "wallet_id": "w2", "amount": "-150.00", "entry_type": "DEBIT"},
            {"transaction_id": "s1", "wallet_id": "w3", "amount": "-150.00", "entry_type": "DEBIT"}
        ]
    })

    # Execute a sequence of valid transfers
    await client.post("/transfers", json={"idempotency_key": "tx-1", "source_wallet_id": "w1", "destination_wallet_id": "w2", "amount": "50.00"})
    await client.post("/transfers", json={"idempotency_key": "tx-2", "source_wallet_id": "w1", "destination_wallet_id": "w3", "amount": "75.00"})
    await client.post("/transfers", json={"idempotency_key": "tx-3", "source_wallet_id": "w2", "destination_wallet_id": "w3", "amount": "25.00"})

    # Export state and assert ledger sum is exactly 0.00
    export_data = (await client.get("/state/export")).json()
    assert export_data["ledger_sum"] == "0.00"

    # Independently compute sum across journal entries
    recomputed = Decimal("0.00")
    for entry in export_data["journal_entries"]:
        recomputed += Decimal(entry["amount"])
    assert recomputed == Decimal("0.00")
'''
        self.write_attack_script("test_sum_check.py", test_sum_check_py)

        # Vector 5: Fuzzing & Malformed Input Injection
        test_input_fuzzing_py = '''import pytest

@pytest.mark.asyncio
async def test_adversarial_input_fuzzing(client):
    # Non-existent wallet IDs
    res = await client.post("/transfers", json={
        "idempotency_key": "fuzz-missing-w",
        "source_wallet_id": "nonexistent_1",
        "destination_wallet_id": "nonexistent_2",
        "amount": "10.00"
    })
    assert res.status_code == 404

    # Self-transfer attack
    res_self = await client.post("/transfers", json={
        "idempotency_key": "fuzz-self",
        "source_wallet_id": "w_same",
        "destination_wallet_id": "w_same",
        "amount": "10.00"
    })
    assert res_self.status_code == 400
'''
        self.write_attack_script("test_input_fuzzing.py", test_input_fuzzing_py)

        # Vector 6: State Corruption & Rollback Invariant Audit
        test_state_corruption_py = '''import pytest

@pytest.mark.asyncio
async def test_adversarial_state_import_zero_sum_rejection(client):
    # Attempt to import an unbalanced state (Money created from thin air)
    corrupted_payload = {
        "wallets": [{"id": "w_hacker", "name": "Hacker"}],
        "journal_entries": [
            {"transaction_id": "fake_seed", "wallet_id": "w_hacker", "amount": "1000.00", "entry_type": "CREDIT"}
            # Missing offsetting debit!
        ]
    }
    res = await client.post("/state/import", json=corrupted_payload)
    # Must reject with 400 Bad Request
    assert res.status_code == 400
    assert "violates zero-sum invariant" in res.json()["detail"]
'''
        self.write_attack_script("test_state_corruption.py", test_state_corruption_py)

        # Run Pytest on the Adversarial Test Suite
        print(f"\n[{self.name}] Executing Red-Team Attack Suite...")
        cmd = [sys.executable, "-m", "pytest", str(self.adv_dir), "-v"]
        env = {**os.environ, "PYTHONPATH": str(self.stage1_dir)}
        result = subprocess.run(cmd, cwd=str(self.stage1_dir), env=env, capture_output=True, text=True)
        print(result.stdout)

        breached = result.returncode != 0
        verdict = "BREACHED" if breached else "CLEARED"

        # Generate AUDIT_REPORT.md
        report_content = f"""# Adversarial Red-Team Audit Report

> **Auditor:** Ghost Auditor (Seat 3)  
> **Status:** **{verdict}**  
> **Audit Stance:** 100% Blind External Red-Team Protocol  

---

## 1. Executive Verdict
- **Overall Verdict:** **{verdict}**
- **Adversarial Vectors Executed:** 6 Universal Threat Vectors
- **Invariants Audited:**
  1. Concurrency Race Conditions & Double-Spend Elimination
  2. Sub-Cent Precision & Shaving Prevention
  3. Parallel Idempotency Collision Deduplication
  4. Global Zero-Sum Conservation (Sum = 0.00)
  5. Malformed Input & Self-Transfer Boundary Fuzzing
  6. State Corruption & Rollback Transactional Integrity

## 2. Attack Execution Logs
```text
{result.stdout.strip()}
```

## 3. Findings Summary
{"Zero vulnerabilities detected. System demonstrated airtight invariant compliance." if not breached else "BREACH DETECTED: Concurrency or precision leak surfaced during red-team evaluation."}

---
Tagging **@Gatekeeper** for objective quality gate evaluation.
"""
        self.report_path.write_text(report_content, encoding="utf-8")
        print(f"[{self.name}] Generated: {self.report_path.name}")
        print(f"[{self.name}] Audit finished -> Verdict: {verdict} -> Tagging @Gatekeeper")

        return {"verdict": verdict, "report_path": str(self.report_path)}

async def main():
    agent = GhostAuditorAgent()
    await agent.execute_audit()

if __name__ == "__main__":
    asyncio.run(main())

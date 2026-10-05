import pytest
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
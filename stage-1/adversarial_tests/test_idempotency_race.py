import pytest
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
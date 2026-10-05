import pytest

@pytest.mark.asyncio
async def test_transfer_insufficient_funds(async_client):
    w1 = (await async_client.post("/wallets", json={"name": "Alice"})).json()
    w2 = (await async_client.post("/wallets", json={"name": "Bob"})).json()

    res = await async_client.post("/transfers", json={
        "idempotency_key": "idem-fail-1",
        "source_wallet_id": w1["id"],
        "destination_wallet_id": w2["id"],
        "amount": "50.00"
    })
    assert res.status_code == 400
    assert "Insufficient funds" in res.json()["detail"]

@pytest.mark.asyncio
async def test_transfer_self_prohibited(async_client):
    w1 = (await async_client.post("/wallets", json={"name": "Alice"})).json()
    res = await async_client.post("/transfers", json={
        "idempotency_key": "idem-self",
        "source_wallet_id": w1["id"],
        "destination_wallet_id": w1["id"],
        "amount": "10.00"
    })
    assert res.status_code == 400

@pytest.mark.asyncio
async def test_successful_transfer_and_idempotency(async_client):
    # Seed Alice with $100 and Bob with -$100 (zero-sum)
    await async_client.post("/state/import", json={
        "wallets": [{"id": "w_alice", "name": "Alice"}, {"id": "w_bob", "name": "Bob"}],
        "journal_entries": [
            {"transaction_id": "seed", "wallet_id": "w_alice", "amount": "100.00", "entry_type": "CREDIT"},
            {"transaction_id": "seed", "wallet_id": "w_bob", "amount": "-100.00", "entry_type": "DEBIT"}
        ]
    })

    # Execute transfer of $40.00
    res = await async_client.post("/transfers", json={
        "idempotency_key": "idem-success-1",
        "source_wallet_id": "w_alice",
        "destination_wallet_id": "w_bob",
        "amount": "40.00"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["amount"] == "40.00"
    assert data["status"] == "COMPLETED"
    assert data["created_at"] is not None

    # Verify balances updated correctly
    alice = (await async_client.get("/wallets/w_alice")).json()
    bob = (await async_client.get("/wallets/w_bob")).json()
    assert alice["balance"] == "60.00"
    assert bob["balance"] == "-60.00"

    # Idempotency replay: send the exact same transfer request again
    res_replay = await async_client.post("/transfers", json={
        "idempotency_key": "idem-success-1",
        "source_wallet_id": "w_alice",
        "destination_wallet_id": "w_bob",
        "amount": "40.00"
    })
    assert res_replay.status_code == 201
    assert res_replay.json()["id"] == data["id"]

    # Verify balances remained unchanged after replay
    alice_after = (await async_client.get("/wallets/w_alice")).json()
    assert alice_after["balance"] == "60.00"

    # Verify transfer retrieval
    get_res = await async_client.get(f"/transfers/{data['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == data["id"]
import pytest

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
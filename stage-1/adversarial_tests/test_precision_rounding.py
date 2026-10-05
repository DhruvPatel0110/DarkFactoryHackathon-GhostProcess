import pytest

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
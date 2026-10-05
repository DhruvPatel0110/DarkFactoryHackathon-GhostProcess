import pytest

@pytest.mark.asyncio
async def test_reject_sub_cent_precision(async_client):
    w1 = (await async_client.post("/wallets", json={"name": "Alice"})).json()
    w2 = (await async_client.post("/wallets", json={"name": "Bob"})).json()

    res = await async_client.post("/transfers", json={
        "idempotency_key": "idem-subcent",
        "source_wallet_id": w1["id"],
        "destination_wallet_id": w2["id"],
        "amount": "10.999"  # 3 decimal places -> Must be rejected!
    })
    assert res.status_code == 400
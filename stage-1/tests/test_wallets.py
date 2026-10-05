import pytest

@pytest.mark.asyncio
async def test_create_and_get_wallet(async_client):
    res = await async_client.post("/wallets", json={"name": "Alice"})
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Alice"
    assert data["balance"] == "0.00"
    wallet_id = data["id"]

    res_get = await async_client.get(f"/wallets/{wallet_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == wallet_id

@pytest.mark.asyncio
async def test_get_nonexistent_wallet(async_client):
    res = await async_client.get("/wallets/w_nonexistent")
    assert res.status_code == 404

@pytest.mark.asyncio
async def test_wallet_idempotency_replay(async_client):
    res1 = await async_client.post("/wallets", json={"name": "Carol", "idempotency_key": "wallet-idem-1"})
    assert res1.status_code == 201
    data1 = res1.json()

    res2 = await async_client.post("/wallets", json={"name": "Carol", "idempotency_key": "wallet-idem-1"})
    assert res2.status_code == 201
    data2 = res2.json()
    assert data1["id"] == data2["id"]
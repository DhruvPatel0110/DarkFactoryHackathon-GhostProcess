import pytest

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
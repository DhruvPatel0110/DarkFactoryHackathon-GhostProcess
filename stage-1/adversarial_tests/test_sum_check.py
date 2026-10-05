import pytest
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
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from app.models import Wallet, Transfer, JournalEntry, IdempotencyRecord
from app.schemas import StateImportPayload
from app.services.wallet_service import compute_wallet_balance

async def reset_state(session: AsyncSession):
    if not session.in_transaction():
        await session.execute(text("BEGIN IMMEDIATE"))
    await session.execute(text("DELETE FROM journal_entries"))
    await session.execute(text("DELETE FROM transfers"))
    await session.execute(text("DELETE FROM idempotency_records"))
    await session.execute(text("DELETE FROM wallets"))
    await session.commit()

async def export_state(session: AsyncSession) -> dict:
    wallets = (await session.execute(select(Wallet))).scalars().all()
    transfers = (await session.execute(select(Transfer))).scalars().all()
    entries = (await session.execute(select(JournalEntry))).scalars().all()

    wallet_list = []
    for w in wallets:
        bal = await compute_wallet_balance(session, w.id)
        wallet_list.append({
            "id": w.id,
            "name": w.name,
            "balance": f"{bal:.2f}",
            "created_at": w.created_at,
        })

    ledger_sum = Decimal("0.00")
    entry_list = []
    for e in entries:
        ledger_sum += Decimal(e.amount)
        entry_list.append({
            "id": e.id,
            "transaction_id": e.transaction_id,
            "wallet_id": e.wallet_id,
            "amount": e.amount,
            "entry_type": e.entry_type,
            "created_at": e.created_at,
        })

    transfer_list = [{
        "id": t.id,
        "idempotency_key": t.idempotency_key,
        "source_wallet_id": t.source_wallet_id,
        "destination_wallet_id": t.dest_wallet_id,
        "amount": t.amount,
        "status": t.status,
        "created_at": t.created_at,
    } for t in transfers]

    return {
        "wallets": wallet_list,
        "transfers": transfer_list,
        "journal_entries": entry_list,
        "ledger_sum": f"{ledger_sum:.2f}",
    }

async def import_state(session: AsyncSession, payload: StateImportPayload) -> dict:
    if not session.in_transaction():
        await session.execute(text("BEGIN IMMEDIATE"))
    
    # 1. Clear existing state
    await session.execute(text("DELETE FROM journal_entries"))
    await session.execute(text("DELETE FROM transfers"))
    await session.execute(text("DELETE FROM idempotency_records"))
    await session.execute(text("DELETE FROM wallets"))

    # 2. Insert wallets
    for w in payload.wallets:
        wallet = Wallet(id=w.id, name=w.name or "Imported Wallet")
        session.add(wallet)

    # 3. Insert journal entries
    if payload.journal_entries:
        for entry in payload.journal_entries:
            je = JournalEntry(
                transaction_id=entry.transaction_id,
                wallet_id=entry.wallet_id,
                amount=entry.amount,
                entry_type=entry.entry_type,
            )
            session.add(je)
    elif any(w.balance for w in payload.wallets):
        # Synthetic seeding if balances provided directly
        for w in payload.wallets:
            if w.balance and Decimal(w.balance) > Decimal("0.00"):
                je = JournalEntry(
                    transaction_id=f"SEED_{w.id}",
                    wallet_id=w.id,
                    amount=w.balance,
                    entry_type="CREDIT",
                )
                session.add(je)

    await session.flush()

    # 4. Invariant Verification: SUM == 0 (or balanced seed)
    res = await session.execute(select(JournalEntry.amount))
    total_sum = Decimal("0.00")
    for amt in res.scalars().all():
        total_sum += Decimal(amt)

    if payload.journal_entries and total_sum != Decimal("0.00"):
        await session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"State import violates zero-sum invariant: ledger sum={total_sum:.2f} != 0.00"
        )

    await session.commit()
    return {"imported_wallets": len(payload.wallets), "status": "success"}
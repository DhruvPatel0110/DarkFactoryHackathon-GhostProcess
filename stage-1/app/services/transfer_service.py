import asyncio
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from app.models import Wallet, Transfer, JournalEntry, IdempotencyRecord
from app.services.wallet_service import compute_wallet_balance

_transfer_locks = {}

def get_transfer_lock() -> asyncio.Lock:
    loop = asyncio.get_running_loop()
    if loop not in _transfer_locks:
        _transfer_locks[loop] = asyncio.Lock()
    return _transfer_locks[loop]

async def execute_transfer(
    session: AsyncSession,
    idempotency_key: str,
    source_wallet_id: str,
    dest_wallet_id: str,
    amount_str: str,
) -> tuple[int, dict]:
    # 1. Validation checks
    if source_wallet_id == dest_wallet_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same wallet (self-transfer prohibited)")

    transfer_amount = Decimal(amount_str)
    if transfer_amount <= Decimal("0.00"):
        raise HTTPException(status_code=400, detail="Transfer amount must be positive")

    # 2. Acquire lock & immediate transaction before state checks to eliminate TOCTOU / double-spend races
    lock = get_transfer_lock()
    async with lock:
        if not session.in_transaction():
            await session.execute(text("BEGIN IMMEDIATE"))

        # Check idempotency inside the lock
        stmt_idem = select(IdempotencyRecord).where(IdempotencyRecord.key == idempotency_key)
        existing_idem = (await session.execute(stmt_idem)).scalar_one_or_none()
        if existing_idem:
            return existing_idem.status_code, json.loads(existing_idem.response_body)

        # Verify both wallets exist
        src_wallet = (await session.execute(select(Wallet).where(Wallet.id == source_wallet_id))).scalar_one_or_none()
        dst_wallet = (await session.execute(select(Wallet).where(Wallet.id == dest_wallet_id))).scalar_one_or_none()

        if not src_wallet or not dst_wallet:
            raise HTTPException(status_code=404, detail="Source or destination wallet not found")

        # Verify sufficient balance
        current_balance = await compute_wallet_balance(session, source_wallet_id)
        if current_balance < transfer_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient funds: available {current_balance:.2f}, required {transfer_amount:.2f}"
            )

        now_ts = datetime.now(timezone.utc).isoformat()
        # Create transfer record
        transfer_id = f"txn_{uuid.uuid4().hex[:12]}"
        transfer = Transfer(
            id=transfer_id,
            idempotency_key=idempotency_key,
            source_wallet_id=source_wallet_id,
            dest_wallet_id=dest_wallet_id,
            amount=amount_str,
            status="COMPLETED",
            created_at=now_ts,
        )
        session.add(transfer)

        # Double-entry bookkeeping: exactly 1 DEBIT and exactly 1 CREDIT
        debit_entry = JournalEntry(
            transaction_id=transfer_id,
            wallet_id=source_wallet_id,
            amount=f"-{amount_str}",
            entry_type="DEBIT",
            created_at=now_ts,
        )
        credit_entry = JournalEntry(
            transaction_id=transfer_id,
            wallet_id=dest_wallet_id,
            amount=f"{amount_str}",
            entry_type="CREDIT",
            created_at=now_ts,
        )
        session.add(debit_entry)
        session.add(credit_entry)

        response_payload = {
            "id": transfer.id,
            "idempotency_key": transfer.idempotency_key,
            "source_wallet_id": transfer.source_wallet_id,
            "destination_wallet_id": transfer.dest_wallet_id,
            "amount": transfer.amount,
            "status": transfer.status,
            "created_at": transfer.created_at,
        }

        # Store idempotency record
        idem_rec = IdempotencyRecord(
            key=idempotency_key,
            status_code=201,
            response_body=json.dumps(response_payload),
            created_at=now_ts,
        )
        session.add(idem_rec)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            # Concurrent duplicate key insertion race condition handled
            existing = (await session.execute(select(IdempotencyRecord).where(IdempotencyRecord.key == idempotency_key))).scalar_one()
            return existing.status_code, json.loads(existing.response_body)

        return 201, response_payload
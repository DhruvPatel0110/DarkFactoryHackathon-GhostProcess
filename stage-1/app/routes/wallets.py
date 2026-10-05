import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import IdempotencyRecord
from app.schemas import WalletCreateRequest, WalletResponse
from app.services.wallet_service import create_wallet, get_wallet, list_wallets, compute_wallet_balance

router = APIRouter(prefix="/wallets", tags=["Wallets"])

@router.post("", response_model=WalletResponse, status_code=201)
async def create_wallet_endpoint(req: WalletCreateRequest, db: AsyncSession = Depends(get_db)):
    if req.idempotency_key:
        stmt = select(IdempotencyRecord).where(IdempotencyRecord.key == req.idempotency_key)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            return WalletResponse(**json.loads(existing.response_body))

    wallet = await create_wallet(db, req.name or "Wallet")
    balance = await compute_wallet_balance(db, wallet.id)
    resp = WalletResponse(
        id=wallet.id,
        name=wallet.name,
        balance=f"{balance:.2f}",
        created_at=wallet.created_at,
    )

    if req.idempotency_key:
        now_ts = datetime.now(timezone.utc).isoformat()
        idem = IdempotencyRecord(
            key=req.idempotency_key,
            status_code=201,
            response_body=json.dumps(resp.model_dump()),
            created_at=now_ts,
        )
        db.add(idem)
        await db.commit()

    return resp

@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet_endpoint(wallet_id: str, db: AsyncSession = Depends(get_db)):
    wallet = await get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    balance = await compute_wallet_balance(db, wallet.id)
    return WalletResponse(
        id=wallet.id,
        name=wallet.name,
        balance=f"{balance:.2f}",
        created_at=wallet.created_at,
    )

@router.get("", response_model=list[WalletResponse])
async def list_wallets_endpoint(db: AsyncSession = Depends(get_db)):
    wallets = await list_wallets(db)
    res = []
    for w in wallets:
        bal = await compute_wallet_balance(db, w.id)
        res.append(WalletResponse(
            id=w.id,
            name=w.name,
            balance=f"{bal:.2f}",
            created_at=w.created_at,
        ))
    return res
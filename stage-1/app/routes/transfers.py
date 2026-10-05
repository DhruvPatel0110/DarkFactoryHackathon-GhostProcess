from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Transfer
from app.schemas import TransferCreateRequest, TransferResponse
from app.services.transfer_service import execute_transfer

router = APIRouter(prefix="/transfers", tags=["Transfers"])

@router.post("", response_model=TransferResponse)
async def create_transfer_endpoint(req: TransferCreateRequest, response: Response, db: AsyncSession = Depends(get_db)):
    status_code, payload = await execute_transfer(
        db,
        idempotency_key=req.idempotency_key,
        source_wallet_id=req.source_wallet_id,
        dest_wallet_id=req.destination_wallet_id,
        amount_str=req.amount,
    )
    response.status_code = status_code
    return payload

@router.get("/{transfer_id}", response_model=TransferResponse)
async def get_transfer_endpoint(transfer_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Transfer).where(Transfer.id == transfer_id)
    transfer = (await db.execute(stmt)).scalar_one_or_none()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return TransferResponse(
        id=transfer.id,
        idempotency_key=transfer.idempotency_key,
        source_wallet_id=transfer.source_wallet_id,
        destination_wallet_id=transfer.dest_wallet_id,
        amount=transfer.amount,
        status=transfer.status,
        created_at=transfer.created_at,
    )

@router.get("", response_model=list[TransferResponse])
async def list_transfers_endpoint(
    wallet_id: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Transfer)
    if wallet_id:
        stmt = stmt.where((Transfer.source_wallet_id == wallet_id) | (Transfer.dest_wallet_id == wallet_id))
    stmt = stmt.order_by(Transfer.created_at.desc()).limit(limit).offset(offset)
    transfers = (await db.execute(stmt)).scalars().all()
    return [
        TransferResponse(
            id=t.id,
            idempotency_key=t.idempotency_key,
            source_wallet_id=t.source_wallet_id,
            destination_wallet_id=t.dest_wallet_id,
            amount=t.amount,
            status=t.status,
            created_at=t.created_at,
        ) for t in transfers
    ]
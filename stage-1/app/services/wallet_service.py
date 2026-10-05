from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Wallet, JournalEntry
import uuid

async def compute_wallet_balance(session: AsyncSession, wallet_id: str) -> Decimal:
    stmt = select(JournalEntry.amount).where(JournalEntry.wallet_id == wallet_id)
    result = await session.execute(stmt)
    entries = result.scalars().all()
    
    total = Decimal("0.00")
    for amt in entries:
        total += Decimal(amt)
    return total

async def create_wallet(session: AsyncSession, name: str) -> Wallet:
    wallet_id = f"w_{uuid.uuid4().hex[:12]}"
    wallet = Wallet(id=wallet_id, name=name)
    session.add(wallet)
    await session.commit()
    await session.refresh(wallet)
    return wallet

async def get_wallet(session: AsyncSession, wallet_id: str) -> Wallet | None:
    stmt = select(Wallet).where(Wallet.id == wallet_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def list_wallets(session: AsyncSession) -> list[Wallet]:
    stmt = select(Wallet)
    result = await session.execute(stmt)
    return list(result.scalars().all())
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

def utcnow_str():
    return datetime.now(timezone.utc).isoformat()

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    created_at = Column(String(64), default=utcnow_str, nullable=False)
    updated_at = Column(String(64), default=utcnow_str, onupdate=utcnow_str, nullable=False)

    journal_entries = relationship("JournalEntry", back_populates="wallet", cascade="all, delete-orphan")

class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(String(64), primary_key=True, index=True)
    idempotency_key = Column(String(128), unique=True, nullable=False, index=True)
    source_wallet_id = Column(String(64), ForeignKey("wallets.id"), nullable=False)
    dest_wallet_id = Column(String(64), ForeignKey("wallets.id"), nullable=False)
    amount = Column(String(64), nullable=False)  # Stored as exact decimal string e.g. "50.00"
    status = Column(String(32), default="COMPLETED", nullable=False)
    created_at = Column(String(64), default=utcnow_str, nullable=False)

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(64), nullable=False, index=True)
    wallet_id = Column(String(64), ForeignKey("wallets.id"), nullable=False, index=True)
    amount = Column(String(64), nullable=False)  # Signed decimal string e.g. "-50.00" or "+50.00"
    entry_type = Column(String(16), nullable=False)  # DEBIT or CREDIT
    created_at = Column(String(64), default=utcnow_str, nullable=False)

    wallet = relationship("Wallet", back_populates="journal_entries")

class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    key = Column(String(128), primary_key=True, index=True)
    status_code = Column(Integer, nullable=False)
    response_body = Column(Text, nullable=False)
    created_at = Column(String(64), default=utcnow_str, nullable=False)
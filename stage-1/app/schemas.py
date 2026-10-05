import re
from decimal import Decimal, InvalidOperation
from typing import Optional, List
from pydantic import BaseModel, field_validator, ConfigDict

def parse_and_validate_amount(v: str) -> str:
    if not isinstance(v, str):
        v = str(v)
    v = v.strip()
    # Reject scientific notation, negative numbers, symbols, and malformed strings
    if not re.match(r"^\d+(\.\d+)?$", v):
        raise ValueError("Amount must be a valid positive numeric decimal string without scientific notation or symbols")

    # Reject more than 2 decimal places (do not silently round)
    parts = v.split(".")
    if len(parts) == 2 and len(parts[1]) > 2:
        raise ValueError("Amount must have at most 2 decimal places (no sub-cent precision)")

    try:
        d = Decimal(v)
    except InvalidOperation:
        raise ValueError("Amount must be a valid numeric decimal string")
    
    if d <= Decimal("0.00"):
        raise ValueError("Amount must be strictly positive (> 0.00)")

    # Normalize to exactly 2 decimal places e.g. "10.1" -> "10.10"
    return f"{d:.2f}"

class WalletCreateRequest(BaseModel):
    name: Optional[str] = "Unnamed Wallet"
    idempotency_key: Optional[str] = None

class WalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: Optional[str]
    balance: str
    created_at: str

class TransferCreateRequest(BaseModel):
    idempotency_key: str
    source_wallet_id: str
    destination_wallet_id: str
    amount: str

    @field_validator("amount")
    @classmethod
    def validate_amount_field(cls, v):
        return parse_and_validate_amount(v)

class TransferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    idempotency_key: str
    source_wallet_id: str
    destination_wallet_id: str
    amount: str
    status: str
    created_at: str

class WalletImportItem(BaseModel):
    id: str
    name: Optional[str] = None
    balance: Optional[str] = None

class JournalImportItem(BaseModel):
    transaction_id: str
    wallet_id: str
    amount: str
    entry_type: str

class StateImportPayload(BaseModel):
    wallets: List[WalletImportItem]
    transfers: Optional[List[dict]] = []
    journal_entries: Optional[List[JournalImportItem]] = []

class StateExportResponse(BaseModel):
    wallets: List[WalletResponse]
    transfers: List[dict]
    journal_entries: List[dict]
    ledger_sum: str
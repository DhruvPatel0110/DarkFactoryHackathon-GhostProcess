from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import StateImportPayload, StateExportResponse
from app.services.state_service import reset_state, export_state, import_state

router = APIRouter(prefix="/state", tags=["State Harness"])

@router.post("/reset")
async def reset_endpoint(db: AsyncSession = Depends(get_db)):
    await reset_state(db)
    return {"status": "reset_successful"}

@router.get("/export", response_model=StateExportResponse)
async def export_endpoint(db: AsyncSession = Depends(get_db)):
    return await export_state(db)

@router.post("/import")
async def import_endpoint(payload: StateImportPayload, db: AsyncSession = Depends(get_db)):
    return await import_state(db, payload)
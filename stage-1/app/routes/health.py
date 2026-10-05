from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ghostprocess-pocketful",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
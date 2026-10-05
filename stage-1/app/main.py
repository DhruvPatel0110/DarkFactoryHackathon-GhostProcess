from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.database import engine, Base
from app.routes import health, wallets, transfers, state

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-initialize database tables on container / server startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="GhostProcess Pocketful Engine",
    description="Venmo-like Clean-Room Wallet & Double-Entry Payment Ledger",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []
    for err in exc.errors():
        formatted_errors.append({
            "type": err.get("type"),
            "loc": list(err.get("loc", [])),
            "msg": str(err.get("msg", "")),
            "input": str(err.get("input", "")),
        })
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Validation error: invalid request payload or precision violation",
            "errors": formatted_errors,
        },
    )

# Include route controllers
app.include_router(health.router)
app.include_router(wallets.router)
app.include_router(transfers.router)
app.include_router(state.router)
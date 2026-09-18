from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.deps import DbSession
from app.api.routes.guest import router as guest_router
from app.api.routes.host import router as host_router
from app.config import settings
from app.services.waitlist_service import WaitlistCallConflictError, WaitlistEntryNotFoundError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield  # startup goes before yield, shutdown after — nothing needed yet


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(guest_router)
    app.include_router(host_router)

    @app.exception_handler(WaitlistEntryNotFoundError)
    async def waitlist_entry_not_found_handler(
        request: Request, exc: WaitlistEntryNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": "waitlist entry not found"})

    @app.exception_handler(WaitlistCallConflictError)
    async def waitlist_call_conflict_handler(
        request: Request, exc: WaitlistCallConflictError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": "entry already called, seated, or not found in this restaurant"},
        )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    async def ready(db: DbSession) -> dict[str, str]:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}

    return app


app = create_app()

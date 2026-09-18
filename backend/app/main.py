from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api.deps import DbSession


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield  # startup goes before yield, shutdown after — nothing needed yet


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    async def ready(db: DbSession) -> dict[str, str]:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}

    return app


app = create_app()

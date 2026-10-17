from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from virtual_office.settings import Settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    # Startup and shutdown hooks (database, catalog client, orchestrator) arrive in later WPs.
    yield


def create_app(settings: Settings) -> FastAPI:
    """Build the core API around injected settings; routes are added by later stories."""
    app = FastAPI(title="Virtual Office core", lifespan=lifespan)
    app.state.settings = settings
    return app

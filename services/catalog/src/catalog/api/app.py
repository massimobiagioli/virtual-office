from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from catalog.settings import Settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Startup and shutdown hooks (database, catalog seed check) arrive in later WPs.
    yield


def create_app(settings: Settings) -> FastAPI:
    """Build the catalog API around injected settings; routes are added by later stories."""
    app = FastAPI(title="Virtual Office catalog", lifespan=lifespan)
    app.state.settings = settings
    return app

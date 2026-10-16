from fastapi import FastAPI

from agents_catalog.api import app as api_app
from agents_catalog.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Uvicorn factory (`--factory`): settings are read from the environment when not given."""
    return api_app.create_app(settings if settings is not None else Settings())

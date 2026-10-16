from fastapi import FastAPI

from virtual_office.api import app as api_app
from virtual_office.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Uvicorn factory (`--factory`): settings are read from the environment when not given."""
    return api_app.create_app(settings if settings is not None else Settings())

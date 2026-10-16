import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute

from virtual_office.main import create_app
from virtual_office.settings import Settings

SETTINGS = Settings(
    database_url="postgresql+asyncpg://core_app@postgres:5432/core",
    catalog_url="http://agents-catalog:8001/",
    ollama_base_url="http://ollama:11434/",
)


def test_app_factory_returns_a_fastapi_app_without_api_routes() -> None:
    app = create_app(SETTINGS)

    assert isinstance(app, FastAPI)
    assert [route for route in app.routes if isinstance(route, APIRoute)] == []


def test_app_factory_keeps_the_injected_settings() -> None:
    app = create_app(SETTINGS)

    assert app.state.settings is SETTINGS


def test_app_factory_reads_settings_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VO_DATABASE_URL", "postgresql+asyncpg://core_app@postgres:5432/core")
    monkeypatch.setenv("VO_CATALOG_URL", "http://agents-catalog:8001/")
    monkeypatch.setenv("VO_OLLAMA_BASE_URL", "http://ollama:11434/")

    app = create_app()

    assert app.state.settings == SETTINGS

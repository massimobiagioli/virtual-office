import asyncio

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute

from catalog.main import create_app
from catalog.settings import Settings


def test_app_factory_returns_a_fastapi_app_without_api_routes(settings: Settings) -> None:
    app = create_app(settings)

    assert isinstance(app, FastAPI)
    assert [route for route in app.routes if isinstance(route, APIRoute)] == []


def test_app_factory_keeps_the_injected_settings(settings: Settings) -> None:
    app = create_app(settings)

    assert app.state.settings is settings


@pytest.mark.usefixtures("catalog_environment")
def test_app_factory_reads_settings_from_the_environment(settings: Settings) -> None:
    app = create_app()

    assert app.state.settings == settings


def test_app_lifespan_starts_and_stops(settings: Settings) -> None:
    app = create_app(settings)
    phases: list[str] = []

    async def run_lifespan() -> None:
        async with app.router.lifespan_context(app):
            phases.append("running")
        phases.append("stopped")

    asyncio.run(run_lifespan())

    assert phases == ["running", "stopped"]

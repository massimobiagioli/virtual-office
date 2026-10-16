import pytest

from catalog.settings import Settings

REQUIRED_ENVIRONMENT = {
    "VO_DATABASE_URL": "postgresql+asyncpg://catalog_app@postgres:5432/catalog",
}
OPTIONAL_VARIABLES = ("VO_LOG_LEVEL",)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Async tests run on asyncio only (BACKEND.md §11)."""
    return "asyncio"


@pytest.fixture
def no_catalog_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """No `VO_*` variable is set, whatever the ambient environment holds."""
    for name in (*REQUIRED_ENVIRONMENT, *OPTIONAL_VARIABLES):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def catalog_environment(
    no_catalog_environment: None, monkeypatch: pytest.MonkeyPatch
) -> dict[str, str]:
    """Exactly the required `VO_*` variables, so ambient optional variables never leak in."""
    for name, value in REQUIRED_ENVIRONMENT.items():
        monkeypatch.setenv(name, value)
    return REQUIRED_ENVIRONMENT


@pytest.fixture
def settings() -> Settings:
    return Settings(database_url=REQUIRED_ENVIRONMENT["VO_DATABASE_URL"], log_level="INFO")

import pytest

from virtual_office.settings import Settings

REQUIRED_ENVIRONMENT = {
    "VO_DATABASE_URL": "postgresql+asyncpg://core_app@postgres:5432/core",
    "VO_CATALOG_URL": "http://agents-catalog:8001/",
    "VO_OLLAMA_BASE_URL": "http://ollama:11434/",
}
OPTIONAL_VARIABLES = ("VO_LOG_LEVEL",)


@pytest.fixture
def no_core_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """No `VO_*` variable is set, whatever the ambient environment holds."""
    for name in (*REQUIRED_ENVIRONMENT, *OPTIONAL_VARIABLES):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def core_environment(no_core_environment: None, monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Exactly the required `VO_*` variables, so ambient optional variables never leak in."""
    for name, value in REQUIRED_ENVIRONMENT.items():
        monkeypatch.setenv(name, value)
    return REQUIRED_ENVIRONMENT


@pytest.fixture
def settings() -> Settings:
    return Settings(
        database_url=REQUIRED_ENVIRONMENT["VO_DATABASE_URL"],
        catalog_url=REQUIRED_ENVIRONMENT["VO_CATALOG_URL"],
        ollama_base_url=REQUIRED_ENVIRONMENT["VO_OLLAMA_BASE_URL"],
        log_level="INFO",
    )

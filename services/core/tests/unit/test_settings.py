import pytest
from pydantic import ValidationError

from virtual_office.settings import Settings

REQUIRED = ("VO_DATABASE_URL", "VO_CATALOG_URL", "VO_OLLAMA_BASE_URL")


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (*REQUIRED, "VO_LOG_LEVEL"):
        monkeypatch.delenv(name, raising=False)


def test_missing_variables_are_named_in_the_error() -> None:
    with pytest.raises(ValidationError) as error:
        Settings()

    message = str(error.value)
    for name in REQUIRED:
        assert name in message


def test_settings_load_from_vo_prefixed_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VO_DATABASE_URL", "postgresql+asyncpg://core_app@postgres:5432/core")
    monkeypatch.setenv("VO_CATALOG_URL", "http://agents-catalog:8001/")
    monkeypatch.setenv("VO_OLLAMA_BASE_URL", "http://ollama:11434/")

    settings = Settings()

    assert str(settings.catalog_url) == "http://agents-catalog:8001/"
    assert settings.log_level == "INFO"


def test_settings_are_frozen(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in REQUIRED:
        monkeypatch.setenv(name, "http://example.test/")
    monkeypatch.setenv("VO_DATABASE_URL", "postgresql+asyncpg://core_app@postgres:5432/core")
    settings = Settings()

    with pytest.raises(ValidationError):
        settings.log_level = "DEBUG"  # type: ignore[misc]  # assigning to a frozen model on purpose

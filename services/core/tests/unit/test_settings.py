import pytest
from pydantic import ValidationError

from virtual_office.settings import Settings


@pytest.mark.usefixtures("no_core_environment")
def test_missing_variables_are_named_in_the_error() -> None:
    with pytest.raises(ValidationError) as error:
        Settings()

    message = str(error.value)
    for name in ("VO_DATABASE_URL", "VO_CATALOG_URL", "VO_OLLAMA_BASE_URL"):
        assert name in message


def test_settings_load_from_vo_prefixed_variables(core_environment: dict[str, str]) -> None:
    settings = Settings()

    assert str(settings.database_url) == core_environment["VO_DATABASE_URL"]
    assert str(settings.catalog_url) == core_environment["VO_CATALOG_URL"]
    assert str(settings.ollama_base_url) == core_environment["VO_OLLAMA_BASE_URL"]
    assert settings.log_level == "INFO"


@pytest.mark.usefixtures("core_environment")
def test_optional_log_level_is_read_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VO_LOG_LEVEL", "DEBUG")

    assert Settings().log_level == "DEBUG"


@pytest.mark.usefixtures("core_environment")
def test_settings_are_frozen() -> None:
    settings = Settings()

    with pytest.raises(ValidationError):
        settings.log_level = "DEBUG"  # type: ignore[misc]  # assigning to a frozen model on purpose

import pytest
from pydantic import ValidationError

from catalog.settings import Settings


@pytest.mark.usefixtures("no_catalog_environment")
def test_missing_variables_are_named_in_the_error() -> None:
    with pytest.raises(ValidationError) as error:
        Settings()

    assert "VO_DATABASE_URL" in str(error.value)


def test_settings_load_from_vo_prefixed_variables(catalog_environment: dict[str, str]) -> None:
    settings = Settings()

    assert str(settings.database_url) == catalog_environment["VO_DATABASE_URL"]
    assert settings.log_level == "INFO"


@pytest.mark.usefixtures("catalog_environment")
def test_optional_log_level_is_read_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VO_LOG_LEVEL", "DEBUG")

    assert Settings().log_level == "DEBUG"


@pytest.mark.usefixtures("catalog_environment")
def test_settings_are_frozen() -> None:
    settings = Settings()

    with pytest.raises(ValidationError):
        settings.log_level = "DEBUG"  # type: ignore[misc]  # assigning to a frozen model on purpose

from typing import Literal

from pydantic import AliasGenerator, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PREFIX = "VO_"


def _env_name(field_name: str) -> str:
    return f"{ENV_PREFIX}{field_name.upper()}"


class Settings(BaseSettings):
    """Configuration of the agents-catalog service, read from `VO_*` environment variables only.

    Each field's validation alias is its environment variable name, so a validation error
    names the variable to set (`VO_DATABASE_URL`), not the Python field.
    """

    model_config = SettingsConfigDict(
        alias_generator=AliasGenerator(validation_alias=_env_name),
        validate_by_name=True,
        extra="forbid",
        frozen=True,
    )

    database_url: PostgresDsn
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

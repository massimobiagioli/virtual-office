from pathlib import Path

import pytest

from check_env_example import main

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

SETTINGS = '''
from pydantic_settings import BaseSettings

ENV_PREFIX = "VO_"


class Settings(BaseSettings):
    """Docstring, not a field."""

    model_config = {"frozen": True}

    database_url: str
    log_level: str = "INFO"
'''

COMPOSE = """
services:
  core:
    image: virtual-office/core:${VO_IMAGE_TAG:-dev}
    environment:
      VO_DATABASE_URL: postgresql+asyncpg://core_app@postgres:5432/core
"""

ENV_EXAMPLE = """# Virtual Office environment.

# Tag of the images built by compose.
VO_IMAGE_TAG=dev

# Database address, set per service by docker-compose.yml.
# VO_DATABASE_URL=postgresql+asyncpg://core_app@postgres:5432/core

# Log level of the services.
VO_LOG_LEVEL=INFO
"""


def write_repository(root: Path, env_example: str | None = ENV_EXAMPLE) -> Path:
    package = root / "services" / "core" / "src" / "core"
    package.mkdir(parents=True)
    (package / "settings.py").write_text(SETTINGS, encoding="utf-8")
    (root / "docker-compose.yml").write_text(COMPOSE, encoding="utf-8")
    if env_example is not None:
        (root / ".env.example").write_text(env_example, encoding="utf-8")
    return root


def test_the_repository_env_example_documents_every_variable() -> None:
    assert main(["--root", str(REPOSITORY_ROOT)]) == 0


def test_the_repository_env_example_never_names_a_floating_tag() -> None:
    # The full `no-latest` check arrives with US-01.09; until then, the word itself is banned.
    text = (REPOSITORY_ROOT / ".env.example").read_text(encoding="utf-8")

    assert "latest" not in text.lower()


def test_passes_when_every_variable_is_documented(tmp_path: Path) -> None:
    root = write_repository(tmp_path)

    assert main(["--root", str(root)]) == 0


def test_fails_when_a_settings_field_is_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = write_repository(tmp_path, ENV_EXAMPLE.replace("VO_LOG_LEVEL=INFO\n", ""))

    assert main(["--root", str(root)]) == 1
    output = capsys.readouterr().out
    assert "services/core/src/core/settings.py:13: VO_LOG_LEVEL" in output
    assert "missing from .env.example" in output


def test_fails_when_a_compose_variable_is_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = write_repository(tmp_path, ENV_EXAMPLE.replace("VO_IMAGE_TAG=dev\n", ""))

    assert main(["--root", str(root)]) == 1
    assert "docker-compose.yml:4: VO_IMAGE_TAG missing" in capsys.readouterr().out


def test_fails_when_a_variable_has_no_comment(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = write_repository(tmp_path, ENV_EXAMPLE.replace("# Log level of the services.\n", ""))

    assert main(["--root", str(root)]) == 1
    assert ".env.example:9: VO_LOG_LEVEL has no comment above it" in capsys.readouterr().out


def test_fails_when_a_documented_variable_is_not_used(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = write_repository(tmp_path, ENV_EXAMPLE + "\n# Some day.\nVO_FUTURE=1\n")

    assert main(["--root", str(root)]) == 1
    output = capsys.readouterr().out
    assert ".env.example:13: VO_FUTURE is not read by any service or compose file" in output


def test_fails_when_a_variable_is_listed_twice(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = write_repository(tmp_path, ENV_EXAMPLE + "\n# Again.\nVO_LOG_LEVEL=DEBUG\n")

    assert main(["--root", str(root)]) == 1
    assert ".env.example:13: VO_LOG_LEVEL is listed twice" in capsys.readouterr().out


def test_fails_when_the_env_example_is_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = write_repository(tmp_path, env_example=None)

    assert main(["--root", str(root)]) == 1
    assert ".env.example: file not found" in capsys.readouterr().out


def test_reads_the_prefix_of_each_settings_module(tmp_path: Path) -> None:
    root = write_repository(tmp_path)
    settings = root / "services" / "core" / "src" / "core" / "settings.py"
    settings.write_text(SETTINGS.replace('"VO_"', '"XX_"'), encoding="utf-8")
    env_example = ENV_EXAMPLE.replace("VO_LOG_LEVEL", "XX_LOG_LEVEL")
    env_example += "\n# Database of core.\nXX_DATABASE_URL=postgresql://core\n"
    (root / ".env.example").write_text(env_example, encoding="utf-8")

    assert main(["--root", str(root)]) == 0


def test_uses_the_vo_prefix_when_a_settings_module_declares_none(tmp_path: Path) -> None:
    root = write_repository(tmp_path)
    settings = root / "services" / "core" / "src" / "core" / "settings.py"
    settings.write_text(SETTINGS.replace('ENV_PREFIX = "VO_"\n', ""), encoding="utf-8")

    assert main(["--root", str(root)]) == 0

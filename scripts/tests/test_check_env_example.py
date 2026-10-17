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
      VO_LOG_LEVEL: ${VO_LOG_LEVEL:-INFO}
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
    for name in ("docker-compose.yml", ".env.example"):
        text = (root / name).read_text(encoding="utf-8")
        text = text.replace("VO_LOG_LEVEL", "XX_LOG_LEVEL")
        text = text.replace("VO_DATABASE_URL", "XX_DATABASE_URL")
        (root / name).write_text(text, encoding="utf-8")

    assert main(["--root", str(root)]) == 0


def test_uses_the_vo_prefix_when_a_settings_module_declares_none(tmp_path: Path) -> None:
    root = write_repository(tmp_path)
    settings = root / "services" / "core" / "src" / "core" / "settings.py"
    settings.write_text(SETTINGS.replace('ENV_PREFIX = "VO_"\n', ""), encoding="utf-8")

    assert main(["--root", str(root)]) == 0


@pytest.mark.parametrize("comment", ["#", "# ", "# ...", "# --- Section ---", "# ===="])
def test_fails_when_the_comment_above_has_no_text(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], comment: str
) -> None:
    env_example = ENV_EXAMPLE.replace("# Log level of the services.", comment)
    root = write_repository(tmp_path, env_example)

    assert main(["--root", str(root)]) == 1
    assert ".env.example:10: VO_LOG_LEVEL has no comment above it" in capsys.readouterr().out


def test_accepts_a_comment_block_that_ends_with_a_ruler_after_its_text(tmp_path: Path) -> None:
    env_example = ENV_EXAMPLE.replace(
        "# Log level of the services.\n", "# Log level of the services.\n# ----\n"
    )
    root = write_repository(tmp_path, env_example)

    assert main(["--root", str(root)]) == 0


def test_a_commented_assignment_that_is_not_a_vo_name_is_a_comment(tmp_path: Path) -> None:
    env_example = ENV_EXAMPLE.replace("# Log level of the services.", "# NOTE=see STACK.md")
    root = write_repository(tmp_path, env_example)

    assert main(["--root", str(root)]) == 0


def test_skips_model_config_and_class_variables(tmp_path: Path) -> None:
    root = write_repository(tmp_path)
    settings = root / "services" / "core" / "src" / "core" / "settings.py"
    settings.write_text(
        SETTINGS.replace(
            'model_config = {"frozen": True}',
            'model_config: SettingsConfigDict = {"frozen": True}\n'
            "    registry: ClassVar[int] = 0\n"
            "    other: typing.ClassVar[int] = 0",
        ),
        encoding="utf-8",
    )

    assert main(["--root", str(root)]) == 0


@pytest.mark.parametrize("keyword", ["alias", "validation_alias"])
def test_reads_a_string_alias_as_is(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], keyword: str
) -> None:
    root = write_repository(tmp_path)
    settings = root / "services" / "core" / "src" / "core" / "settings.py"
    field = f'    anthropic_api_key: str = Field(default="", {keyword}="ANTHROPIC_API_KEY")\n'
    settings.write_text(SETTINGS + field, encoding="utf-8")

    assert main(["--root", str(root)]) == 1
    output = capsys.readouterr().out
    assert "settings.py:14: ANTHROPIC_API_KEY missing from .env.example" in output
    assert "VO_ANTHROPIC_API_KEY" not in output


def test_prefers_the_validation_alias_and_reads_only_field_aliases(tmp_path: Path) -> None:
    root = write_repository(tmp_path)
    settings = root / "services" / "core" / "src" / "core" / "settings.py"
    fields = (
        '    token: str = Field(alias=ALIAS, validation_alias="TOKEN", default=make())\n'
        '    plain: str = compute(alias="IGNORED")\n'
    )
    settings.write_text(SETTINGS + fields, encoding="utf-8")
    compose = COMPOSE + "      TOKEN: ${TOKEN:-}\n      VO_PLAIN: ${VO_PLAIN:-}\n"
    (root / "docker-compose.yml").write_text(compose, encoding="utf-8")
    env_example = ENV_EXAMPLE + "\n# Token.\nTOKEN=x\n# Plain.\nVO_PLAIN=x\n"
    (root / ".env.example").write_text(env_example, encoding="utf-8")

    assert main(["--root", str(root)]) == 0


@pytest.mark.parametrize(
    "alias",
    ['validation_alias=AliasChoices("A", "B")', "alias=NAME", 'validation_alias=NAME, alias="A"'],
)
def test_fails_when_an_alias_is_not_a_string(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], alias: str
) -> None:
    root = write_repository(tmp_path)
    settings = root / "services" / "core" / "src" / "core" / "settings.py"
    settings.write_text(SETTINGS + f"    choice: str = Field({alias})\n", encoding="utf-8")

    assert main(["--root", str(root)]) == 1
    output = capsys.readouterr().out
    assert (
        "services/core/src/core/settings.py:14: choice has an alias the check cannot resolve: "
        "use a string" in output
    )
    assert "missing from .env.example" not in output


def test_requires_every_variable_compose_interpolates(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = write_repository(tmp_path)
    compose = COMPOSE + "  postgres:\n    environment:\n      PGPASSWORD: ${POSTGRES_PASSWORD:?}\n"
    (root / "docker-compose.yml").write_text(compose, encoding="utf-8")

    assert main(["--root", str(root)]) == 1
    assert "docker-compose.yml:10: POSTGRES_PASSWORD missing" in capsys.readouterr().out


def test_ignores_an_escaped_interpolation(tmp_path: Path) -> None:
    root = write_repository(tmp_path)
    compose = COMPOSE + '    command: ["sh", "-c", "echo $${BAR}"]\n'
    (root / "docker-compose.yml").write_text(compose, encoding="utf-8")

    assert main(["--root", str(root)]) == 0


def test_ignores_variables_named_only_in_a_trailing_comment(tmp_path: Path) -> None:
    root = write_repository(tmp_path)
    compose = COMPOSE + "      VO_MODE: dev  # VO_LATER arrives with WP02\n"
    (root / "docker-compose.yml").write_text(compose, encoding="utf-8")
    env_example = ENV_EXAMPLE + "\n# Mode, set by docker-compose.yml.\n# VO_MODE=dev\n"
    (root / ".env.example").write_text(env_example, encoding="utf-8")

    assert main(["--root", str(root)]) == 0


def test_fails_when_an_interpolated_variable_is_commented_out(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = write_repository(tmp_path, ENV_EXAMPLE.replace("VO_IMAGE_TAG=dev", "# VO_IMAGE_TAG=dev"))

    assert main(["--root", str(root)]) == 1
    assert (
        ".env.example:4: VO_IMAGE_TAG is interpolated by compose: list it as NAME=value"
        in capsys.readouterr().out
    )


def test_fails_when_a_variable_compose_fixes_is_not_commented_out(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    env_example = ENV_EXAMPLE.replace("# VO_DATABASE_URL=", "VO_DATABASE_URL=")
    root = write_repository(tmp_path, env_example)

    assert main(["--root", str(root)]) == 1
    assert (
        ".env.example:7: VO_DATABASE_URL is fixed by compose: list it as # NAME=value"
        in capsys.readouterr().out
    )


def test_a_comment_documents_only_the_variable_right_below_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    env_example = ENV_EXAMPLE.replace(
        "VO_IMAGE_TAG=dev\n", "VO_IMAGE_TAG=dev\nVO_LOG_LEVEL=INFO\n"
    ).replace("\n# Log level of the services.\nVO_LOG_LEVEL=INFO\n", "")
    root = write_repository(tmp_path, env_example)

    assert main(["--root", str(root)]) == 1
    output = capsys.readouterr().out
    assert ".env.example:5: VO_LOG_LEVEL has no comment above it" in output
    assert "VO_IMAGE_TAG has no comment" not in output


def test_a_blank_line_separates_a_comment_from_the_variable_below(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    env_example = ENV_EXAMPLE.replace(
        "# Log level of the services.\n", "# Log level of the services.\n\n"
    )
    root = write_repository(tmp_path, env_example)

    assert main(["--root", str(root)]) == 1
    assert ".env.example:11: VO_LOG_LEVEL has no comment above it" in capsys.readouterr().out


@pytest.mark.parametrize("entry", ["VO_EXTRA=x", "# VO_EXTRA=x"])
def test_fails_when_a_settings_variable_is_not_passed_by_compose(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], entry: str
) -> None:
    root = write_repository(tmp_path, ENV_EXAMPLE + f"\n# Extra.\n{entry}\n")
    settings = root / "services" / "core" / "src" / "core" / "settings.py"
    settings.write_text(SETTINGS + '    extra: str = ""\n', encoding="utf-8")

    assert main(["--root", str(root)]) == 1
    assert (
        ".env.example:13: VO_EXTRA is read by a service but not passed by compose"
        in capsys.readouterr().out
    )


def test_a_settings_alias_compose_fixes_is_listed_commented_out(tmp_path: Path) -> None:
    root = write_repository(tmp_path, ENV_EXAMPLE + "\n# Fixed key.\n# API_KEY=fixed\n")
    settings = root / "services" / "core" / "src" / "core" / "settings.py"
    field = '    api_key: str = Field(validation_alias="API_KEY")\n'
    settings.write_text(SETTINGS + field, encoding="utf-8")
    compose = COMPOSE + "      API_KEY: fixed\n"
    (root / "docker-compose.yml").write_text(compose, encoding="utf-8")

    assert main(["--root", str(root)]) == 0

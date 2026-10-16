from pathlib import Path

import pytest

from check_python_pins import main

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

STACK = """# Stack

## 5. Backend services

| Concern | Choice | Version | Notes |
| ------- | ------ | ------- | ----- |
| Runtime | CPython | 3.15.0 | |
| Package/env manager | uv | 0.13.1 | |
| Build backend | uv_build | 0.13.1 | |
| Web framework | FastAPI | 0.143.3 | |
| ASGI server | uvicorn | 0.54.0 | |
| **Agent framework** | **pydantic-ai-slim** | 2.57.0 | |
| Type checking | mypy (strict, pydantic plugin) | 2.4.0 | |

## 6. Models

| Role | Model | Version | Notes |
| ---- | ----- | ------- | ----- |
| PM | ignored | 9.9.9 | |
"""

PYPROJECT = """
[project]
name = "svc"
requires-python = ">=3.15,<3.16"
dependencies = ["fastapi==0.143.3", "uvicorn[standard]==0.54.0", "pydantic-ai-slim[openai]==2.57.0"]

[dependency-groups]
dev = ["mypy==2.4.0"]

[build-system]
requires = ["uv_build==0.13.1"]

[tool.uv]
required-version = "==0.13.1"
"""


def write_repository(root: Path, pyproject: str = PYPROJECT) -> Path:
    (root / ".docs").mkdir()
    (root / ".docs" / "STACK.md").write_text(STACK, encoding="utf-8")
    service = root / "services" / "svc"
    service.mkdir(parents=True)
    (service / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    return root


def test_the_repository_pins_match_the_stack() -> None:
    assert main(["--root", str(REPOSITORY_ROOT)]) == 0


def test_passes_when_every_pin_matches_the_stack(tmp_path: Path) -> None:
    assert main(["--root", str(write_repository(tmp_path))]) == 0


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ('"fastapi==0.143.3"', '"fastapi>=0.143"', "fastapi>=0.143: is not an exact '==' pin"),
        (
            '"fastapi==0.143.3"',
            '"fastapi==0.143.2"',
            "fastapi==0.143.2: pins 0.143.2, STACK.md §5 says 0.143.3",
        ),
        (
            '"mypy==2.4.0"',
            '"mypy==2.4.0", "requests==2.32.5"',
            "requests==2.32.5: is not listed in STACK.md §5",
        ),
        (
            '"uv_build==0.13.1"',
            '"uv_build==0.13.0"',
            "uv_build==0.13.0: pins 0.13.0, STACK.md §5 says 0.13.1",
        ),
        (
            'requires-python = ">=3.15,<3.16"',
            'requires-python = ">=3.14"',
            "requires-python = '>=3.14': expected '>=3.15,<3.16' (STACK.md §5 CPython 3.15.0)",
        ),
        (
            'required-version = "==0.13.1"',
            'required-version = ">=0.13"',
            "[tool.uv] required-version = '>=0.13': expected '==0.13.1' (STACK.md §5 uv)",
        ),
    ],
)
def test_fails_with_file_and_requirement(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], old: str, new: str, message: str
) -> None:
    root = write_repository(tmp_path, PYPROJECT.replace(old, new))

    assert main(["--root", str(root)]) == 1
    assert f"services/svc/pyproject.toml: {message}" in capsys.readouterr().out

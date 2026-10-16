"""The quality tools pass on the service and fire on negative fixtures (US-01.04).

Each fixture is written to a temporary folder at test time, so the service sources never
contain code that breaks a rule. A rule that cannot fail is not a rule (ROADMAP §5.1.5).
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

PACKAGE = "virtual_office"
SERVICE_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = SERVICE_ROOT / "pyproject.toml"

pytestmark = pytest.mark.tooling


def run_tool(*args: str, cwd: Path = SERVICE_ROOT, env: dict[str, str] | None = None) -> str:
    """Run a tool from the service virtualenv; fail the test with its output on a non-zero exit."""
    result = _run(args, cwd, env)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


def run_failing_tool(
    *args: str, cwd: Path = SERVICE_ROOT, env: dict[str, str] | None = None
) -> str:
    """Run a tool expected to reject its input; return everything it printed."""
    result = _run(args, cwd, env)
    assert result.returncode != 0, result.stdout + result.stderr
    return result.stdout + result.stderr


def _run(
    args: tuple[str, ...], cwd: Path, env: dict[str, str] | None
) -> subprocess.CompletedProcess[str]:
    executable = shutil.which(args[0])
    assert executable is not None, f"{args[0]} is not installed in the service virtualenv"
    return subprocess.run(
        [executable, *args[1:]],
        cwd=cwd,
        env={**os.environ, **(env or {})},
        capture_output=True,
        text=True,
        check=False,
    )


def write_fixture(folder: Path, name: str, source: str) -> Path:
    path = folder / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    return path


def test_ruff_passes_on_the_service() -> None:
    run_tool("ruff", "check", "--no-cache", ".")
    run_tool("ruff", "format", "--check", "--no-cache", ".")


def test_ruff_rejects_a_print_call(tmp_path: Path) -> None:
    fixture = write_fixture(tmp_path, "print_call.py", 'print("debug")\n')

    output = run_failing_tool(
        "ruff", "check", "--no-cache", "--config", str(PYPROJECT), str(fixture)
    )

    assert "T201" in output


def test_mypy_passes_on_the_service() -> None:
    run_tool("mypy", "--cache-dir", os.devnull)


def test_mypy_rejects_an_untyped_function(tmp_path: Path) -> None:
    fixture = write_fixture(tmp_path, "untyped_def.py", "def add(a, b):\n    return a + b\n")

    output = run_failing_tool(
        "mypy", "--config-file", str(PYPROJECT), "--cache-dir", os.devnull, str(fixture)
    )

    assert "no-untyped-def" in output


def test_mypy_checks_pydantic_models_with_the_plugin(tmp_path: Path) -> None:
    # Without the pydantic plugin, BaseModel.__init__ accepts any keyword and this passes.
    fixture = write_fixture(
        tmp_path,
        "pydantic_extra_field.py",
        "from pydantic import BaseModel\n\n\nclass Point(BaseModel):\n    x: int\n\n\n"
        "Point(x=1, y=2)\n",
    )

    output = run_failing_tool(
        "mypy", "--config-file", str(PYPROJECT), "--cache-dir", os.devnull, str(fixture)
    )

    assert "call-arg" in output


def test_lint_imports_passes_on_the_service() -> None:
    run_tool("lint-imports", "--no-cache")


def test_lint_imports_rejects_a_domain_module_importing_sqlalchemy(tmp_path: Path) -> None:
    sources = tmp_path / "src"
    shutil.copytree(SERVICE_ROOT / "src", sources)
    write_fixture(sources / PACKAGE / "domain", "uses_sqlalchemy.py", "import sqlalchemy\n")

    output = run_failing_tool(
        "lint-imports",
        "--no-cache",
        "--config",
        str(PYPROJECT),
        cwd=tmp_path,
        env={"PYTHONPATH": str(sources)},
    )

    assert f"{PACKAGE}.domain.uses_sqlalchemy -> sqlalchemy" in output

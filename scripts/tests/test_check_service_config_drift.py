from pathlib import Path

import pytest

from check_service_config_drift import main

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

CORE = """
[tool.uv]
required-version = "==0.13.1"

[tool.uv.build-backend]
module-name = "virtual_office"

[tool.ruff]
line-length = 100
src = ["src", "tests"]

[tool.coverage.run]
source_pkgs = ["virtual_office"]

[tool.importlinter]
root_packages = ["virtual_office"]

[[tool.importlinter.contracts]]
name = "Bounded contexts are independent"
type = "independence"
modules = ["virtual_office.domain.kanban", "virtual_office.domain.staff"]
"""


def write_services(root: Path, catalog: str) -> Path:
    for name, content in (("core", CORE), ("catalog", catalog)):
        service = root / "services" / name
        service.mkdir(parents=True)
        (service / "pyproject.toml").write_text(content, encoding="utf-8")
    return root


def catalog_from_core() -> str:
    """The catalog configuration: the core one with its own package and contracts."""
    tools = CORE[: CORE.index("[[tool.importlinter.contracts]]")]
    return tools.replace("virtual_office", "catalog")


def test_the_repository_services_do_not_drift() -> None:
    assert main(["--root", str(REPOSITORY_ROOT)]) == 0


def test_passes_when_only_package_names_and_contracts_differ(tmp_path: Path) -> None:
    root = write_services(tmp_path, catalog_from_core())

    assert main(["--root", str(root)]) == 0


def test_fails_when_a_tool_setting_differs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = write_services(
        tmp_path, catalog_from_core().replace("line-length = 100", "line-length = 120")
    )

    assert main(["--root", str(root)]) == 1
    output = capsys.readouterr().out
    assert "tool.ruff.line-length" in output
    assert "services/core=100" in output
    assert "services/catalog=120" in output


def test_fails_when_a_tool_setting_is_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = write_services(tmp_path, catalog_from_core().replace('src = ["src", "tests"]\n', ""))

    assert main(["--root", str(root)]) == 1
    assert "tool.ruff.src" in capsys.readouterr().out


def test_fails_when_a_package_name_is_hard_coded(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    drifted = catalog_from_core().replace(
        'source_pkgs = ["catalog"]', 'source_pkgs = ["virtual_office"]'
    )
    root = write_services(tmp_path, drifted)

    assert main(["--root", str(root)]) == 1
    assert "tool.coverage.run.source_pkgs" in capsys.readouterr().out

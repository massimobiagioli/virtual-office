"""Fail when a Python service pin differs from STACK.md §5 (version policy, STACK.md §1).

Checked in every `services/*/pyproject.toml`: `requires-python` is the CPython minor,
`[tool.uv] required-version` is the uv version, and every requirement in `[project]
dependencies`, `[dependency-groups]` and `[build-system] requires` is an exact `==` pin of
the version listed in STACK.md §5.

Usage: python -I scripts/check_python_pins.py [--root REPOSITORY_ROOT]
"""

import argparse
import re
import sys
import tomllib
from pathlib import Path

SECTION = re.compile(r"^## 5\. .*?(?=^## )", re.MULTILINE | re.DOTALL)
VERSION = re.compile(r"^\d+(\.\d+)*$")
REQUIREMENT = re.compile(r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)(\[[^\]]*\])?\s*(?P<spec>.*)$")
EXACT_PIN = re.compile(r"^==\s*(?P<version>[^\s,;]+)$")
TABLE_COLUMNS = 3  # | Concern | Choice | Version | … |


def canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def stack_versions(stack: Path) -> dict[str, str]:
    """Package → version from the tables of STACK.md §5 (`| Concern | Choice | Version | … |`)."""
    match = SECTION.search(stack.read_text(encoding="utf-8") + "\n## ")
    versions: dict[str, str] = {}
    for line in match.group(0).splitlines() if match else []:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= TABLE_COLUMNS and VERSION.match(cells[2]):
            choice = cells[1].replace("*", "").split(" ")[0]
            versions[canonical(choice)] = cells[2]
    return versions


def check_requirement(requirement: str, versions: dict[str, str]) -> str | None:
    match = REQUIREMENT.match(requirement.strip())
    if match is None:
        return f"{requirement}: cannot be parsed"
    pin = EXACT_PIN.match(match.group("spec"))
    if pin is None:
        return f"{requirement}: is not an exact '==' pin"
    expected = versions.get(canonical(match.group("name")))
    if expected is None:
        return f"{requirement}: is not listed in STACK.md §5"
    if pin.group("version") != expected:
        return f"{requirement}: pins {pin.group('version')}, STACK.md §5 says {expected}"
    return None


def check_service(pyproject: Path, versions: dict[str, str]) -> list[str]:
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    problems: list[str] = []

    major, minor = versions["cpython"].split(".")[:2]
    expected_python = f">={major}.{minor},<{major}.{int(minor) + 1}"
    requires_python = data.get("project", {}).get("requires-python")
    if requires_python != expected_python:
        problems.append(
            f"requires-python = {requires_python!r}: expected {expected_python!r} "
            f"(STACK.md §5 CPython {versions['cpython']})"
        )

    expected_uv = f"=={versions['uv']}"
    required_uv = data.get("tool", {}).get("uv", {}).get("required-version")
    if required_uv != expected_uv:
        problems.append(
            f"[tool.uv] required-version = {required_uv!r}: expected {expected_uv!r} "
            "(STACK.md §5 uv)"
        )

    requirements = [
        *data.get("project", {}).get("dependencies", []),
        *data.get("build-system", {}).get("requires", []),
    ]
    for group in data.get("dependency-groups", {}).values():
        requirements.extend(item for item in group if isinstance(item, str))
    problems.extend(
        problem
        for requirement in requirements
        if (problem := check_requirement(requirement, versions))
    )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)

    versions = stack_versions(args.root / ".docs" / "STACK.md")
    missing = [name for name in ("cpython", "uv") if name not in versions]
    if missing:
        sys.stdout.write(f".docs/STACK.md: §5 lists no version for {', '.join(missing)}\n")
        return 1

    failed = False
    for pyproject in sorted(args.root.glob("services/*/pyproject.toml")):
        relative = pyproject.relative_to(args.root).as_posix()
        for problem in check_service(pyproject, versions):
            failed = True
            sys.stdout.write(f"{relative}: {problem}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

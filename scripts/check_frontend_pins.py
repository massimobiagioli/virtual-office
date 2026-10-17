"""Fail when a frontend pin differs from STACK.md §3 (version policy, STACK.md §1).

Checked in `frontend/package.json`: every entry of `dependencies` and `devDependencies` is an
exact version (no `^`, `~` or range) equal to the version listed in STACK.md §3,
`packageManager` is `pnpm@<version>`, and `engines.node` / `engines.pnpm` are the exact Node.js
and pnpm versions.

Usage: python -I scripts/check_frontend_pins.py [--root REPOSITORY_ROOT]
"""

import argparse
import json
import re
import sys
from pathlib import Path

SECTION = re.compile(r"^## 3\. .*?(?=^## )", re.MULTILINE | re.DOTALL)
VERSION = re.compile(r"^\d+(\.\d+)*$")
TABLE_COLUMNS = 3  # | Concern | Choice | Version | … |


def stack_versions(stack: Path) -> dict[str, str]:
    """Package → version from the tables of STACK.md §3 (`| Concern | Choice | Version | … |`).

    A choice cell may name several packages joined by `+` (`Vitest + @vitest/coverage-v8`);
    each takes the row's version. Only the first word of a name counts (`Node.js LTS …`).
    """
    match = SECTION.search(stack.read_text(encoding="utf-8") + "\n## ")
    versions: dict[str, str] = {}
    for line in match.group(0).splitlines() if match else []:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= TABLE_COLUMNS and VERSION.match(cells[2]):
            for choice in cells[1].replace("*", "").split("+"):
                versions[choice.split()[0].lower()] = cells[2]
    return versions


def check_dependency(name: str, spec: str, versions: dict[str, str]) -> str | None:
    if not VERSION.match(spec):
        return f"{name}@{spec}: is not an exact version"
    expected = versions.get(name.lower())
    if expected is None:
        return f"{name}@{spec}: is not listed in STACK.md §3"
    if spec != expected:
        return f"{name}@{spec}: pins {spec}, STACK.md §3 says {expected}"
    return None


def check_package(package: Path, versions: dict[str, str]) -> list[str]:
    data = json.loads(package.read_text(encoding="utf-8"))
    problems: list[str] = []

    expected_manager = f"pnpm@{versions['pnpm']}"
    if data.get("packageManager") != expected_manager:
        problems.append(
            f"packageManager = {data.get('packageManager')!r}: expected {expected_manager!r} "
            "(STACK.md §3 pnpm)"
        )
    engines = data.get("engines", {})
    for engine, label in (("node", "Node.js"), ("pnpm", "pnpm")):
        expected = versions[label.lower()]
        if engines.get(engine) != expected:
            problems.append(
                f"engines.{engine} = {engines.get(engine)!r}: expected {expected!r} "
                f"(STACK.md §3 {label})"
            )

    for group in ("dependencies", "devDependencies"):
        for name, spec in data.get(group, {}).items():
            if problem := check_dependency(name, spec, versions):
                problems.append(problem)
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)

    versions = stack_versions(args.root / ".docs" / "STACK.md")
    missing = [name for name in ("node.js", "pnpm") if name not in versions]
    if missing:
        sys.stdout.write(f".docs/STACK.md: §3 lists no version for {', '.join(missing)}\n")
        return 1

    package = args.root / "frontend" / "package.json"
    problems = check_package(package, versions)
    for problem in problems:
        sys.stdout.write(f"{package.relative_to(args.root).as_posix()}: {problem}\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

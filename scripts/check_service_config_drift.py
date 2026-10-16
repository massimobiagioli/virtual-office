"""Fail when the tool configuration of the Python services drifts (BACKEND.md §1 rule 3).

Every `services/*/pyproject.toml` must hold the same `[tool.*]` sections once each service's
import package name is replaced by a placeholder. Two parts differ by design and are skipped:
`[tool.uv.build-backend] module-name` (the package itself) and `[tool.importlinter]` (contracts
follow each service's layers, BACKEND.md §2.1).

Usage: python -I scripts/check_service_config_drift.py [--root REPOSITORY_ROOT]
"""

import argparse
import sys
import tomllib
from pathlib import Path

PLACEHOLDER = "<package>"
SKIPPED = ("tool.importlinter", "tool.uv.build-backend.module-name")


def flatten(value: object, prefix: str, package: str) -> dict[str, object]:
    """Dotted key → leaf value, with the package name replaced in every string."""
    if isinstance(value, dict):
        flat: dict[str, object] = {}
        for key, item in value.items():
            flat.update(flatten(item, f"{prefix}.{key}", package))
        return flat
    if prefix.startswith(SKIPPED):
        return {}
    return {prefix: normalize(value, package)}


def normalize(value: object, package: str) -> object:
    if isinstance(value, str) and package:
        return value.replace(package, PLACEHOLDER)
    if isinstance(value, list):
        return [normalize(item, package) for item in value]
    return value


def tool_settings(pyproject: Path) -> dict[str, object]:
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    tool = data.get("tool", {})
    package = tool.get("uv", {}).get("build-backend", {}).get("module-name", "")
    return flatten(tool, "tool", package)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)

    services = {
        path.parent.relative_to(args.root).as_posix(): tool_settings(path)
        for path in sorted(args.root.glob("services/*/pyproject.toml"))
    }
    if not services:
        return 0

    reference_name, reference = next(iter(services.items()))
    drift: list[str] = []
    for name, settings in services.items():
        for key in sorted(reference.keys() | settings.keys()):
            ours = settings.get(key, "<missing>")
            theirs = reference.get(key, "<missing>")
            if ours != theirs:
                drift.append(f"{key}: {reference_name}={theirs!s}, {name}={ours!s}\n")

    for line in drift:
        sys.stdout.write(line)
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())

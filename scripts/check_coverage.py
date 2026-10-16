"""Enforce the per-layer coverage thresholds of Constitution §18.2 on a coverage JSON report.

coverage.py has a single `fail_under`; the layer thresholds are checked here on the report
written by `pytest --cov --cov-report=json` (lines and branches together, as coverage.py does).

Usage: python -I scripts/check_coverage.py services/core/coverage.json --package virtual_office
"""

import argparse
import json
import sys
from pathlib import Path, PurePosixPath

THRESHOLDS = {"domain": 95.0, "application": 90.0}
DEFAULT_THRESHOLD = 70.0


def layer_of(path: str, package: str) -> str | None:
    """`src/<package>/<layer>/…` → `<layer>`; modules directly in the package form one group."""
    parts = PurePosixPath(path.replace("\\", "/")).parts
    if package not in parts:
        return None
    rest = parts[parts.index(package) + 1 :]
    if len(rest) > 1:
        return rest[0]
    return f"{package} (top-level modules)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("report", type=Path, help="coverage JSON report")
    parser.add_argument("--package", required=True, help="import package of the service")
    args = parser.parse_args(argv)

    files = json.loads(args.report.read_text(encoding="utf-8"))["files"]
    measured: dict[str, int] = {}
    covered: dict[str, int] = {}
    for path, data in files.items():
        layer = layer_of(path, args.package)
        if layer is None:
            continue
        summary = data["summary"]
        measured[layer] = (
            measured.get(layer, 0) + summary["num_statements"] + summary["num_branches"]
        )
        covered[layer] = (
            covered.get(layer, 0) + summary["covered_lines"] + summary["covered_branches"]
        )

    failed = False
    for layer in sorted(measured):
        if measured[layer] == 0:
            continue
        percent = 100.0 * covered[layer] / measured[layer]
        required = THRESHOLDS.get(layer, DEFAULT_THRESHOLD)
        ok = round(percent, 1) >= required
        failed = failed or not ok
        status = "ok  " if ok else "FAIL"
        sys.stdout.write(f"{status} {layer}: {percent:.1f} % (required {required:.0f} %)\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

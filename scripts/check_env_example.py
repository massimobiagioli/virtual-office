"""Fail when `.env.example` does not document every environment variable (Constitution §15.11).

The variables in use are the fields of every `services/*/src/*/settings.py` `Settings` class
(prefixed with the module's `ENV_PREFIX`) and every `VO_*` name in the root
`docker-compose*.yml` files. `.env.example` must list each of them once, as `NAME=value` or,
for a value compose sets itself, as a commented `# NAME=value`, with a comment line directly
above. A listed variable that nothing reads fails too: variables are added by the story that
starts reading them.

Usage: python -I scripts/check_env_example.py [--root REPOSITORY_ROOT]
"""

import argparse
import ast
import re
import sys
from pathlib import Path

ENV_EXAMPLE = ".env.example"
DEFAULT_PREFIX = "VO_"
COMPOSE_VARIABLE = re.compile(r"\bVO_[A-Z0-9_]+\b")
ENTRY = re.compile(r"^(?:#\s?)?([A-Z][A-Z0-9_]*)=")


def module_prefix(tree: ast.Module) -> str:
    """The string assigned to the module-level `ENV_PREFIX`, or `VO_` without one."""
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and [ast.unparse(target) for target in node.targets] == ["ENV_PREFIX"]
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            return node.value.value
    return DEFAULT_PREFIX


def settings_variables(path: Path, root: Path) -> dict[str, str]:
    """Variable name → `file:line` of the `Settings` field that reads it."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    prefix = module_prefix(tree)
    where = path.relative_to(root).as_posix()
    found: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Settings":
            for field in node.body:
                if isinstance(field, ast.AnnAssign) and isinstance(field.target, ast.Name):
                    found[f"{prefix}{field.target.id.upper()}"] = f"{where}:{field.lineno}"
    return found


def compose_variables(path: Path, root: Path) -> dict[str, str]:
    """Variable name → `file:line` of its first use in a compose file."""
    where = path.relative_to(root).as_posix()
    found: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.lstrip().startswith("#"):
            continue
        for name in COMPOSE_VARIABLE.findall(line):
            found.setdefault(name, f"{where}:{number}")
    return found


def used_variables(root: Path) -> dict[str, str]:
    used: dict[str, str] = {}
    for path in sorted(root.glob("services/*/src/*/settings.py")):
        for name, where in settings_variables(path, root).items():
            used.setdefault(name, where)
    for path in sorted(root.glob("docker-compose*.yml")):
        for name, where in compose_variables(path, root).items():
            used.setdefault(name, where)
    return used


def check(root: Path) -> list[str]:
    env_example = root / ENV_EXAMPLE
    if not env_example.is_file():
        return [f"{ENV_EXAMPLE}: file not found"]

    used = used_variables(root)
    problems: list[str] = []
    listed: set[str] = set()
    previous = ""
    for number, line in enumerate(env_example.read_text(encoding="utf-8").splitlines(), start=1):
        entry = ENTRY.match(line)
        if entry:
            name = entry.group(1)
            where = f"{ENV_EXAMPLE}:{number}: {name}"
            if name in listed:
                problems.append(f"{where} is listed twice")
            listed.add(name)
            if name not in used:
                problems.append(f"{where} is not read by any service or compose file")
            if not previous.startswith("#") or ENTRY.match(previous):
                problems.append(f"{where} has no comment above it")
        previous = line
    problems.extend(
        f"{where}: {name} missing from {ENV_EXAMPLE}"
        for name, where in sorted(used.items())
        if name not in listed
    )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)

    problems = check(args.root)
    for problem in problems:
        sys.stdout.write(f"{problem}\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

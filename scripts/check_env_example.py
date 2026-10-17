"""Fail when `.env.example` does not document every environment variable (Constitution §15.11).

The variables in use are the fields of every `services/*/src/*/settings.py` `Settings` class
(prefixed with the module's `ENV_PREFIX`, or named by a string `validation_alias`/`alias`; any
other alias fails; `model_config` and `ClassVar`s are not fields) and, in the root
`docker-compose*.yml` files, every `VO_*` or `Settings` name and every `${NAME}` interpolation
outside YAML comments. `.env.example` must list each of them once, with comment text directly
above: a variable compose interpolates as `NAME=value`, a variable compose only sets itself as
a commented `# NAME=value`. A `Settings` variable that no compose file passes fails in either
form, because the services never read `.env` (DOCKER.md §2). A listed variable that nothing
reads fails too: variables are added by the story that starts reading them.

Usage: python -I scripts/check_env_example.py [--root REPOSITORY_ROOT]
"""

import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ENV_EXAMPLE = ".env.example"
DEFAULT_PREFIX = "VO_"
ALIAS_KEYWORDS = ("validation_alias", "alias")  # in order of precedence
COMPOSE_NAME = re.compile(r"\b[A-Z][A-Z0-9_]*\b")
INTERPOLATION = re.compile(r"(?<!\$)\$\{([A-Za-z_][A-Za-z0-9_]*)")
YAML_COMMENT = re.compile(r"(?:^|\s)#.*$")
ENTRY = re.compile(r"^(?P<commented>#\s?)?(?P<name>[A-Z][A-Z0-9_]*)=")
RULER = re.compile(r"^[-=*~#]{3}")
LETTER = re.compile(r"[A-Za-z]")


@dataclass
class Usage:
    """Where each variable is read, by whom, and what could not be resolved."""

    where: dict[str, str] = field(default_factory=dict)
    settings: set[str] = field(default_factory=set)
    composed: set[str] = field(default_factory=set)
    interpolated: set[str] = field(default_factory=set)
    problems: list[str] = field(default_factory=list)

    def add(self, name: str, where: str) -> None:
        self.where.setdefault(name, where)


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


def is_class_variable(annotation: ast.expr) -> bool:
    return ast.unparse(annotation).split("[")[0].split(".")[-1] == "ClassVar"


class UnresolvedAliasError(ValueError):
    """A `Field(...)` alias that is not a string literal, so its variable name is unknown."""


def field_alias(value: ast.expr | None) -> str | None:
    """The `validation_alias` (or else `alias`) string of a `Field(...)` default, if any."""
    if not (isinstance(value, ast.Call) and ast.unparse(value.func).split(".")[-1] == "Field"):
        return None
    aliases = {keyword.arg: keyword.value for keyword in value.keywords}
    alias = next((aliases[name] for name in ALIAS_KEYWORDS if name in aliases), None)
    if alias is None:
        return None
    if isinstance(alias, ast.Constant) and isinstance(alias.value, str):
        return alias.value
    raise UnresolvedAliasError


def scan_settings(path: Path, root: Path, usage: Usage) -> None:
    """Record the variable each field of the module's `Settings` class reads."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    prefix = module_prefix(tree)
    where = path.relative_to(root).as_posix()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Settings":
            for item in node.body:
                if (
                    isinstance(item, ast.AnnAssign)
                    and isinstance(item.target, ast.Name)
                    and item.target.id != "model_config"
                    and not is_class_variable(item.annotation)
                ):
                    try:
                        alias = field_alias(item.value)
                    except UnresolvedAliasError:
                        usage.problems.append(
                            f"{where}:{item.lineno}: {item.target.id} has an alias the check "
                            "cannot resolve: use a string"
                        )
                        continue
                    name = alias or f"{prefix}{item.target.id.upper()}"
                    usage.settings.add(name)
                    usage.add(name, f"{where}:{item.lineno}")


def scan_compose(path: Path, root: Path, usage: Usage) -> None:
    """Record every `VO_*` or `Settings` name and `${NAME}` interpolation of a compose file."""
    where = path.relative_to(root).as_posix()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        code = YAML_COMMENT.sub("", line)
        interpolated = INTERPOLATION.findall(code)
        usage.interpolated.update(interpolated)
        names = [
            name
            for name in COMPOSE_NAME.findall(code)
            if name.startswith(DEFAULT_PREFIX) or name in usage.settings
        ]
        for name in [*names, *interpolated]:
            usage.composed.add(name)
            usage.add(name, f"{where}:{number}")


def used_variables(root: Path) -> Usage:
    usage = Usage()
    for path in sorted(root.glob("services/*/src/*/settings.py")):
        scan_settings(path, root, usage)
    for path in sorted(root.glob("docker-compose*.yml")):
        scan_compose(path, root, usage)
    return usage


def is_comment_text(line: str) -> bool:
    """A comment line with words in it, not a bare `#` or a `# --- … ---` ruler."""
    text = line.lstrip("#").strip()
    return bool(LETTER.search(text)) and not RULER.match(text)


def check(root: Path) -> list[str]:
    env_example = root / ENV_EXAMPLE
    if not env_example.is_file():
        return [f"{ENV_EXAMPLE}: file not found"]

    usage = used_variables(root)
    problems = list(usage.problems)
    listed: set[str] = set()
    comments: list[str] = []
    for number, line in enumerate(env_example.read_text(encoding="utf-8").splitlines(), start=1):
        entry = ENTRY.match(line)
        name = entry.group("name") if entry else ""
        if not entry or (
            entry.group("commented")
            and not name.startswith(DEFAULT_PREFIX)
            and name not in usage.where
        ):
            comments = [*comments, line] if line.startswith("#") else []
            continue
        where = f"{ENV_EXAMPLE}:{number}: {name}"
        if name in listed:
            problems.append(f"{where} is listed twice")
        listed.add(name)
        if name not in usage.where:
            problems.append(f"{where} is not read by any service or compose file")
        elif name in usage.settings and name not in usage.composed:
            problems.append(f"{where} is read by a service but not passed by compose")
        elif entry.group("commented") and name in usage.interpolated:
            problems.append(f"{where} is interpolated by compose: list it as NAME=value")
        elif not entry.group("commented") and name in usage.composed - usage.interpolated:
            problems.append(f"{where} is fixed by compose: list it as # NAME=value")
        if not any(is_comment_text(comment) for comment in comments):
            problems.append(f"{where} has no comment above it")
        comments = []
    problems.extend(
        f"{where}: {name} missing from {ENV_EXAMPLE}"
        for name, where in sorted(usage.where.items())
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

# ADR-0009: US-01.04: Quality gates as identical tool configuration plus stdlib repository scripts

- Status: Proposed
- Date: 2026-10-16
- Deciders: Project owner
- Related: Constitution §18.2; [BACKEND.md](../BACKEND.md) §1, §2.1, §3, §11;
  [STACK.md](../STACK.md) §1, §5, §10; [ADR-0004](0004-per-service-python-projects.md);
  [ADR-0007](0007-amend-constitution-rename-agents-catalog-to-catalog.md); US-01.04

## Context

US-01.04 configures ruff, mypy, pytest, coverage and import-linter in both services and asks
for three checks the tools do not provide:

1. **Per-layer coverage** (domain 95 %, application 90 %, others 70 %): coverage.py has a
   single `fail_under`.
2. **Configuration drift** between the two `pyproject.toml` files (ADR-0004 forbids a shared
   root manifest, so the configuration is copied).
3. **Pins against STACK.md §5**, including `requires-python` and uv `required-version`.

There is no root Python project (ADR-0004), CI arrives in WP03, and pre-commit in US-01.10.
Each rule also needs a negative fixture that proves it fires, but committed violating files
would break the normal `ruff`/`mypy` runs.

## Decision

We will:

1. Keep every tool section **identical** in both services except package names, and enforce
   it with `scripts/check_service_config_drift.py`. Import-linter contracts and
   `[tool.uv.build-backend] module-name` are exempt: `core` has the three BACKEND.md §2.1
   contracts, `catalog` the "Domain is pure" contract plus a three-layer contract (no
   `agents`, no bounded contexts). `include_external_packages = true` is set for the forbidden
   contract on third-party modules.
2. Write repository checks as **stdlib-only scripts in `scripts/`**, run with `python -I`
   (no dependency, no manifest): `check_coverage.py` (per-layer thresholds on the JSON report,
   exact comparison, fails when no file belongs to the package), `check_service_config_drift.py`,
   `check_python_pins.py`. Each `pyproject.toml` keeps `fail_under = 70` with
   `branch = true` and `source_pkgs` = its package. The scripts are linted with the core rules
   through `scripts/ruff.toml` (`extend`), and their tests run with `pytest scripts/tests` in a
   service toolchain container with the repository mounted.
3. Generate **negative fixtures at test time** in a temporary folder (`tests/tooling/`, marker
   `tooling`, excluded by default) and run the tools via `subprocess`: ruff T201, mypy
   `no-untyped-def`, a pydantic extra keyword that only the plugin rejects, and a copy of
   `src/` with a domain module importing `sqlalchemy`. `tests/tooling/**` also ignores ruff
   `S603` (fixed, trusted tool arguments).
4. Enable the pydantic mypy plugin with `init_forbid_extra = true` and **without**
   `init_typed`, because settings and DTOs are built from strings that pydantic parses (URLs).
5. Pin `anyio==4.15.1` (STACK.md §5) as a direct dev dependency and select the asyncio backend
   with a session `anyio_backend` fixture in each `tests/conftest.py`.

## Alternatives Considered

1. **Per-layer coverage through separate pytest runs** (`--cov=…/domain --cov-fail-under=95`,
   as BACKEND.md §11 first suggested) — no script, but three or more test runs per service and
   thresholds scattered across commands; a single report checked once is faster and keeps
   the numbers in one place.
2. **A shared Python tooling package or a root uv project for the checks** — dependencies
   such as `packaging` or `tomlkit` would be available, but ADR-0004 forbids a root manifest
   and the checks need only `tomllib`, `json`, `re`.
3. **Committed fixture files excluded from ruff/mypy** — visible in the tree, but every
   exclusion is a place where real code could hide, and ruff ignores exclusions for explicit
   paths unless `force-exclude` is on.
4. **Drift check including import-linter contracts** — would force identical layers in both
   services; `catalog` has no `agents` layer, so the contracts must differ.

## Consequences

- Positive: every rule has a test proving it fires; gates fail with file and reason; the
  catalog coverage caveat of ADR-0007 is solved by `source_pkgs`.
- Negative: gate commands are a list to run (BACKEND.md §11.1) until pre-commit (US-01.10)
  and CI (WP03) call them; tooling tests take ~15 s per service; a test-only ruff ignore
  (`S603`) departs from the "S101 only" line of the ROADMAP configuration table.
- Risks and mitigations: STACK.md table format changes could hide a row from the pin parser →
  the repository test `test_the_repository_pins_match_the_stack` and the explicit failure when
  CPython or uv is missing.

## Compliance

- `pytest -m tooling` in each service fails if a rule stops firing.
- `pytest scripts/tests` covers every threshold, drift and pin failure, and checks the real
  repository passes.
- `python -I scripts/check_python_pins.py` and `check_service_config_drift.py` exit 0 on
  `main`; US-01.10 and WP03 must wire them into pre-commit and CI.

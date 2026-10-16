# ADR-0006: US-01.02: Core settings named by env variable, uvicorn app factory, uv_build backend

- Status: Proposed
- Date: 2026-10-16
- Deciders: Project owner
- Related: [BACKEND.md](../BACKEND.md) §1, §2, §4.3; [DOCKER.md](../DOCKER.md) §3, §4.2, §5.2;
  [STACK.md](../STACK.md) §2.3, §5; [ADR-0004](0004-per-service-python-projects.md);
  [ADR-0005](0005-us-01-01-root-compose-and-makefile-first.md); Constitution §15.2

## Context

US-01.02 scaffolds `services/core`. Four points were not settled by the guides:

1. AC3 asks for a validation error that names the missing `VO_*` variables. With
   `env_prefix="VO_"` (BACKEND.md §4.3 sample), pydantic reports the Python field
   (`database_url`), not the variable the operator must set.
2. BACKEND.md says `Settings` is created once and injected, never a global, while DOCKER.md
   §4.2 started uvicorn on `virtual_office.main:app`, i.e. a module-level app that reads the
   environment at import time — importing `main` in a test would require the full environment.
3. A `src/` layout project must be installable (`uv sync` installs the project), so it needs a
   PEP 517 build backend, which STACK.md did not list; the Dockerfile `# syntax=` frontend
   version was also unspecified.
4. DOCKER.md requires `${VO_IMAGE_TAG:?}`, but there is no `.env` yet (US-01.08): a required
   variable would make every `docker compose` call, including `make status|logs|down`, fail on
   a clean clone.

## Decision

We will:

1. Derive each `Settings` field's **validation alias** from its environment name
   (`AliasGenerator(validation_alias=lambda f: f"VO_{f.upper()}")`, `validate_by_name=True`),
   instead of `env_prefix`, so errors name `VO_DATABASE_URL` etc. Settings stay frozen with
   `extra="forbid"`; required now: `VO_DATABASE_URL`, `VO_CATALOG_URL`, `VO_OLLAMA_BASE_URL`;
   optional: `VO_LOG_LEVEL`.
2. Split the factory: `api.app.create_app(settings)` builds the app (lifespan stub, settings on
   `app.state`); `main.create_app(settings=None)` reads `Settings()` when none is given and is
   started by uvicorn with `--factory`. DOCKER.md and BACKEND.md are updated accordingly.
3. Use `uv_build==0.13.1` (same version as uv) as the build backend and
   `docker/dockerfile:1.28.0` (with digest) as the Dockerfile frontend; both are recorded in
   STACK.md.
4. Default the image tag to `${VO_IMAGE_TAG:-dev}` and give `core` fixed, secret-free compose
   addresses until WP02 (hardening) and WP04 (database credentials) make them required.

## Alternatives Considered

1. **`env_prefix` plus a `load_settings()` wrapper that rewrites the error** — keeps the guide
   sample, but `Settings()` itself would still report field names, and every caller must
   remember the wrapper.
2. **Per-field `Field(validation_alias="VO_…")`** — explicit, but repetitive and easy to forget
   on a new field; the alias generator applies the rule to every field.
3. **Module-level `app = create_app()` in `main.py`** (original DOCKER.md) — the usual uvicorn
   form, but reads the environment at import time and makes the module untestable without it.
4. **`[tool.uv] package = false` with `PYTHONPATH=src`** — no build backend, but the runtime
   image would depend on a path hack instead of an installed package.
5. **`${VO_IMAGE_TAG:?}` now** — matches DOCKER.md, but breaks `make status` on a clean clone
   (US-01.01 AC3).

## Consequences

- Positive: misconfiguration errors name the exact variable; no settings are read at import;
  the runtime image only carries the installed virtualenv.
- Negative: the settings snippet in BACKEND.md departs from the plain pydantic-settings
  default; the compose file temporarily departs from DOCKER.md §3 rule 3.
- Risks and mitigations: without the pydantic mypy plugin, `mypy --strict` reports false
  `call-arg` errors on `Settings()` → the plugin is configured in US-01.04. The default image
  tag must not survive WP02 → DOCKER.md §8 review checklist and the compose comment.

## Compliance

- `tests/unit/test_settings.py::test_missing_variables_are_named_in_the_error` fails if an
  error stops naming a `VO_*` variable.
- `tests/unit/test_app_factory.py` covers the factory with injected and environment settings
  and the lifespan.
- `make up` starts `core` through `--factory`; `uv lock --check` and `uv sync --frozen` pass in
  the image.
- WP02 review: `${VO_IMAGE_TAG:?}` and required database credentials replace the defaults.

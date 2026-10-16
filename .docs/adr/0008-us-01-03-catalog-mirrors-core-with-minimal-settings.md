# ADR-0008: US-01.03: Catalog service mirrors core, with database-only settings and a writable uv cache in dev images

- Status: Proposed
- Date: 2026-10-16
- Deciders: Project owner
- Related: [BACKEND.md](../BACKEND.md) §1, §2, §4.3; [DOCKER.md](../DOCKER.md) §4.2;
  [STACK.md](../STACK.md) §5, §5.3; [ADR-0004](0004-per-service-python-projects.md);
  [ADR-0006](0006-us-01-02-core-settings-and-app-factory.md);
  [ADR-0007](0007-amend-constitution-rename-agents-catalog-to-catalog.md); Constitution §15.2

## Context

US-01.03 scaffolds `services/catalog` "with the same conventions as `core`". Three points were
not settled by the guides:

1. Which `VO_*` variables the catalog requires. It owns database `catalog` (POSTGRES.md) and
   calls no other service; `core` needs `VO_CATALOG_URL` and `VO_OLLAMA_BASE_URL`, the catalog
   does not.
2. How much of `core`'s scaffold to copy: settings via alias generator, split factory
   (`api.app.create_app(settings)` + `main.create_app()` for `uvicorn --factory`), Dockerfile,
   `.dockerignore`, tests.
3. The `dev` target runs as UID 10001 without a home directory, so `uv` in the toolchain image
   (`uv lock --check`, `uv sync --frozen`, BACKEND.md §1 rule 5) failed with
   `Failed to initialize cache at /home/app/.cache/uv` in both services (review R1).

## Decision

We will:

1. Give the catalog `Settings` only `VO_DATABASE_URL` (required, `PostgresDsn`) and
   `VO_LOG_LEVEL` (optional, default `INFO`), built exactly like `core` (ADR-0006: validation
   alias = variable name, frozen, `extra="forbid"`). Compose sets
   `VO_DATABASE_URL=postgresql+asyncpg://catalog_app@postgres:5432/catalog` until WP02/WP04 add
   the credentials.
2. Mirror `core` file by file: same `pyproject.toml` (only name, description and
   `module-name` differ), same pins, same Dockerfile (only title, module and port 8001 differ),
   same `.dockerignore`, same factory split and the same test shapes (fixtures
   `no_catalog_environment` / `catalog_environment` / `settings`). The `catalog/` definitions
   folders are tracked with `.gitkeep` and asserted by `test_package_layout.py`.
3. Set `UV_CACHE_DIR=/tmp/uv-cache` in the `dev` stage of **both** Dockerfiles and in the
   DOCKER.md §4.2 sample, so `uv` works as UID 10001 without creating a home directory.

## Alternatives Considered

1. **Share a settings base class or a common library between the services** — less
   duplication, but a shared package breaks the self-contained subprojects of ADR-0004; the
   drift check of US-01.04 keeps the copies aligned instead.
2. **Give the catalog the same three URLs as `core`** — identical settings, but it would
   require variables the service never uses (twelve-factor: config is what the service needs).
3. **Create a home directory for UID 10001** (`useradd --create-home`) — fixes the cache too,
   but adds a writable home to every image, including `runtime`, where it is not needed; or
   **always pass `-e UV_CACHE_DIR`** — easy to forget, breaks BACKEND.md §1 rule 5 by default.

## Consequences

- Positive: both services read the same; a reviewer can diff them file by file; `uv` commands
  work in both dev images.
- Negative: the two scaffolds are duplicated code by design (ADR-0004); the `dev` image keeps
  its uv cache in `/tmp`, lost on container restart (only slower re-syncs).
- Risks and mitigations: drift between the copies → drift check in US-01.04 (AC5). The
  `catalog` import package shares its name with the `catalog/` folder → coverage by path or
  `source_pkgs` (ADR-0007).

## Compliance

- `services/catalog/tests/unit/test_settings.py::test_missing_variables_are_named_in_the_error`
  fails if `VO_DATABASE_URL` stops being named.
- `services/catalog/tests/unit/test_package_layout.py` fails if a layer package or a
  `catalog/{roles,prompts,characters,evals}` folder disappears.
- `docker run … --target dev` image: `uv lock --check && uv sync --frozen` succeed as UID 10001
  for `core` and `catalog`.
- `make up` → `make status` shows `catalog` running next to `core`.

# ADR-0004: US-01.01: Self-contained subprojects; only docker-compose.yml and Makefile at the root

- Status: Proposed
- Date: 2026-10-16
- Deciders: Project owner
- Related: [STACK.md](../STACK.md) §1, §2.2, §5, §10; [BACKEND.md](../BACKEND.md) §1;
  [DOCKER.md](../DOCKER.md) §1, §2, §4, §5, §6, §8; [OLLAMA.md](../OLLAMA.md);
  [ROADMAP.md](../../.project/ROADMAP.md) WP01, WP02, WP03; Constitution §15.2;
  [ADR-0002](0002-technology-stack.md)

## Context

STACK.md §10, BACKEND.md §1, DOCKER.md §4 and the WP01 roadmap planned a single uv workspace
whose `pyproject.toml` and `uv.lock` sit at the repository root, with `services/*` as members,
all Python tool configuration shared from that root file, and the repository root as the
Docker build context of the Python images. Compose files were named `compose*.yaml`, and no
command wrapper was planned.

The project owner rejected that layout: everything is dockerized, every subproject must be
self-contained with its own Dockerfile, and the repository root should show only the
orchestration entry points — `docker-compose.yml` and a `Makefile` (`help` as default goal,
plus `up`, `down`, `logs`, `status`).

A root workspace has concrete costs in a fully dockerized setup:

- the build context of every Python image becomes the whole repository, so an image depends on
  files outside its folder and every build sends the frontend, docs and assets to the daemon;
- the root lockfile couples the services: a dependency bump for `agents-catalog` changes the
  lock used to build `core`;
- the root mixes ecosystems, while the frontend already keeps its manifest inside `frontend/`.

## Decision

We will lay out the repository as self-contained subprojects orchestrated from the root:

1. **No ecosystem manifest at the root.** `services/core/`, `services/agents-catalog/` and
   `frontend/` each own their manifest, committed lockfile (`uv.lock` / `pnpm-lock.yaml`),
   `Dockerfile` and `.dockerignore`, and each folder is its image's **build context**.
2. **Python services are independent uv projects.** Each `pyproject.toml` declares
   `requires-python` pinned to the STACK.md minor, `[tool.uv] required-version` equal to the
   STACK.md uv version, `==`-pinned runtime dependencies, a `[dependency-groups] dev` group
   with the shared dev tools pinned `==`, and the full tool configuration (`ruff`, `mypy`,
   `pytest`, `coverage`, `importlinter`). The tool configuration is identical in both services
   except for package names and paths.
3. **Root entry points.** The root holds `docker-compose.yml` (plus the overlays
   `docker-compose.dev.yml`, `docker-compose.gpu.yml`, `docker-compose.ci.yml`) and a
   `Makefile`. The Makefile is a thin wrapper over `docker compose` with no logic of its own:
   `make` prints the help; `up`, `down`, `logs`, `status` run the commands of DOCKER.md §6.
   It is created with the base compose file in WP02 (US-02.04).
4. **Constitution §15.2 layout** is amended (PATCH, clarification of the layout sketch) once
   this ADR is accepted:
   - old: `├── compose*.yaml, .env.example`
   - new: `├── docker-compose*.yml, Makefile, .env.example   # orchestration only; each subproject owns its manifest, lock and Dockerfile`
5. US-01.01 is re-scoped from "Create the uv workspace root" to recording this decision and
   aligning the docs; US-01.02 and US-01.03 create the service manifests and locks.

## Alternatives Considered

1. **Root uv workspace (original plan)** — one lockfile and one tool config, identical versions
   across services guaranteed. Rejected by the project owner: Python files at the root,
   whole-repository build context, coupled locks.
2. **Workspace root inside `services/`** (`services/pyproject.toml` + `services/uv.lock`) —
   keeps one lock and one config and a clean root. Still couples the services' locks and makes
   `services/` the build context of both images, so a service is not self-contained.
3. **Self-contained subprojects (chosen)** — each subproject builds, locks and tests in
   isolation with a minimal build context. Costs: two Python lockfiles and duplicated tool
   configuration, mitigated by the checks below.
4. **No Makefile, raw `docker compose` only** — one less file, but the owner wants short,
   discoverable commands; the Makefile adds no logic, so every target still works without
   `make`.

## Consequences

- Positive: each image is built from its own folder only; dependency updates are scoped to one
  subproject; the root shows only how to run the system; `make` gives a discoverable command
  list.
- Negative: tool configuration is duplicated in two Python services; the services may resolve
  different transitive versions; Renovate opens one update per lock; `make` becomes an
  optional host tool next to Docker (DOCKER.md §1).
- Risks and mitigations:
  - *Config drift between services* → a tooling check compares the tool sections of the two
    `pyproject.toml` files (US-01.04 AC5).
  - *Direct pins drifting from STACK.md* → a stdlib script under `scripts/`, run with
    `python -I` in the pinned Python image, compares each service's direct pins,
    `requires-python` and `required-version` with STACK.md §5 (US-01.04 AC6; pre-commit in
    US-01.10, CI in WP03).
  - *"Installs no package not listed in STACK.md"* is read as "no **direct** dependency outside
    STACK.md"; transitive packages are governed by the committed locks.
  - *Makefile growing logic* → DOCKER.md §8 review item: targets only wrap `docker compose`.

## Compliance

- Review item (DOCKER.md §8): build context is the subproject folder; no Python or Node
  manifest at the repository root; Makefile targets only wrap `docker compose`.
- `uv lock --check` and `uv sync --frozen` succeed per service in the service container
  (US-01.02 AC5, US-01.03 AC4).
- Tooling checks of US-01.04 (pin consistency with STACK.md, config parity between services)
  fail on negative fixtures and pass on the skeleton.
- WP02 US-02.04 AC6/AC7: `make` prints the help; compose uses
  `build.context: frontend | services/core | services/agents-catalog`.

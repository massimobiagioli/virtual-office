# WP01 — Repository & Toolchain

| Field        | Value |
| ------------ | ----- |
| Milestone    | M0 — Boot Disk |
| Status       | PROCESSING |
| Depends on   | — |
| Enables      | WP02, WP07 |
| Constitution | Article XV (§15.2, §15.3), Article XVIII, Article XIX |
| Guides       | [STACK.md](../../.docs/STACK.md) §1, §3, §5 · [BACKEND.md](../../.docs/BACKEND.md) §1–3 · [FRONTEND.md](../../.docs/FRONTEND.md) §1–2, §11 · [PRINCIPLES.md](../../.docs/PRINCIPLES.md) |
| Skills       | `delivering-features`, `writing-adrs` |
| Estimate     | 26 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [x] US-01.01 — Root `docker-compose.yml` and `Makefile` (2 pts) · ADR: ADR-0005
- [ ] US-01.02 — Scaffold the `core` service package (3 pts)
- [ ] US-01.03 — Scaffold the `agents-catalog` service package (2 pts)
- [ ] US-01.04 — Configure quality tools and architecture contracts (3 pts)
- [ ] US-01.05 — Scaffold the Vue + Vite application (3 pts)
- [ ] US-01.06 — Strict TypeScript and lint configuration (3 pts)
- [ ] US-01.07 — Vitest setup with coverage (2 pts)
- [ ] US-01.08 — Editor, ignore and environment files (2 pts)
- [ ] US-01.09 — `no-latest` check (3 pts)
- [ ] US-01.10 — Pre-commit hooks and Renovate (3 pts)

## 1. Objective

Create the code skeleton of the repository so that every later story starts from a uniform,
strictly-checked base: the two Python services as independent uv projects, the Vue frontend, and the
repository hygiene that keeps versions pinned and code consistent. No business logic is written
in this WP.

## 2. Scope

**In:** per-service uv projects, service packages with empty layered layout, frontend skeleton, linters,
type checkers, test runners, architecture boundary rules, pre-commit, `no-latest` check,
Renovate configuration, `.env.example`, `.gitignore`, `.editorconfig`.

**Out:** compose hardening, Postgres, Ollama, overlays (WP02), CI workflows (WP03), any domain code (WP05+).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D01.1 | Python services | `services/core` and `services/agents-catalog` as independent uv projects (own `pyproject.toml` + `uv.lock`) in `src/` layout; ruff, mypy strict, pytest, import-linter configured identically per service and passing | `uv sync --frozen`, `ruff check`, `ruff format --check`, `mypy`, `pytest`, `lint-imports` exit 0 inside each service container | US-01.01 – US-01.04 |
| D01.2 | Frontend skeleton | Vue + Vite + TS app with the folder layout of FRONTEND.md §1, strict tsconfig, ESLint flat config incl. boundaries, Prettier, Vitest | `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build` exit 0; boundaries rule violation demo test fails as expected | US-01.05 – US-01.07 |
| D01.3 | Repository hygiene | Editor/ignore files, pre-commit hooks, `no-latest` check, Renovate, `.env.example` | Pre-commit runs all hooks; `no-latest` script fails on a fixture containing `:latest`; Renovate config validates | US-01.08 – US-01.10 |

## 4. User stories

### D01.1 — Python services

#### US-01.01 — Root `docker-compose.yml` and `Makefile`

- [x] **US-01.01 completed** · **Points:** 2 · **Priority:** Must · **ADR:** ADR-0005
- **Story:** As a contributor, I want `docker-compose.yml` and a `Makefile` at the repository
  root from day one, so that the whole system is driven by `make` and every subproject plugs
  into compose with its own Dockerfile as soon as it exists (ADR-0004).
- **Acceptance criteria:**
  - [x] AC1 — Given `docker-compose.yml` at the root, when `docker compose config` runs, then it is
    valid, declares `name: virtual-office`, has no `version:` key and no services yet.
  - [x] AC2 — Given the `Makefile`, when `make` runs with no target, then it prints the help
    listing `help`, `up`, `down`, `logs`, `status` with a one-line description each.
  - [x] AC3 — Given the `Makefile`, when inspected, then `up` runs `docker compose up --build -d`,
    `down` runs `docker compose down`, `logs` runs `docker compose logs -f` (optional
    `s=<service>`), `status` runs `docker compose ps`; `make status`, `make logs`, `make down`
    exit 0 on the empty stack.
  - [x] AC4 — Given the repository root, when listed, then it contains no Python or Node
    manifest.
- **Tasks:**
  - [x] Write `docker-compose.yml` (Compose Specification, no services yet).
  - [x] Write the `Makefile` (`.DEFAULT_GOAL := help`, self-documenting targets, `.PHONY`).
- **Tests:** `docker compose config`; `make`, `make status`, `make logs`, `make down` exit codes
  and help output. `make up` is verified from US-01.02, when `core` is the first service.
- **Done when:** both files merged and the checks pass.

#### US-01.02 — Scaffold the `core` service package

- [ ] **US-01.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a backend developer, I want the `core` package with the exact layered layout of
  BACKEND.md §2, so that every future module has an obvious home.
- **Acceptance criteria:**
  - [x] AC1 — Given `services/core/src/virtual_office/`, when listed, then it contains `domain/{shared,
    kanban,staff,intake,decisions}`, `application/`, `agents/`, `infrastructure/`, `api/`,
    `settings.py`, `main.py`, each with an `__init__.py`.
  - [x] AC2 — Given `main.py`, when imported, then `create_app()` returns a FastAPI app with no routes
    except health placeholders (added in WP02).
  - [x] AC3 — Given `settings.py`, when instantiated without required env vars, then it fails with a
    clear validation error naming the missing `VO_*` variables.
  - [x] AC4 — Given `services/core/tests/`, when `pytest` runs, then one smoke test (`test_app_factory`)
    passes.
  - [x] AC5 — Given `services/core/pyproject.toml`, when inspected, then `requires-python` is pinned
    to the STACK.md minor, `[tool.uv] required-version` equals the STACK.md uv version, and every
    direct dependency (runtime and `dev` group) is pinned `==` to STACK.md; `uv lock --check` and
    `uv sync --frozen` succeed from the service folder in the container (ADR-0004).
  - [x] AC6 — Given `services/core/Dockerfile` (multi-stage, base images pinned by tag and digest,
    non-root UID 10001, `.dockerignore`) and the `core` service in `docker-compose.yml`
    (`build.context: services/core`, required `VO_*` variables), when `make up` runs, then the
    image builds and `make status` shows `core` running.
- **Tasks:**
  - [x] Create package tree, `pyproject.toml` (`name = "virtual-office-core"`, `dev` group with
    ruff, mypy, import-linter, pytest, pytest-cov, hypothesis) and commit `uv.lock`.
  - [x] Implement `Settings` (pydantic-settings, `VO_` prefix, frozen, `extra="forbid"`).
  - [x] Implement `create_app()` with lifespan stub.
  - [x] Add `tests/unit/test_app_factory.py`.
- **Tests:** unit smoke test; settings validation test.
- **Done when:** `pytest` green for `core`.

#### US-01.03 — Scaffold the `agents-catalog` service package

- [ ] **US-01.03 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a backend developer, I want the `agents-catalog` package with the same
  conventions as `core`, so that both services look identical.
- **Acceptance criteria:**
  - [ ] AC1 — Given `services/agents-catalog/src/agents_catalog/`, when listed, then it contains
    `domain/`, `application/`, `infrastructure/`, `api/`, `settings.py`, `main.py`.
  - [ ] AC2 — Given `services/agents-catalog/catalog/`, when listed, then it contains `roles/`,
    `prompts/`, `characters/`, `evals/` (each with a `.gitkeep`).
  - [ ] AC3 — Given the package, when `pytest` runs, then the app-factory smoke test passes.
  - [ ] AC4 — Given `services/agents-catalog/pyproject.toml` and its `uv.lock`, when inspected, then
    the pinning rules of US-01.02 AC5 hold and `uv sync --frozen` succeeds in the container.
  - [ ] AC5 — Given `services/agents-catalog/Dockerfile` and the `agents-catalog` service in
    `docker-compose.yml` (`build.context: services/agents-catalog`), when `make up` runs, then
    `make status` shows it running next to `core`.
- **Tasks:** mirror US-01.02 for the catalog service (own `pyproject.toml` + `uv.lock`).
- **Tests:** unit smoke test.
- **Done when:** `pytest` green for `agents-catalog`.

#### US-01.04 — Configure quality tools and architecture contracts

- [ ] **US-01.04 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a tech lead, I want ruff, mypy strict and import-linter configured identically
  in both services, so that the hexagonal rules are enforced from the first line of code.
- **Acceptance criteria:**
  - [ ] AC1 — Given a service config, when `ruff check` runs, then the rule sets of BACKEND.md §3 are
    active (verified by a fixture file with a `print` call failing T20).
  - [ ] AC2 — Given a service config, when `mypy` runs, then `strict = true` and the pydantic plugin are
    active for both services.
  - [ ] AC3 — Given the import-linter contracts of BACKEND.md §2.1, when a test fixture module in
    `domain` imports `sqlalchemy`, then `lint-imports` fails; when removed, it passes.
  - [ ] AC4 — Given the coverage config, when `pytest --cov` runs, then per-package thresholds of
    Constitution §18.2 are configured (domain 95, application 90, others 70).
  - [ ] AC5 — Given the two service `pyproject.toml` files, when their tool sections differ beyond
    package names and paths, then the drift check fails (ADR-0004).
  - [ ] AC6 — Given a direct pin, `requires-python` or `required-version` that differs from
    STACK.md §5, when the pin check (`scripts/`, stdlib, `python -I`) runs, then it fails with
    file and requirement; on the skeleton it passes.
- **Tasks:**
  - [ ] `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.format]` sections.
  - [ ] `[tool.mypy]` strict + plugins.
  - [ ] `[tool.importlinter]` contracts for both services.
  - [ ] `[tool.pytest.ini_options]` (markers `integration`, `eval`; anyio) and `[tool.coverage]`.
- **Tests:** negative fixtures executed in a dedicated test that runs the tools via subprocess
  (marked `tooling`).
- **Done when:** all tools pass on the skeleton and fail on the negative fixtures.

### D01.2 — Frontend skeleton

#### US-01.05 — Scaffold the Vue + Vite application

- [ ] **US-01.05 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a frontend developer, I want a Vue + Vite + TS app with the layout of
  FRONTEND.md §1, so that UI work can start without setup decisions.
- **Acceptance criteria:**
  - [ ] AC1 — Given `frontend/`, when listed, then `src/` contains `api/`, `stores/`, `composables/`,
    `ui-amiga/`, `windows/`, `office-engine/`, `office-renderer/`, `assets/`, `shared/`.
  - [ ] AC2 — Given `package.json`, when inspected, then every dependency uses an exact version from
    STACK.md, `packageManager` pins pnpm, and `.npmrc` has `save-exact=true` and
    `engine-strict=true`.
  - [ ] AC3 — Given `pnpm build`, when run in the build container, then a `dist/` with hashed assets is
    produced and `App.vue` renders a placeholder "My Workbench" title.
  - [ ] AC4 — Given `frontend/Dockerfile` (build stage pnpm, runtime nginx, both pinned by tag and
    digest) and the `frontend` service in `docker-compose.yml` (`build.context: frontend`,
    published only on `127.0.0.1:8080`), when `make up` runs, then `http://127.0.0.1:8080/`
    serves the "My Workbench" placeholder.
- **Tasks:** create project files, `main.ts`, `App.vue`, Pinia and router registration.
- **Tests:** `App.spec.ts` renders the title.
- **Done when:** build and test pass.

#### US-01.06 — Strict TypeScript and lint configuration

- [ ] **US-01.06 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a tech lead, I want strict TS and ESLint rules from FRONTEND.md §2 and §11, so
  that style debates never happen in review.
- **Acceptance criteria:**
  - [ ] AC1 — Given `tsconfig.app.json`, when inspected, then all compiler options listed in
    FRONTEND.md §2 are set.
  - [ ] AC2 — Given `eslint.config.ts`, when a fixture SFC uses the Options API, then lint fails with
    `vue/component-api-style`.
  - [ ] AC3 — Given the boundaries config, when a fixture file in `office-engine/` imports `vue` or
    `pixi.js`, then lint fails.
  - [ ] AC4 — Given Prettier config, when `pnpm format:check` runs on the skeleton, then it passes.
- **Tasks:** write configs; add negative fixtures under `frontend/tooling-fixtures/`
  (excluded from build) and a script asserting they fail.
- **Tests:** tooling script in CI.
- **Done when:** positive passes, negatives fail.

#### US-01.07 — Vitest setup with coverage

- [ ] **US-01.07 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a frontend developer, I want Vitest with jsdom, @vue/test-utils and coverage
  thresholds, so that TDD works out of the box.
- **Acceptance criteria:**
  - [ ] AC1 — Given `vitest.config.ts`, when `pnpm test` runs, then tests in `src/**/*.spec.ts` run
    with jsdom and coverage v8.
  - [ ] AC2 — Given coverage thresholds, when below 70 % globally (higher for `office-engine` later),
    then the run fails.
  - [ ] AC3 — Given fast-check, when a sample property test runs, then it passes (proves wiring).
- **Tasks:** config, sample tests, scripts `test`, `test:watch`, `coverage`.
- **Tests:** sample spec files.
- **Done when:** `pnpm test` green with coverage report.

### D01.3 — Repository hygiene

#### US-01.08 — Editor, ignore and environment files

- [ ] **US-01.08 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a contributor, I want shared editor settings, ignore rules and a documented
  `.env.example`, so that every machine behaves the same and secrets never get committed.
- **Acceptance criteria:**
  - [ ] AC1 — `.editorconfig` sets UTF-8, LF, final newline, 2 spaces for TS/Vue/YAML/JSON, 4 for Python.
  - [ ] AC2 — `.gitignore` ignores `.env`, build outputs, caches, `node_modules`, `.venv`.
  - [ ] AC3 — `.env.example` lists every `VO_*` variable known so far, each with a comment, no real
    secrets, and passes the `no-latest` check.
- **Tasks:** write the three files.
- **Tests:** `no-latest` check (US-01.09) covers `.env.example`.
- **Done when:** files merged.

#### US-01.09 — `no-latest` check

- [ ] **US-01.09 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want an automated check that rejects `latest` and floating
  version tags, so that the version policy of STACK.md §1 cannot be broken by accident.
- **Acceptance criteria:**
  - [ ] AC1 — Given a file containing `image: postgres:latest`, `FROM node:24`, `ollama/ollama:latest`,
    `"vue": "latest"`, `uses: actions/checkout@v4` or `qwen3.6` without tag, when the check
    runs, then it fails and prints file:line for each hit.
  - [ ] AC2 — Given files containing exact tags (`postgres:18.6-trixie@sha256:…`, `"vue": "3.5.44"`,
    `uses: actions/checkout@<40-hex-sha> # v…`), when the check runs, then it passes.
  - [ ] AC3 — Given Markdown files in `.docs/` and `.project/`, when the check runs, then they are
    excluded.
- **Tasks:** implement `scripts/check_no_latest.py` (stdlib only, run with `python -I`);
  fixtures in `scripts/fixtures/no_latest/{good,bad}`; test file.
- **Tests:** pytest over the fixtures.
- **Done when:** script and tests merged; hooked in pre-commit (US-01.10) and CI (WP03).

#### US-01.10 — Pre-commit hooks and Renovate

- [ ] **US-01.10 completed** · **Points:** 3 · **Priority:** Should · **ADR:** —
- **Story:** As a contributor, I want pre-commit hooks and automated dependency updates, so that
  problems are caught before CI and versions stay current.
- **Acceptance criteria:**
  - [ ] AC1 — Given `.pre-commit-config.yaml` with hooks pinned by exact rev, when `pre-commit run
    --all-files` runs in the dev container, then ruff, ruff-format, mypy, eslint, prettier,
    vue-tsc and `no-latest` run.
  - [ ] AC2 — Given `renovate.json`, when validated with the Renovate config validator, then it is
    valid; it groups updates per ecosystem, pins Docker digests, schedules weekly, and
    never uses `latest`.
  - [ ] AC3 — Given a Renovate PR, when it changes a version, then the PR template reminds to update
    STACK.md.
- **Tasks:** write configs; add `.github/pull_request_template.md` with the review checklist
  from PRINCIPLES.md §7.
- **Tests:** config validation in CI (WP03).
- **Done when:** hooks run locally in container; Renovate config valid.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WPNN closing: …`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; D01.1–D01.3 acceptance evidence attached to the PRs.
- [ ] No file contains a floating version or `latest` (check green).
- [ ] STACK.md unchanged or updated in the same PR if any version moved.
- [ ] Constitution §15.2 layout matches the repository.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| A pinned tool version is incompatible with Python 3.15 or TS 6 | Record a version hold in STACK.md §9 instead of downgrading silently |
| Tool configuration drifts between services | Identical per-service config enforced by the drift check of US-01.04 (ADR-0004) |

## 7. Blockers

None.

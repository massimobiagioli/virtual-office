# Review — WP01 Repository & Toolchain

## US-01.01 — Create the uv workspace root

### Round 1 · 2026-10-16 · branch `feat/us-01-01-uv-workspace-root` · head `2cd4dd8`

**Verdict:** APPROVED

**Quality gate**

Run in a throwaway container built from the pinned images `python:3.15.0-slim-trixie` +
`ghcr.io/astral-sh/uv:0.13.1` (the project dev container arrives in WP02).

| Gate | Result |
| ---- | ------ |
| `uv lock --check` | pass |
| `uv sync --frozen --no-cache` (cold cache, lock only) | pass |
| pytest (`tests/repository`, 5 tests) | pass |
| Negative check: `ruff>=0.17` instead of `==` | fails as expected (`is not an exact '==' pin`) |
| ruff check (default rules; root config arrives in US-01.04) | pass |
| ruff format --check (line length 100) | pass |
| mypy --strict (`tests/`) | pass |
| lint-imports | not available (contracts arrive in US-01.04) |
| pytest coverage thresholds | not available (US-01.04) |
| frontend gates (eslint, prettier, vue-tsc, vitest) | not available (US-01.05–07) |
| `docker compose up --build`, Playwright | not available (WP02, WP14+) |
| `no-latest` check | not available (US-01.09); manual grep for `latest`: 0 hits |

**Acceptance**

- AC1 — `uv sync --frozen` succeeds from `uv.lock` alone with an empty cache; every direct
  dependency is in STACK.md §5 (enforced by
  `tests/repository/test_uv_workspace.py:96`).
- AC2 — `members = ["services/*"]` (`pyproject.toml:27`) and
  `requires-python = ">=3.15,<3.16"` (`pyproject.toml:8`), both checked against STACK.md by
  `test_workspace_members_are_the_services` and `test_requires_python_is_pinned_to_the_stack_minor`.
- AC3 — all six dev tools are pinned `==` to STACK.md §5; the test also covers
  `services/*/pyproject.toml` so US-01.02/03 inherit the check.

**Findings**

- [ ] **R1 · Minor** — `tests/repository/test_uv_workspace.py:1` — new top-level `tests/`
  directory for repository-level tests is not in the documented layout (BACKEND.md §1,
  Constitution §15.2, STACK.md §10). A reader would not know where repository tooling tests
  live. Suggested fix: add `tests/repository/` to the BACKEND.md §1 layout with one line saying
  what belongs there.
- [ ] **R2 · Nit** — AC1 says "installs no package not listed in STACK.md"; `uv sync` also
  installs 17 transitive packages (e.g. `rich`, `librt`, `grimp`) that STACK.md does not list
  and cannot reasonably list. The implementation reads AC1 as "no *direct* dependency outside
  STACK.md". Suggested fix: record this interpretation in the story ADR.

**Notes**

- Nice touch: `[tool.uv] required-version = "==0.13.1"` keeps contributors on the STACK uv.
- The repository test is not collected by a bare `pytest` yet (no `testpaths`); US-01.04 should
  include `tests/` in `[tool.pytest.ini_options]`, and WP03 should run it in CI.
- `.project/execution/` is in `.gitignore`, so this review file and the WP checkboxes stay
  local and cannot be committed as the command asks.

### Round 2 · 2026-10-16 · branch `docs/us-01-01-per-service-python-projects` · head `960a492`

Round 1 reviewed `feat/us-01-01-uv-workspace-root`, which the project owner rejected (no Python
files at the repository root). That branch was discarded unmerged; R1 and R2 of Round 1 are
obsolete. The story is re-scoped as a docs story under ADR-0004.

**Verdict:** APPROVED

**Quality gate**

| Gate | Result |
| ---- | ------ |
| Root contains no `pyproject.toml`, `uv.lock`, `package.json` | pass (`ls`) |
| No `compose*.yaml` name left outside the Constitution (pending amendment) and ADR-0004 | pass (`grep`) |
| ADR-0004 links from STACK, BACKEND, DOCKER, ROADMAP resolve | pass |
| Conventional Commits, subject ≤ 72 chars | pass (57, 62, 70) |
| `latest` added | only the rule name `no-latest` in ROADMAP.md (Markdown, excluded by policy) |
| ruff, mypy, pytest, lint-imports, frontend gates, compose, Playwright | not available — docs-only story, no code exists yet |
| `no-latest` script | not available (US-01.09) |

**Acceptance**

- AC1 — `.docs/adr/0004-per-service-python-projects.md`: 4 alternatives, `Proposed`; registered
  in `.docs/adr/index.md:16` and `AGENTS.md:89`.
- AC2 — STACK.md §5/§10, BACKEND.md §1, DOCKER.md §2/§4, ROADMAP WP01 describe per-service
  projects; grep finds no root workspace wording.
- AC3 — DOCKER.md §6 Makefile table; DOCKER.md §1 adds GNU Make; ROADMAP WP02 D02.2 and
  US-02.04 AC6/AC7.
- AC4 — root listing shows no manifest.

**Findings**

- [x] **R1 · Minor** — `.docs/CONSTITUTION.md:1245` still lists `compose*.yaml`. Correct by
  process: the amendment text is in ADR-0004 §Decision 4 and is applied only when the owner
  accepts ADR-0004 (skill `writing-adrs`). Follow-up, not fixable in this story without
  acceptance. → Resolved in fa1c87b: owner accepted ADR-0004; §15.2 amended, Constitution v3.1.1.

**Notes**

- Host Docker on this machine is 24.0.7, below the DOCKER.md §1 minimum (Engine 29.9.1); it
  will matter in WP02 (`develop.watch`, Compose v5 features).
- DOCKER.md §2 `.dockerignore` list still names `.docs` and `.agents`; harmless now that
  contexts are subfolders.

**Rework:** 2026-10-16 · head fa1c87b · gates: docs checks re-run (root listing, grep, links) pass; code gates not available

---

> **WP01 restarted from scratch (2026-10-16).** The project owner asked for the root
> `docker-compose.yml` and `Makefile` to exist from the first story. WP01 tracking was reset to
> `READY`; US-01.01 was redefined as "Root `docker-compose.yml` and `Makefile`". Rounds 1–2
> above belong to the previous scope and are kept for history.

### Round 3 · 2026-10-16 · branch `feat/us-01-01-root-compose-and-makefile` · head `c080f12`

**Verdict:** APPROVED

**Quality gate**

| Gate | Result |
| ---- | ------ |
| `docker compose config` | pass (`name: virtual-office`, `services: {}`, no `version:`) |
| `make` (no target) prints help with help/up/down/logs/status | pass |
| `make status`, `make logs`, `make down` on the empty stack | pass (exit 0) |
| `make -n up / logs s=core / down / status` map to DOCKER.md §6 commands | pass |
| `make up` | not applicable yet: Compose refuses `up` with no services ("no service selected"); verified from US-01.02 (AC6) |
| Root has no Python/Node manifest | pass |
| Conventional Commits ≤ 72 chars | pass (47, 65) |
| `latest` in diff | 0 hits |
| ruff, mypy, pytest, frontend gates, Playwright | not available (no code yet) |
| `no-latest` script | not available (US-01.09) |

**Acceptance**

- AC1 — `docker-compose.yml:4-6`.
- AC2/AC3 — `Makefile:6-24`; `.DEFAULT_GOAL := help`, `.PHONY`, recipes are single
  `docker compose` calls (DOCKER.md §8: no logic).
- AC4 — root listing: `AGENTS.md`, `CLAUDE.md`, `Makefile`, `docker-compose.yml`.

**Findings**

- [x] **R1 · Minor** — `.project/ROADMAP.md:274` links
  `.docs/adr/0005-us-01-01-root-compose-and-makefile-first.md`, which does not exist yet; and
  accepted ADR-0004 §Decision 3 still says the Makefile is created in WP02. Fix: write the story
  ADR-0005 at close (it amends the timing of ADR-0004 §3 without rewriting ADR-0004). → Resolved in b53cc0c: ADR-0005 written and registered; link resolves.

**Rework:** 2026-10-16 · head b53cc0c · gates: compose config, make help/status/logs/down re-run pass; ADR-0005 link resolves

**Notes**

- Your Docker Compose is v2.23.3 (DOCKER.md §1 asks for v5.6.0); fine for these checks, will
  matter for `develop.watch` in WP02.

## US-01.02 — Scaffold the `core` service package

### Round 1 · 2026-10-16 · branch `feat/us-01-02-core-service-package` · head `2651ca4`

**Verdict:** APPROVED

**Quality gate**

Run in the `dev` target of `services/core/Dockerfile` (pinned `python:3.15.0-slim-trixie` +
`uv 0.13.1`). Host: Docker Engine 24.0.7 / Compose v2.23.3, below the DOCKER.md §1 minimum;
every command below still succeeded.

| Gate | Result |
| ---- | ------ |
| `uv lock --check` | pass |
| `uv sync --frozen` (image build, `--no-dev` and dev) | pass |
| ruff check (default rules; BACKEND.md §3 rule sets arrive in US-01.04) | pass |
| ruff format --check (line length 100) | pass |
| mypy --strict with the pydantic plugin (ad-hoc config) | pass |
| mypy --strict without the plugin | fail — 16 `call-arg`/`arg-type` false positives on `Settings`; the plugin is configured in US-01.04 |
| pytest (17 tests) | pass |
| coverage | 96 % total, `api/app.py` 91 % (thresholds configured in US-01.04) |
| lint-imports | not available (contracts arrive in US-01.04) |
| `docker compose config`, `make up`, `make status` (`core` Up, UID 10001), `make down` | pass |
| healthcheck, Playwright | not available (WP02, WP14+) |
| `no-latest` script | not available (US-01.09); manual grep in `services/`, compose, Makefile: 0 hits |
| frontend gates | not available (US-01.05–07) |

**Acceptance**

- AC1 — package tree with `__init__.py` everywhere; `tests/unit/test_package_layout.py`.
- AC2 — `main.create_app()` returns a FastAPI app without `APIRoute`s
  (`tests/unit/test_app_factory.py:15`).
- AC3 — `Settings()` without env fails naming `VO_DATABASE_URL`, `VO_CATALOG_URL`,
  `VO_OLLAMA_BASE_URL` (`services/core/src/virtual_office/settings.py:20`, alias generator;
  `tests/unit/test_settings.py:15`).
- AC4 — `test_app_factory` smoke tests pass.
- AC5 — `requires-python = ">=3.15,<3.16"`, `required-version = "==0.13.1"`, all direct deps
  `==` STACK.md §5; lock check and frozen sync pass.
- AC6 — multi-stage Dockerfile, tag + digest pins, UID 10001, `.dockerignore`; `make up` →
  `make status` shows `core` running.

**Findings**

- [x] **R1 · Minor** — `docker-compose.yml:9` — `${VO_IMAGE_TAG:-dev}` deviates from DOCKER.md §3
  rule 3 / §5.2 rule 6 (`${VAR:?}`). The default is needed so `make status|logs|down` keep
  working on a clean clone before `.env.example` (US-01.08), but the reason is not written
  down. Suggested fix: explain it in a compose comment and in the story ADR.
  → Resolved in 549f118: compose comment explains the default; the ADR records it.
- [x] **R2 · Minor** — `services/core/src/virtual_office/api/app.py:12` — the lifespan stub is
  never entered by a test. Suggested fix: a test that enters `app.router.lifespan_context`.
  → Resolved in 9c1bf5f: `test_app_lifespan_starts_and_stops`; coverage now 100 %.
- [x] **R3 · Minor** — `services/core/tests/unit/test_app_factory.py:26` and
  `tests/unit/test_settings.py:36` — env-reading tests do not clear `VO_LOG_LEVEL` (factory
  test) and build values indirectly (frozen test: three URLs, then an override), so an ambient
  variable could change the outcome. Suggested fix: a shared fixture that sets the three
  required variables and deletes `VO_LOG_LEVEL`.
  → Resolved in 9c1bf5f: `core_environment` / `no_core_environment` / `settings` fixtures in
  `tests/conftest.py`; added a test for `VO_LOG_LEVEL`.

**Rework:** 2026-10-16 · head 549f118 · gates: ruff, ruff format, mypy strict + pydantic plugin,
pytest 19 passed (coverage 100 %), `docker compose config` — all pass.

**Notes**

- Good call starting uvicorn through `--factory`: settings are never read at import time;
  DOCKER.md and BACKEND.md were updated in the same branch.
- New pins recorded in STACK.md: `uv_build 0.13.1`, `docker/dockerfile 1.28.0`.
- Compose security defaults, healthcheck and network are deliberately left to WP02 (ADR-0005).

## US-01.03 — Scaffold the `catalog` service package

### Round 1 · 2026-10-16 · branch `feat/us-01-03-catalog-service-package` · head `1832ef3`

**Verdict:** APPROVED

**Quality gate**

Run in a throwaway container from the pinned `python:3.15.0-slim-trixie` + `uv 0.13.1` images
and in the `dev` target of `services/catalog/Dockerfile`. Host: Docker Engine 24.0.7 /
Compose v2.23.3 (below DOCKER.md §1 minimum; all commands still succeeded).

| Gate | Result |
| ---- | ------ |
| `uv lock --check` | pass (tool container and `dev` image) |
| `uv sync --frozen` (image build `--no-dev`, dev group) | pass |
| ruff check (default rules; BACKEND.md §3 rule sets arrive in US-01.04) | pass |
| ruff format --check (line length 100) | pass |
| mypy --strict with the pydantic plugin (ad-hoc config, as in US-01.02) | pass (12 files) |
| pytest (19 tests) | pass |
| coverage | 100 % (thresholds configured in US-01.04) |
| lint-imports | not available (contracts arrive in US-01.04) |
| pin check / drift check | not available (US-01.04 AC5–AC6); manual diff of the two `pyproject.toml`: only name, description, `module-name` differ |
| `docker compose config`, `make up`, `make status` (`catalog` Up next to `core`, UID 10001, uvicorn on 8001), `make down` | pass |
| healthcheck, Playwright | not available (WP02, WP14+) |
| `no-latest` script | not available (US-01.09); manual grep on the changed code files: 0 hits |
| frontend gates | not available (US-01.05–07) |

**Acceptance**

- AC1 — `domain/`, `application/`, `infrastructure/`, `api/` packages, `settings.py`, `main.py`;
  `tests/unit/test_package_layout.py` (`test_layered_package_exists`, `test_entry_module_exists`).
- AC2 — `catalog/{roles,prompts,characters,evals}/.gitkeep`;
  `test_catalog_source_folder_is_tracked`.
- AC3 — `tests/unit/test_app_factory.py` (factory, injected/env settings, lifespan).
- AC4 — `requires-python = ">=3.15,<3.16"`, `required-version = "==0.13.1"`, every direct dep
  `==` STACK.md §5 (same pins as `core`); lock check and frozen sync pass.
- AC5 — `services/catalog/Dockerfile` mirrors `core` (tag + digest pins, UID 10001,
  `--factory`); `docker-compose.yml` `catalog` with `build.context: services/catalog`.

**Findings**

- [x] **R1 · Minor** — `services/catalog/Dockerfile:41` (and `services/core/Dockerfile:41`)
  — the `dev` target runs as UID 10001 with no home directory, so any `uv` command in the
  toolchain image (`uv lock --check`, `uv sync --frozen`, BACKEND.md §1 rule 5) fails with
  `Failed to initialize cache at /home/app/.cache/uv: Permission denied` unless
  `UV_CACHE_DIR` is overridden. Suggested fix: set `UV_CACHE_DIR=/tmp/uv-cache` in the `dev`
  stage of both Dockerfiles (they must stay identical, ADR-0004).
  → Resolved in 6e0c04f: `UV_CACHE_DIR=/tmp/uv-cache` in both `dev` stages and the DOCKER.md §4.2
  sample; `uv lock --check` and `uv sync --frozen` pass as UID 10001 in both dev images.
- [x] **R2 · Nit** — `services/catalog/pyproject.toml:4` — description is 117 characters,
  over the 100-column convention. Suggested fix: shorten it.
  → Resolved in 754cccf: description shortened to 89 characters.

**Notes**

- Settings deliberately carry only `VO_DATABASE_URL` (required) and `VO_LOG_LEVEL`: the
  catalog calls no other service. `.env.example` (US-01.08) must list them.
- `core`'s `VO_CATALOG_URL` (`http://catalog:8001/`) now points at a running service.

**Rework:** 2026-10-16 · head 055be61 · gates: uv lock --check, uv sync --frozen, ruff,
ruff format, mypy strict + pydantic plugin, pytest 19 passed (coverage 100 % with
`--cov=src/catalog`), `docker compose config`, `make up`/`status` (`catalog` and `core` Up,
UID 10001), dev-image `uv` commands — all pass.

**Owner change during rework:** the project owner asked to rename `agents-catalog` to
`catalog` everywhere. Done in 805969d (folder, package, image, compose, docs, branch renamed
to `feat/us-01-03-catalog-service-package`) and 055be61 (Constitution v3.1.2, ADR-0007).
Accepted ADR-0004 keeps the old name by rule. Not reviewed yet: needs Round 2.

### Round 2 · 2026-10-16 · branch `feat/us-01-03-catalog-service-package` · head `21dd4a3`

Focus: the owner-requested rename `agents-catalog` → `catalog` (805969d, 055be61) and the R1
fix that touched `services/core/Dockerfile`.

**Verdict:** APPROVED

**Quality gate**

| Gate | Result |
| ---- | ------ |
| catalog: `uv lock --check`, `uv sync --frozen` (tool container and `dev` image as UID 10001) | pass |
| catalog: ruff check, ruff format --check, mypy strict + pydantic plugin | pass (12 files) |
| catalog: pytest | 19 passed; coverage 100 % with `--cov=src/catalog` (bare `--cov=catalog` hits the definitions folder, see ADR-0007) |
| core: `uv lock --check`, ruff, ruff format, mypy strict + plugin, pytest (`conftest.py` URL changed) | pass; 19 passed, coverage 100 % |
| core: `dev` image `uv lock --check` / `uv sync --frozen` as UID 10001 | pass |
| `docker compose config`, `make up`, `make status` (`catalog` + `core` Up, UID 10001), `make down` | pass |
| Relative Markdown links in the repository | pass (0 broken) |
| `git grep -E "agents[-_]catalog"` | only accepted ADR-0004, ADR-0007 (file, registry, AGENTS.md), the Amendment Log row and this review history |
| Conventional Commits ≤ 72 chars | pass |
| lint-imports, pin/drift check, `no-latest`, healthcheck, frontend gates, Playwright | not available (US-01.04, US-01.09, WP02, US-01.05+) |

**Acceptance** — AC1–AC5 hold under the new name: `services/catalog/src/catalog/`,
`services/catalog/catalog/{roles,prompts,characters,evals}`, `services/catalog/Dockerfile`,
compose service `catalog` with `build.context: services/catalog`. The story text in the WP
file and ROADMAP now reads "Scaffold the `catalog` service package".

**Findings**

None open.

**Notes**

- The Constitution was amended in the same change (PATCH v3.1.2, ADR-0007 marked Accepted as
  the owner's direct instruction); the owner should confirm that status.
- ADR-0007's compliance grep also matches this review file's history; harmless.
- US-01.04 must configure coverage with `source_pkgs = ["catalog"]` or a path, not a bare
  `catalog` source.

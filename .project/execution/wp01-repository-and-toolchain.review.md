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

## US-01.04 — Configure quality tools and architecture contracts

### Round 1 · 2026-10-16 · branch `feat/us-01-04-quality-tools-and-contracts` · head `3ddb41d`

**Verdict:** CHANGES REQUESTED

**Quality gate**

Run in a throwaway container from the pinned `python:3.15.0-slim-trixie` + `uv 0.13.1` images
(repository mounted) and in the `dev` targets of both service Dockerfiles.

| Gate | Result |
| ---- | ------ |
| `uv lock --check`, `uv sync --frozen` (core, catalog; `anyio==4.15.1` added to dev) | pass |
| ruff check (BACKEND.md §3 rule sets), ruff format --check — core, catalog, scripts | pass |
| mypy (strict, pydantic plugin, `warn_unreachable`) — core 19 files, catalog 13, scripts 7 | pass |
| lint-imports — core 3 contracts kept, catalog 2 kept | pass |
| pytest (default selection) — core 19, catalog 19 | pass; coverage 100 %, `fail_under = 70` reached |
| pytest `-m tooling` — core 7, catalog 7 (T201, no-untyped-def, pydantic call-arg, domain → sqlalchemy) | pass (each fixture rejected by its tool) |
| pytest `scripts/tests` | 20 passed |
| `python -I scripts/check_python_pins.py`, `check_service_config_drift.py` on the repository | exit 0 |
| `python -I scripts/check_coverage.py` on both services' JSON reports | exit 0 |
| `make up` / `make status` / `make down` | pass |
| `no-latest` script | not available (US-01.09); manual grep in the diff: 0 hits |
| frontend gates, healthcheck, Playwright | not available (US-01.05+, WP02, WP14+) |

**Acceptance**

- AC1 — `[tool.ruff.lint] select` = BACKEND.md §3 (`services/*/pyproject.toml`);
  `test_ruff_rejects_a_print_call` asserts T201.
- AC2 — `strict = true`, `plugins = ["pydantic.mypy"]`; `test_mypy_rejects_an_untyped_function`,
  `test_mypy_checks_pydantic_models_with_the_plugin` (fails only with the plugin).
- AC3 — BACKEND.md §2.1 contracts; `test_lint_imports_rejects_a_domain_module_importing_sqlalchemy`
  copies `src/` to a temp folder, adds the import, expects the broken contract; the clean
  service passes.
- AC4 — `branch = true`, `fail_under = 70`; domain 95 / application 90 / others 70 in
  `scripts/check_coverage.py` with tests per threshold.
- AC5 — `scripts/check_service_config_drift.py` + 5 tests (differing, missing, hard-coded
  package name, repository passes).
- AC6 — `scripts/check_python_pins.py` + parametrized failures with file and requirement.

**Findings**

- [x] **R1 · Major** — `scripts/check_coverage.py:41` — when `--package` matches no file of the
  report (typo, wrong report), every file is skipped and the check exits 0 with no output: the
  gate passes silently (Constitution §18.2, "a rule that cannot fail is not a rule"). Suggested
  fix: fail with a message when no file belongs to the package.
  → Resolved in caf126b: exits 1 with "no measured file belongs to package …";
  `test_fails_when_no_file_belongs_to_the_package`.
- [x] **R2 · Minor** — `scripts/check_coverage.py:52` — `round(percent, 1) >= required` lets
  94.96 % pass the 95 % domain threshold. Suggested fix: compare the unrounded percentage;
  round only for display.
  → Resolved in caf126b: exact comparison, display truncated (94.96 % reads 94.9 %);
  `test_a_threshold_is_not_reached_by_rounding`.

**Notes**

- `"tests/tooling/**" = ["S101", "S603"]` departs from the ROADMAP config table ("per-file
  ignores only for tests (S101)"); still test-only and justified (fixed tool arguments). Record
  it in the story ADR.
- `init_typed` of the pydantic plugin is left off on purpose (settings take URL strings).
- `source_pkgs = ["catalog"]` resolves the coverage caveat of ADR-0007.
- The scripts are not yet run by anything automatic: pre-commit (US-01.10) and CI (WP03)
  must call them.

**Rework:** 2026-10-16 · head caf126b · gates: scripts ruff, ruff format, mypy strict pass;
`pytest scripts/tests` 22 passed; core pytest + `check_coverage.py` on the real report exit 0.

### Round 2 · 2026-10-16 · branch `feat/us-01-04-quality-tools-and-contracts` · head `a59db96`

Focus: the R1/R2 fix (caf126b).

**Verdict:** APPROVED

**Quality gate**

| Gate | Result |
| ---- | ------ |
| scripts: ruff check, ruff format --check, mypy strict | pass |
| `pytest scripts/tests` | 22 passed (R1 and R2 tests fail on the previous code, pass now) |
| core pytest + `check_coverage.py` on the real JSON report | pass (exit 0) |
| service gates (ruff, mypy, lint-imports, pytest, `-m tooling`) | unchanged since Round 1 (no service file touched); pass |
| `no-latest`, frontend gates, healthcheck, Playwright | not available |

**Findings**

None open.

**Notes**

- A package whose modules are all empty is measured as nothing and passes without output;
  correct for the skeleton, and any real statement makes the layer appear.

## US-01.05 — Scaffold the Vue + Vite application

### Round 1 · 2026-10-17 · branch `feat/us-01-05-vue-vite-app` · head `9bf7c29`

**Verdict:** CHANGES REQUESTED

**Quality gate**

Run in the `frontend/Dockerfile` `dev` target (pinned `node:24.22.0-trixie-slim` by digest,
`pnpm install --frozen-lockfile`) and with `make up` from the repository root.

| Gate | Result |
| ---- | ------ |
| `docker compose config -q` | pass |
| image build (`dev` target, frozen lockfile) | pass |
| `pnpm typecheck` (`vue-tsc --build`) | pass |
| `pnpm test` (vitest, 2 files, 2 tests) | pass |
| `pnpm build` (hashed `dist/assets/index-<hash>.js`) | pass |
| `make up` + runtime smoke (200 on `/`, SPA fallback, immutable assets, security headers, UID 10001, JSON logs) | pass |
| ESLint / Prettier | not available (US-01.06) |
| frontend coverage thresholds | not available (US-01.07) |
| `no-latest` check | not available (US-01.09); manual grep: 0 hits |
| Python gates (core, catalog) | not run (diff touches no Python) |
| Playwright / real browser render | not available (WP14+) |

**Acceptance**

- AC1 — nine `src/` folders with `.gitkeep` (`git ls-files frontend`).
- AC2 — `frontend/package.json:8-33` pins every dependency exactly to STACK.md §3,
  `packageManager: pnpm@12.14.0`; `.npmrc` flags mirrored in `pnpm-workspace.yaml` (pnpm 12).
  Verified by inspection only.
- AC3 — `pnpm build` produces hashed assets; `frontend/src/App.spec.ts:15` asserts the title.
- AC4 — `frontend/Dockerfile:3-4` pins both images by tag and digest; `docker-compose.yml`
  serves on `127.0.0.1:8080`; `make up` serves the placeholder (title checked via HTML shell
  and jsdom, not a browser).

**Findings**

- [x] **R1 · Major** — commit `ac7c8d2` — subject `feat(frontend): render the My Workbench
  placeholder with Pinia and router` is 73 characters, over the 72 limit (AGENTS.md rule 16).
  Suggested fix: reword on the feature branch, e.g. `feat(frontend): render My Workbench
  placeholder with Pinia and router` (69).
  → Resolved in 0e8e06a: branch history rewritten (local, never pushed); subject now 69 chars, body and trailers kept, tree unchanged.
- [x] **R2 · Minor** — `frontend/src/router.ts:12` — the root route uses an inline
  `{ name, render: () => null }` component object, against FRONTEND.md §3 rule 1
  (`<script setup lang="ts">` SFCs only); `frontend/src/App.vue:3-7` has no `<RouterView/>`,
  so routes never render. Suggested fix: add `src/windows/WorkbenchDesktop.vue` (empty
  `<script setup lang="ts">`), point the route at it and render `<RouterView/>` in `App.vue`.
  → Resolved in 7530c13: `src/windows/WorkbenchDesktop.vue` SFC rendered through `<RouterView/>`; `App.spec.ts` asserts it.
- [x] **R3 · Minor** — `frontend/Dockerfile:33-35` — nginx config and `dist` are
  `--chown=10001:10001`, so the runtime can rewrite its own config and web root (DOCKER.md
  §4.1 least privilege). Suggested fix: copy them root-owned (0644), keep the chown on
  `/var/cache/nginx` only; update the DOCKER.md §4.3 snippet.
  → Resolved in f069ce3: nginx config and `dist` copied root-owned (0644); UID 10001 gets "Permission denied" writing them; DOCKER.md §4.3 synced in 014494c.
- [x] **R4 · Minor** — `frontend/nginx.conf:38` — `/ws` does not forward `X-Forwarded-For` /
  `X-Forwarded-Proto` while `/api/` does (`:34-35`); core trusts proxy headers. Suggested fix:
  add the same two `proxy_set_header` lines to `/ws`.
  → Resolved in 86fdf5a: `/ws` forwards `X-Forwarded-For` and `X-Forwarded-Proto`.
- [x] **R5 · Minor** — `frontend/Dockerfile:41-43` — `COPY . ./` then `chown -R /app` duplicates
  the tree (including `node_modules`) in a second layer (DOCKER.md §4.1: `COPY --chown`).
  Suggested fix: create the user first and use `COPY --chown=10001:10001`.
  → Resolved in f069ce3: user created in `base`, `COPY --chown=10001:10001` plus a non-recursive chown of `/app` and `/app/node_modules`; the layers are 68.9 kB and 0 B.
- [x] **R6 · Minor** — `frontend/Dockerfile:42` — the dev user has `--no-create-home`, so `HOME`
  points to a missing directory where pnpm/corepack write cache and state (same class of issue
  as ADR-0008 `UV_CACHE_DIR`). Suggested fix: `ENV HOME=/tmp` (or `XDG_*` to `/tmp`) and
  confirm `pnpm typecheck && pnpm test && pnpm build` as UID 10001.
  → Resolved in f069ce3: `ENV HOME=/tmp` in `dev`; `pnpm typecheck && pnpm test && pnpm build` pass as UID 10001.
- [x] **R7 · Minor** — `.docs/STACK.md:30` — §1 rule 4 still says only `save-exact=true` in
  `.npmrc`; pnpm 12 ignores it and the branch enforces `saveExact`/`engineStrict` in
  `frontend/pnpm-workspace.yaml`. STACK.md outranks FRONTEND.md. Suggested fix: add the
  `pnpm-workspace.yaml` settings to STACK.md §1.4.
  → Resolved in 014494c: STACK.md §1.4 names the `pnpm-workspace.yaml` `saveExact`/`engineStrict` settings.
- [x] **R8 · Minor** — `.docs/FRONTEND.md:28` — layout says `App.vue # <WorkbenchScreen/>`
  while the code renders a placeholder `<h1>`. Suggested fix: note "(placeholder until WP08)"
  or record the gap in the story ADR.
  → Resolved in 014494c: FRONTEND.md layout marks `App.vue` as a placeholder until WP08.
- [x] **R9 · Minor** — `frontend/package.json:8-33` — AC2 pins are checked only by inspection;
  no automated check fails on a `^` range or drift from STACK.md §3 (`scripts/check_python_pins.py`
  covers Python only). Suggested fix: extend the pin check to `frontend/package.json`, or record
  the deferral to US-01.09/US-01.10 in the story ADR.
  → Resolved in 3ee2048: `scripts/check_frontend_pins.py` (stdlib, `python -I`) with 9 tests; exits 0 on the repository.
- [x] **R10 · Minor** — `frontend/Dockerfile:22-37`, `docker-compose.yml` — AC3/AC4 verified by
  hand only. Suggested fix: state in the story ADR that WP02/WP03 smoke and healthchecks
  automate them.
  → Resolved at close in ADR-0010 (Decision 12): AC3/AC4 verified by hand (`pnpm build` in the dev image, `make up` + curl smoke); WP02 healthchecks and WP03 CI smoke automate them.
- [x] **R11 · Nit** — `frontend/Dockerfile:6` — no `base` stage (DOCKER.md §4.1 lists
  `base → deps → build → runtime`). Suggested fix: add it, or document the Node exception.
  → Resolved in f069ce3: `base` stage added (user, WORKDIR, corepack).
- [x] **R12 · Nit** — `frontend/nginx.conf:38` — prefix `location /ws` also matches `/wsfoo`.
  Suggested fix: `location = /ws` (and DOCKER.md §4.3).
  → Resolved in 86fdf5a: `location = /ws`; `/wsfoo` now gets the SPA fallback; DOCKER.md §4.3 synced in 014494c.
- [x] **R13 · Nit** — no favicon; `/favicon.ico` falls through to `index.html` with 200 HTML.
  Suggested fix: placeholder favicon in `public/`, or `location = /favicon.ico { return 404; }`.
  → Resolved in 86fdf5a: `location = /favicon.ico` returns 404 until WP12 assets add a favicon in `public/`.
- [x] **R14 · Nit** — `frontend/src/router.ts:15` — the `'web' | 'memory'` switch is a test seam
  in the production API. Suggested fix: inject `history: RouterHistory = createWebHistory()`.
  → Resolved in 7530c13: `createWorkbenchRouter(history: RouterHistory = createWebHistory())`; specs inject `createMemoryHistory()`.
- [x] **R15 · Nit** — `frontend/src/App.vue:4-5` — placeholder uses browser defaults, no
  DESIGN.md tokens; acceptable until WP07 tokens exist. Suggested fix: say so in the story ADR.
  → Resolved at close in ADR-0010 (Decision 6): the placeholder `App.vue` uses browser defaults, no DESIGN.md tokens, until the WP07 tokens exist (comment added in 7530c13).

**Rework:** 2026-10-17 · head 3ee2048 · gates: frontend `dev` image as UID 10001 `pnpm typecheck`,
`pnpm test` (2 files, 3 tests), `pnpm build` pass; `docker compose config -q` pass; `make up` +
smoke (200 on `/` and deep link, `/healthz`, `/favicon.ico` 404, `/ws` reaches core, `/wsfoo` SPA
fallback, immutable assets, security headers, root-owned nginx files, UID 10001) pass, `make down`;
`pytest scripts/tests` 31 passed, scripts ruff, ruff format, mypy strict pass,
`check_frontend_pins.py` and `check_python_pins.py` exit 0; all subjects ≤ 72 chars.
ESLint/Prettier, frontend coverage, `no-latest`, Playwright: not available.

**Notes**

- Pins, digests, lockfile integrity and the compose entry follow STACK.md and ADR-0004/0005/0006.
- nginx re-includes security headers in every location, has `/healthz`, SPA fallback, correct
  cache policy, JSON logs and `server_tokens off`.
- Commit bodies document the pnpm 12 `.npmrc` behaviour well; for the ADR: no `@` alias yet,
  `depends_on: [core]` because nginx needs a resolvable upstream (WP02 hardens).

### Round 2 · 2026-10-17 · branch `feat/us-01-05-vue-vite-app` · head `31e763d`

**Verdict:** APPROVED

**Quality gate**

Run in the `frontend/Dockerfile` `dev` target as UID 10001 (`HOME=/tmp`), the core `dev` image
for `scripts/`, and `make up` from the repository root.

| Gate | Result |
| ---- | ------ |
| `pnpm typecheck` | pass (exit 0; pre-run install noise, see R16) |
| `pnpm test` (2 files, 3 tests) | pass (same noise) |
| R2 mutation (remove `<RouterView/>`) | fails as expected |
| `pnpm build` (hashed assets) | pass (same noise) |
| `docker compose config -q` | pass |
| `make up` + curl smoke (`/`, deep link, `/healthz`, favicon 404, `/wsfoo` fallback, `/ws` reaches core, immutable assets, root-owned nginx config) | pass |
| `pytest scripts/tests` (31 tests, branch coverage 95 %) | pass |
| `ruff check` / `ruff format --check` / `mypy --strict` on `scripts/` | pass |
| `check_frontend_pins.py`, `check_python_pins.py`, `check_service_config_drift.py` | pass |
| ESLint/Prettier, frontend coverage, `no-latest`, Playwright | not available (US-01.06, US-01.07, US-01.09, WP14+) |

**Round 1 follow-up** — R1–R9, R11–R14 verified fixed. R10 and R15 are ADR items that are
still pending until `/feature-close` writes the story ADR (see R17).

**Findings**

- [x] **R16 · Minor** — `frontend/Dockerfile:51` — the non-recursive chown (R5) leaves
  `node_modules/.bin` and `.modules.yaml` root-owned, so every `pnpm <script>` as UID 10001
  prints `ERR_PNPM_PACKAGE_MANAGER_REMOVE_MODULES_DIR … Permission denied` from
  `verifyDepsBeforeRun`; gates pass only because it is a warning. Suggested fix: chown those
  paths too (or disable `verifyDepsBeforeRun` with a reason) and confirm no `ERR_PNPM` output.
  → Resolved in c869458: root cause was the 0600 root-owned `node_modules/.pnpm-workspace-state-v1.json` (unreadable, so pnpm assumed stale deps and tried a reinstall); the dev stage chowns that file (855 B layer); `pnpm typecheck && pnpm test && pnpm build` as UID 10001 print no `ERR_PNPM`; DOCKER.md §4.3 synced.
- [x] **R17 · Minor** — `.project/execution/wp01-repository-and-toolchain.review.md` (Round 1
  R10, R15) — ticked "Resolved at close" although no ADR exists yet (feature-rework.md:32-33,
  AGENTS.md rule 15). Suggested fix: mark them "Deferred to /feature-close (story ADR)" until
  close records them and writes the ADR id.
  → Resolved in this rework (review file): Round 1 R10 and R15 unticked and marked "Deferred to /feature-close (story ADR)".
- [x] **R18 · Minor** — `.docs/FRONTEND.md:36` — the §1 layout does not show the new
  `src/windows/WorkbenchDesktop.vue`; `windows/` is described as "one folder per Workbench
  window". Suggested fix: add a layout line for the root-route view (moved/reshaped in WP08).
  → Resolved in 7dbcc12: §1 layout lists `windows/WorkbenchDesktop.vue` as the root-route placeholder reshaped in WP08.
- [x] **R19 · Nit** — `.docs/FRONTEND.md:18-19` — no pointer to `scripts/check_frontend_pins.py`
  (only STACK.md §1.4 and BACKEND.md mention it). Suggested fix: one line next to the
  `.npmrc` / `pnpm-workspace.yaml` entries.
  → Resolved in 7dbcc12: §1 layout points to `scripts/check_frontend_pins.py` (BACKEND.md §11) under `pnpm-workspace.yaml`.
- [x] **R20 · Nit** — `scripts/check_frontend_pins.py:81-84` — no test for a STACK.md §3 without
  a Node.js/pnpm row (branch uncovered, file at 94 %). Suggested fix: one fixture test expecting
  exit 1 and the message.
  → Resolved in 302f133: fixture test without the Node.js/pnpm rows expects exit 1 and the message; file at 98 % (only `__main__` uncovered).

**Rework:** 2026-10-17 · head 7dbcc12 · gates: frontend `dev` image as UID 10001
`pnpm typecheck && pnpm test` (2 files, 3 tests) `&& pnpm build` exit 0 with 0 `ERR_PNPM`/warn
lines; `docker compose config -q` pass; `make up` + curl smoke (`/` and deep link 200, `/healthz`
200, `/favicon.ico` 404, `/wsfoo` SPA fallback 200, CSP and nosniff headers) pass, `make down`;
core `dev` image: `pytest scripts/tests` 32 passed (branch coverage 96 %), `ruff check`,
`ruff format --check`, `mypy --strict` on `scripts/` pass, `check_frontend_pins.py` exit 0.
ESLint/Prettier, frontend coverage, `no-latest`, Playwright: not available.

**Notes**

- Ownership hardening, `location = /ws`, the router history injection and the new pin check
  are clean; all commit subjects are ≤ 72 characters with the trailer.

## US-01.06 — Strict TypeScript and lint configuration

### Round 1 · 2026-10-17 · branch `feat/us-01-06-strict-ts-and-lint-config` · head `137c2f9`

**Verdict:** CHANGES REQUESTED

**Quality gate**

Run in the `frontend/Dockerfile` `dev` target as UID 10001 and in the core `dev` image for
`scripts/`; mutations ran on throwaway copies inside containers.

| Gate | Result |
| ---- | ------ |
| image build, `dev` and `runtime` targets (no fixtures in the web root) | pass |
| `pnpm lint` (`--max-warnings 0`) | pass |
| `pnpm format:check` | pass |
| `pnpm typecheck` | pass |
| `pnpm test` (2 files, 3 tests) | pass |
| `pnpm build` | pass |
| `pnpm check:tooling` (8 expected errors) | pass |
| tooling check mutation test (17 mutations) | 15 caught, 2 survived (R2) |
| `docker compose config -q` | pass |
| `python -I scripts/check_frontend_pins.py`, `pytest scripts/tests` (32) | pass |
| frontend coverage thresholds | not available (US-01.07) |
| CI | not available (WP03) |

**Acceptance**

- AC1 — `frontend/tsconfig.app.json:9-19`; asserted by `tooling-fixtures/check-tooling.ts:17-28,69-82`
  (four tsconfig mutations each failed the check).
- AC2 — `tooling-fixtures/src/windows/OptionsApiWindow.vue:5` fails with
  `vue/component-api-style` (`check-tooling.ts:31-35`).
- AC3 — `office-engine` fixtures importing `vue` / `pixi.js` fail with `boundaries/dependencies`;
  probes in the real `src/` confirm the rules apply beyond the fixtures.
- AC4 — `pnpm format:check` exits 0; `.prettierrc.json` matches FRONTEND.md §11.

**Findings**

- [x] **R1 · Major** — `frontend/eslint.config.ts:32-39,60-61` — the no-audio lint covers only
  Web Audio globals and three libraries; Constitution §14.10 also names `<audio>`/`<video>` with
  sound, and ROADMAP.md:371 asks for "any audio API or library anywhere". Missing:
  `vue/no-restricted-html-elements` for `audio` (and `video` without `muted`), `speechSynthesis` /
  `SpeechSynthesisUtterance`, `HTMLAudioElement`, `window.Audio` / `globalThis.AudioContext`
  (`no-restricted-properties`), `document.createElement('audio')`. Suggested fix: add the rules,
  fixtures (including an SFC with `<audio>`) and expectations, and update FRONTEND.md §8.6/§11. → Resolved in 571ee84: bans `HTMLAudioElement`, `speechSynthesis`, `SpeechSynthesisUtterance` (globals and `window`/`globalThis`/`self` properties), `document.createElement('audio')`, `<audio>` and `<video>` without `muted`; fixtures `shared/uses-audio.ts`, `windows/AudioWindow.vue`; docs in 2136ae1.
- [x] **R2 · Major** — `frontend/tooling-fixtures/src/shared/uses-audio.ts:2`,
  `frontend/eslint.config.ts:36-41,84-89` — the audio-import ban is not really tested: `@pixi/sound`
  also matches the `@pixi/*` pattern, so replacing the audio group with `['xxx']` or emptying the
  `office-renderer` override's `patterns: [audioImports]` both leave `check:tooling` green. The
  fixture also skips `howler`, `tone`, `OfflineAudioContext`, `webkitAudioContext`. Suggested fix:
  shared fixture imports `howler`/`tone`; add `tooling-fixtures/src/office-renderer/imports-sound.ts`
  importing `@pixi/sound`; one line per banned name; optionally match the §14.10 message text. → Resolved in 571ee84: one fixture line per banned import/global, `office-renderer/imports-sound.ts`, expectations match the §14.10 message; container mutation run: emptying the audio group or the `office-renderer` override, dropping `@pixi/sound`/`howler`/`tone`/any global now fails the check (redundant `/*` entries removed).
- [x] **R3 · Major** — `frontend/eslint.config.ts:108-111` — catch-all `from '*' → allow external`
  lets `shared` (and `api`) import `vue`, `pinia`, `vue-router`; FRONTEND.md §1 says `shared/` is
  "no Vue" and §1.1 "nothing else". Suggested fix: disallow those externals for `shared` (and
  `api`), with a `shared/imports-vue.ts` fixture and expectation. → Resolved in 571ee84: `shared` and `api` disallow `vue`, `vue-router`, `pinia`, `@vue/*`; fixtures `shared/imports-vue.ts`, `api/imports-pinia.ts`.
- [x] **R4 · Major** — `frontend/tooling-fixtures/check-tooling.ts:30-59` — with
  `default: 'disallow'` only negative edges are proven; no fixture shows the allowed edges pass
  (renderer→engine, stores→engine `import type`, engine→api `import type`, composables→stores,
  ui-amiga→composables, intra-element). `src/` is empty, so a green `pnpm lint` proves nothing
  (ADR-0009: every rule proven). Suggested fix: positive fixtures asserted to have zero
  `boundaries/dependencies` messages. → Resolved in 571ee84: 11 positive fixtures (every allowed §1.1 edge, `import type` edges, intra-element, muted `<video>`) must produce zero messages; mutation run removing any allowed edge fails the check.
- [x] **R5 · Major** — `.docs/DOCKER.md:329-330` — gate commands not updated: line 329 lacks
  `pnpm format:check` and `pnpm check:tooling`; the interim line 330 runs only
  `typecheck && test && build`, so lint, Prettier and the negative fixtures never run in the
  documented container gate (Constitution §18.2). Suggested fix: add
  `pnpm lint && pnpm format:check && pnpm check:tooling` to both. → Resolved in 2136ae1: both DOCKER.md gate lines run `lint`, `format:check` and `check:tooling`.
- [x] **R6 · Minor** — `frontend/tooling-fixtures/check-tooling.ts:30-59` — no fixture covers
  `no-restricted-exports` (FRONTEND.md §2 rule 5, `eslint.config.ts:64-82`). Suggested fix:
  `tooling-fixtures/src/shared/default-export.ts` plus expectation. → Resolved in 571ee84: `shared/default-export.ts` fails with `no-restricted-exports`.
- [x] **R7 · Minor** — `.docs/FRONTEND.md:250-251,296` — says `no-restricted-globals` covers
  `Audio`/`AudioContext` only; config bans more. Suggested fix: list the full sets (after R1). → Resolved in 2136ae1: FRONTEND.md §8.6 and §11 list the full rule sets.
- [ ] **R8 · Minor** — `frontend/eslint.config.ts:47` + `tooling-fixtures/` — ADR-0009
  Alternative 3 rejected committed, lint-excluded fixtures; the departure (typed linting needs a
  tsconfig; ignore scoped to `tooling-fixtures/src/`) is not recorded. Suggested fix: record it in
  the story ADR. → Deferred to /feature-close (story ADR).
- [ ] **R9 · Minor** — `frontend/package.json:17`, `frontend/eslint.config.ts:1-2` — ESLint's
  `unstable_native_nodejs_ts_config` flag can be renamed/removed in a minor release (spirit of
  STACK.md §1.1 "stable only"). Suggested fix: record in the story ADR with rejected alternatives
  (`jiti`, `eslint.config.js`) and a re-check trigger; optionally a STACK.md §9 watch row. → Deferred to /feature-close (story ADR).
- [x] **R10 · Minor** — `frontend/pnpm-workspace.yaml:6-10` — `minimumReleaseAgeExclude:
  eslint@10.13.0` disables a supply-chain control and is undocumented in STACK.md §1.4; the
  quarantine expires within about a day of 2026-10-16. Suggested fix: remove it once the lock
  resolves without it, or document a release-age policy in STACK.md §1 / the ADR. → Resolved in 7c12cac: a frozen install without the entry still fails on 2026-10-17 (eslint 10.13.0 published 2026-10-16T14:24Z), so it stays; STACK.md §1.4 documents the exemption policy and removal trigger.
- [x] **R11 · Minor** — `frontend/eslint.config.ts:135` — `ui-amiga → composables` allows every
  composable, though §1.1 says "generic ones only" (composables may reach stores). Suggested fix:
  document the limitation in FRONTEND.md §11 or classify generic composables separately. → Resolved in 2136ae1: limitation documented in FRONTEND.md §11 (generic-only checked in review); §1.1 unchanged.
- [x] **R12 · Minor** — `frontend/eslint.config.ts:115` — `typesOnly('api')` allows types from any
  `api/` file; §1.1 restricts `office-engine` to `api/schema.d.ts` while §2 rule 4 names
  `api/types.ts`. Suggested fix: narrow the rule, or align §1.1 with §2 rule 4 and the config. → Resolved in 571ee84: `office-engine` type imports narrowed to `api/schema.d.ts` (`fileInternalPath`), faithful to §1.1; fixture `office-engine/imports-api-module.ts`; documented in 2136ae1.
- [x] **R13 · Nit** — `frontend/eslint.config.ts:9-11` — unclassified files (`router.ts`,
  `assets/`) are unchecked, so `shared → ../router` passes. Suggested fix: note `router.ts` in
  FRONTEND.md §11 or classify it. → Resolved in 2136ae1: FRONTEND.md §11 documents that imports of unclassified files (e.g. `shared` → `../router`) are not checked and §1.1 is checked in review.
- [x] **R14 · Nit** — `frontend/tooling-fixtures/check-tooling.ts:70` — `JSON.parse` breaks on JSONC
  and ignores `extends`. Suggested fix: `ts.readConfigFile` / `parseJsonConfigFileContent`. → Resolved in 571ee84: `ts.readConfigFile` + `parseJsonConfigFileContent` (JSONC and `extends` verified in a container copy).
- [x] **R15 · Nit** — `frontend/tooling-fixtures/check-tooling.ts:98` — `${cwd}/${file}` assumes
  POSIX paths. Suggested fix: `path.join`. → Resolved in 571ee84: `path.resolve`.
- [x] **R16 · Nit** — `frontend/tooling-fixtures/check-tooling.ts` — strict `tsconfig.node.json`
  is not asserted. Suggested fix: check the same options there. → Resolved in 571ee84: `tsconfig.node.json` checked with the same options and `types: ["node"]`.

**Notes**

- The tooling check asserts rule id, file, line and severity and rejects fatal parse errors — the
  ADR-0009 lesson applied well; 15 of 17 mutations caught.
- New pins (`eslint-config-prettier` 10.1.8, `@types/node` 24.19.2 with a §9 hold) are exact and in
  STACK.md; everything stays inside `frontend/` (ADR-0004).
- ROADMAP.md:375-376 `test:watch` and `coverage` scripts correctly left to US-01.07.

**Rework:** 2026-10-17 · head 7c12cac · gates: dev image as UID 10001 `pnpm lint`, `format:check`, `typecheck`, `test` (3), `build`, `check:tooling` (32 expected errors, 11 clean positives) pass; runtime target build pass (no fixtures in web root); container mutation runs on throwaway copies: 33 config mutations with 2 survivors (redundant `@pixi/sound/*` and `windows` → `windows` entries, then removed), 7 re-run on the final config all caught, 2 tsconfig mutations caught and JSONC/`extends` variants accepted; `docker compose config -q` pass; `check_frontend_pins.py` and `pytest scripts/tests` (32) pass; coverage n/a (US-01.07), CI n/a (WP03).

### Round 2 · 2026-10-17 · branch `feat/us-01-06-strict-ts-and-lint-config` · head `b395418`

**Verdict:** APPROVED

**Quality gate**

Fresh temp images; `frontend/Dockerfile` `dev` target as UID 10001, core `dev` image for
`scripts/`; mutations on throwaway copies inside containers.

| Gate | Result |
| ---- | ------ |
| `pnpm lint` (`--max-warnings 0`) | pass |
| `pnpm format:check` | pass |
| `pnpm typecheck` | pass |
| `pnpm test` (2 files, 3 tests) | pass |
| `pnpm build` | pass |
| `pnpm check:tooling` (32 expected errors, 11 clean positive fixtures) | pass |
| `ERR_PNPM` output in any gate | 0 hits |
| runtime target build (no fixtures in web root, UID 10001) | pass |
| tooling check mutation test (30 mutations) | 30 caught, 0 survived |
| `docker compose config -q` | pass |
| `check_frontend_pins.py`, `pytest scripts/tests` (32) | pass |
| frontend coverage thresholds | not available (US-01.07) |
| CI | not available (WP03) |

**Round 1 follow-up** — R1–R7, R10–R16 verified fixed (mutations confirm R2, R4, R6, R12, R16).
R8 and R9 remain open, deferred to the story ADR at `/feature-close`.

**Findings**

- [ ] **R17 · Minor** — `.docs/STACK.md:39-40` — the release-age bullet was inserted inside the
  npm bullet, so the `check_frontend_pins.py` sentence now reads as part of the quarantine policy.
  Suggested fix: move lines 39-40 back to the end of the npm bullet (or their own bullet).
- [ ] **R18 · Minor** — `.docs/STACK.md:10-11,33-38` — "Changing anything here requires a
  repository ADR", but the new §1.4 release-age policy has none and R10 does not defer it.
  Suggested fix: mark it "Deferred to /feature-close (story ADR)" and record it in the story ADR.
- [ ] **R19 · Minor** — `.docs/STACK.md:37-38`, `frontend/pnpm-workspace.yaml:8-9` — the removal
  trigger joins two conditions, so the exemption lingers as dead config until the next eslint bump.
  Suggested fix: "removed as soon as a frozen install passes without it, and at the latest at the
  next update of that package".
- [ ] **R20 · Minor** — `frontend/eslint.config.ts:152` — the `office-engine` disallow list omits
  `@vue/*` (FRONTEND.md:309-310, §1.1 "no `vue`"). Suggested fix: one shared `frameworkPackages`
  constant for both policies.
- [ ] **R21 · Minor** — `frontend/tooling-fixtures/src/shared/imports-vue.ts:2-4` — no fixture
  imports a `@vue/*` package, so that entry is never proven (ADR-0009). Suggested fix: add a
  `@vue/reactivity` line with its expectation here and in `office-engine` (after R20).
- [ ] **R22 · Minor** — `frontend/eslint.config.ts:31-61` — importing an audio asset
  (`*.mp3`, `*.ogg`, …) still passes lint, though FRONTEND.md:42,249 say "no audio files"
  (Constitution §14.10). Suggested fix: an audio-extension group in `no-restricted-imports` with a
  fixture line, or state in FRONTEND.md §11 that WP12's asset check covers it.
- [ ] **R23 · Nit** — `frontend/eslint.config.ts:53-56` — `audioElementCreation` matches only the
  literal `'audio'`; misses `createElement('video')`, template literals, `createElementNS`.
  Suggested fix: extend to `/^(audio|video)$/i`, or list the limit in FRONTEND.md §8.6/§11.
- [ ] **R24 · Nit** — `frontend/eslint.config.ts:59` — `:has(...)` matches descendants, so
  `<source muted>` would satisfy the `<video>` rule. Suggested fix: restrict to the `VStartTag`'s
  own attributes, or note it.
- [ ] **R25 · Nit** — `frontend/eslint.config.ts:135-139` — the catch-all lets `office-renderer`
  import `vue`/`pinia`/`vue-router`; FRONTEND.md §1.1 lists only PixiJS for it. Suggested fix: add
  the framework disallow, or state in §11 that it is accepted.
- [ ] **R26 · Nit** — `frontend/tooling-fixtures/tsconfig.json:2` — comment says "negative fixtures
  only" but positives live there too. Suggested fix: "lint fixtures".
- [ ] **R27 · Nit** — `frontend/tooling-fixtures/check-tooling.ts:178` — `describe` lacks an
  explicit return type and shadows the Vitest global. Suggested fix: `formatMessage(...): string`.
- [ ] **R28 · Nit** — `.docs/FRONTEND.md:250-251` — "Web Audio and speech globals" omits
  `HTMLAudioElement`. Suggested fix: reword or point to §11.
- [ ] **R29 · Nit** — `.docs/DOCKER.md:329` — the compose gate line lacks `pnpm build`, unlike
  `:330`. Suggested fix: add it.
- [ ] **R30 · Nit** — `.project/ROADMAP.md:444` — deliverables still list only `@pixi/sound` and
  `Audio`/`AudioContext`. Suggested fix: update, or leave as plan text.

**Notes**

- Every banned audio name has its own fixture line and expectations check the §14.10 message; all
  allowed §1.1 edges are now proven both ways.

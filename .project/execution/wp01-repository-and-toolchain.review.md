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

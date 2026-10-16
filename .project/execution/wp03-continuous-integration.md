# WP03 — Continuous Integration

| Field        | Value |
| ------------ | ----- |
| Milestone    | M0 — Boot Disk |
| Status       | READY |
| Depends on   | WP01, WP02 |
| Enables      | All later WPs (quality gate) |
| Constitution | Article XVIII (§18.2), Article XVII (§17.6) |
| Guides       | [STACK.md](../../.docs/STACK.md) §8 · [DOCKER.md](../../.docs/DOCKER.md) §7 · [PRINCIPLES.md](../../.docs/PRINCIPLES.md) §2–3 |
| Skills       | `delivering-features` |
| Estimate     | 21 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-03.01 — Backend checks job (3 pts)
- [ ] US-03.02 — Frontend checks job (3 pts)
- [ ] US-03.03 — Repository checks job (2 pts)
- [ ] US-03.04 — Multi-arch image build (3 pts)
- [ ] US-03.05 — Vulnerability scan (2 pts)
- [ ] US-03.06 — Compose smoke test in CI (3 pts)
- [ ] US-03.07 — Coverage enforcement and reports (2 pts)
- [ ] US-03.08 — Contract and palette checks (3 pts)

## 1. Objective

Every pull request is verified automatically by the full quality gate of Constitution §18.2,
fast enough (< 15 min end to end) that integrating daily is painless, so `main` is always
releasable.

## 2. Scope

**In:** GitHub Actions workflows (PR, main, nightly), caching, image builds, Trivy scan,
compose smoke test, coverage enforcement, OpenAPI drift and palette checks (skeletons), branch
protection documentation.

**Out:** E2E feature tests (added by each feature WP), release automation (WP24).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D03.1 | PR pipeline | Lint, format, types, boundaries, unit tests for backend and frontend in parallel jobs, < 10 min | Green run on a PR; a deliberately broken PR fails the right job | US-03.01 – US-03.03 |
| D03.2 | Images & scan | Multi-arch image builds with cache; Trivy blocking fixable HIGH/CRITICAL | Build job artifacts; Trivy report in job summary | US-03.04 – US-03.05 |
| D03.3 | Compose smoke | Full stack up in CI with `VO_LLM_MODE=fake`; smoke script passes | Job runs `infra/tests/smoke.sh` green | US-03.06 |
| D03.4 | Quality reports | Coverage thresholds, OpenAPI drift check, OCS palette check, `no-latest` | Each check fails on its negative fixture | US-03.07 – US-03.08 |

## 4. User stories

### D03.1 — PR pipeline

#### US-03.01 — Backend checks job

- [ ] **US-03.01 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a reviewer, I want every PR to run ruff, mypy, import-linter and pytest unit
  tests for both Python services, so that I only review behavior.
- **Acceptance criteria:**
  - [ ] AC1 — Given a PR, when the workflow runs, then job `backend-checks` runs inside the `dev` image
    of each service (no host Python setup) and executes the commands of DOCKER.md §6.
  - [ ] AC2 — Given a ruff, mypy, import or test failure, when it occurs, then the job fails with the
    tool output visible in the log and summary.
  - [ ] AC3 — Given unchanged dependencies, when the job runs twice, then the second run uses the
    BuildKit cache and finishes ≥ 40 % faster.
- **Tasks:** `.github/workflows/pr.yml` job; all actions pinned by commit SHA with version
  comment.
- **Tests:** a throwaway PR with an injected failure per tool (documented in the PR).
- **Done when:** job required in branch protection.

#### US-03.02 — Frontend checks job

- [ ] **US-03.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a reviewer, I want ESLint, Prettier, vue-tsc and Vitest to run on every PR.
- **Acceptance criteria:**
  - [ ] AC1 — Given a PR, when `frontend-checks` runs in the frontend `deps` image, then lint, format
    check, typecheck and unit tests with coverage run.
  - [ ] AC2 — Given the pnpm store cache, when dependencies are unchanged, then install takes < 30 s.
  - [ ] AC3 — Given a failure, then the job fails and the coverage summary is posted to the job summary.
- **Tasks:** job definition, cache keys on `pnpm-lock.yaml`.
- **Tests:** injected failure PR.
- **Done when:** job required.

#### US-03.03 — Repository checks job

- [ ] **US-03.03 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want `no-latest`, Renovate config validation and Markdown
  link checks on every PR, so that policy and docs never rot.
- **Acceptance criteria:**
  - [ ] AC1 — `no-latest` runs and fails on any hit (US-01.09).
  - [ ] AC2 — Renovate config validator runs when `renovate.json` changes.
  - [ ] AC3 — Internal Markdown links in `.docs/`, `.project/`, `AGENTS.md` and `.agents/` are checked;
    a broken relative link fails the job.
- **Tasks:** job; link checker pinned by version (offline mode, internal links only).
- **Tests:** fixture with a broken link.
- **Done when:** job required.

### D03.2 — Images and scan

#### US-03.04 — Multi-arch image build

- [ ] **US-03.04 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As an operator, I want CI to build all images for amd64 and arm64 with caching.
- **Acceptance criteria:**
  - [ ] AC1 — Given `docker-bake.hcl` mirroring compose services, when `docker buildx bake` runs, then
    `frontend`, `core`, `agents-catalog` build for both platforms.
  - [ ] AC2 — Given images, when tagged, then the tag is the commit SHA; nothing is pushed in v1.
  - [ ] AC3 — Given `infra/tests/check_images.sh` (US-02.03), when run, then it passes.
- **Tasks:** bake file, workflow job with GitHub Actions cache backend.
- **Tests:** CI run.
- **Done when:** job required.

#### US-03.05 — Vulnerability scan

- [ ] **US-03.05 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a security-minded owner, I want images scanned and PRs blocked on fixable
  HIGH/CRITICAL vulnerabilities.
- **Acceptance criteria:**
  - [ ] AC1 — Given built images, when Trivy (pinned version) scans them, then fixable HIGH/CRITICAL
    findings fail the job.
  - [ ] AC2 — Given findings, then a table is written to the job summary.
  - [ ] AC3 — Given an accepted risk, when documented in `.trivyignore` with an expiry date and ADR
    reference, then it is ignored until the expiry.
- **Tasks:** job, `.trivyignore` policy comment.
- **Tests:** CI run.
- **Done when:** job required.

### D03.3 — Compose smoke

#### US-03.06 — Compose smoke test in CI

- [ ] **US-03.06 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want CI to start the real stack and check it, so that "it
  works on my machine" never happens.
- **Acceptance criteria:**
  - [ ] AC1 — Given built images, when the job runs `docker compose up -d` with the CI profile
    (`VO_LLM_MODE=fake`, no Ollama pull), then all required services become healthy in
    ≤ 120 s.
  - [ ] AC2 — Given the running stack, when `infra/tests/smoke.sh` runs, then it verifies `/healthz`,
    `/api/health/ready`, security headers and WebSocket upgrade on `/ws`.
  - [ ] AC3 — Given a failure, then `docker compose logs` of all services is uploaded as an artifact.
- **Tasks:** CI profile/override `docker-compose.ci.yml`; job.
- **Tests:** the smoke script itself.
- **Done when:** job required.

### D03.4 — Quality reports

#### US-03.07 — Coverage enforcement and reports

- [ ] **US-03.07 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a tech lead, I want coverage thresholds enforced per area, so that Constitution
  §18.2 is real.
- **Acceptance criteria:**
  - [ ] AC1 — Backend: domain ≥ 95 %, application ≥ 90 %, others ≥ 70 % (separate `--cov` runs or
    coverage contexts); failing threshold fails the job.
  - [ ] AC2 — Frontend: `office-engine` ≥ 90 %, others ≥ 70 %.
  - [ ] AC3 — Reports (XML + summary) uploaded as artifacts.
- **Tasks:** coverage configs, job steps.
- **Tests:** temporary threshold breach in a test PR.
- **Done when:** enforced.

#### US-03.08 — Contract and palette checks

- [ ] **US-03.08 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a tech lead, I want the OpenAPI drift check and the OCS palette check wired now,
  so that later WPs only add content.
- **Acceptance criteria:**
  - [ ] AC1 — OpenAPI drift: CI exports `core`'s OpenAPI, regenerates `frontend/src/api/schema.d.ts`,
    and fails if `git diff` is non-empty.
  - [ ] AC2 — Palette check: `scripts/check_palette.py` validates every hex color in
    `frontend/src/ui-amiga/tokens.css` and every indexed PNG palette under
    `frontend/src/assets/` against the OCS 12-bit rule; fails on `#0056AA`-like values.
  - [ ] AC3 — Both checks pass on the skeleton (trivially) and fail on negative fixtures.
- **Tasks:** export script (`python -m virtual_office.api.export_openapi`), palette script with
  Pillow-free PNG palette parsing (stdlib `zlib`/`struct`), fixtures.
- **Tests:** pytest over fixtures.
- **Done when:** both jobs required.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WPNN closing: …`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All jobs required in branch protection (documented in `.github/BRANCH_PROTECTION.md`).
- [ ] Every action pinned by commit SHA; `no-latest` green.
- [ ] Full PR pipeline < 15 min on a warm cache.
- [ ] Nightly workflow runs the full matrix including Ollama model pull and evals placeholder.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Slow CI discourages small PRs | Parallel jobs, BuildKit and pnpm/uv caches, fake LLM in PRs |
| Multi-arch builds are slow | arm64 build only on `main` and nightly; PRs build amd64 |

## 7. Blockers

None.

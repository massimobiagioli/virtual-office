# WP02 — Containerized Platform

| Field        | Value |
| ------------ | ----- |
| Milestone    | M0 — Boot Disk |
| Status       | READY |
| Depends on   | WP01 |
| Enables      | WP03, WP04 |
| Constitution | Article XV (§15.1, §15.2, §15.11), Article XVII (§17.1–17.3) |
| Guides       | [DOCKER.md](../../.docs/DOCKER.md) · [POSTGRES.md](../../.docs/POSTGRES.md) §1–2 · [OLLAMA.md](../../.docs/OLLAMA.md) §1–2 · [STACK.md](../../.docs/STACK.md) §2 |
| Skills       | `delivering-features` |
| Estimate     | 31 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-02.01 — Python service images (5 pts)
- [ ] US-02.02 — Frontend image with nginx (3 pts)
- [ ] US-02.03 — Image hygiene checks (2 pts)
- [ ] US-02.04 — Base compose file (5 pts)
- [ ] US-02.05 — Dev overlay with live sync (3 pts)
- [ ] US-02.06 — GPU overlay (1 pts)
- [ ] US-02.07 — Postgres databases and roles (3 pts)
- [ ] US-02.08 — Ollama init with locked models (3 pts)
- [ ] US-02.09 — Health endpoints in Python services (3 pts)
- [ ] US-02.10 — One-command startup verification (3 pts)

## 1. Objective

Make the whole system run in containers with one command: five services plus one-off jobs,
secure defaults, health checks and a dev mode with live sync. At the end of this WP a person
with only Docker can start an (empty) Virtual Office.

## 2. Scope

**In:** Dockerfiles (runtime + dev targets), `docker-compose.yml`, `docker-compose.dev.yml`,
`docker-compose.gpu.yml`, Postgres init scripts (databases, roles, privileges), Ollama init with
`models.lock`, nginx config, health endpoints.

**Out:** database tables (WP04), CI (WP03), real application features.

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D02.1 | Dockerfiles | Multi-stage, non-root (UID 10001), digest-pinned Dockerfiles for `frontend`, `core`, `catalog`, each with `runtime` and `dev` targets | `docker build --target runtime` succeeds for all; `docker run … id -u` prints `10001`; images < 250 MB (Python) / < 60 MB (frontend) | US-02.01 – US-02.03 |
| D02.2 | Compose stack | Base, dev and GPU compose files following DOCKER.md §5 | `docker compose config` valid for each combination; only `frontend` publishes a port, bound to `127.0.0.1` | US-02.04 – US-02.06 |
| D02.3 | Data and model init | Postgres init (2 DBs, 4 roles, privileges) and `ollama-init` pulling locked models with digest verification | Fresh volume init creates DBs/roles; tampered digest makes `ollama-init` exit non-zero | US-02.07 – US-02.08 |
| D02.4 | Health | `/health/live`, `/health/ready` in both Python services; `/healthz` in nginx; all services healthy | `docker compose up --build -d && docker compose ps` shows all healthy in ≤ 120 s (models already pulled) | US-02.09 – US-02.10 |

## 4. User stories

### D02.1 — Dockerfiles

#### US-02.01 — Python service images

- [ ] **US-02.01 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As an operator, I want identical, minimal, non-root images for `core` and
  `catalog`, so that both services build and run the same way everywhere.
- **Acceptance criteria:**
  - [ ] AC1 — Given `services/<svc>/Dockerfile`, when built with context = repo root and target
    `runtime`, then it follows DOCKER.md §4.2 (stages, uv copy from pinned image, cache mounts,
    OCI labels, `USER 10001`).
  - [ ] AC2 — Given the runtime image, when inspected, then it contains no compiler, no `uv`, no tests
    and no dev dependencies.
  - [ ] AC3 — Given the `dev` target, when run, then uvicorn starts with `--reload` and dev dependencies
    (pytest, ruff, mypy) are available.
  - [ ] AC4 — Given both base images, when inspected, then they are referenced by exact tag + digest.
- **Tasks:** two Dockerfiles; one `.dockerignore` per service context (ADR-0004); OCI labels
  with `ARG VCS_REF`.
- **Tests:** CI build (WP03); container structure check script asserting user, absence of
  `uv`, entrypoint.
- **Done when:** both images build for amd64 and arm64.

#### US-02.02 — Frontend image with nginx

- [ ] **US-02.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As an operator, I want the SPA served by unprivileged nginx with a reverse proxy to
  `core`, so that the browser talks to a single origin.
- **Acceptance criteria:**
  - [ ] AC1 — Given `frontend/Dockerfile`, when built, then it follows DOCKER.md §4.3.
  - [ ] AC2 — Given `nginx.conf`, when the container runs, then `/healthz` returns 200, unknown paths
    return `index.html`, `/assets/*` have immutable cache headers, `index.html` has `no-cache`.
  - [ ] AC3 — Given requests to `/api/*` and `/ws`, when proxied, then they reach `core:8000`
    (WebSocket upgrade works, read timeout 3600 s for `/ws`).
  - [ ] AC4 — Given any response, when inspected, then security headers of DOCKER.md §4.3 are present
    and `server_tokens` is off.
- **Tasks:** Dockerfile, `nginx.conf`, header policy (CSP allowing self only, `connect-src`
  self + ws).
- **Tests:** compose smoke test with `curl -I` assertions (script in `infra/tests/`).
- **Done when:** headers and proxy verified in the stack.

#### US-02.03 — Image hygiene checks

- [ ] **US-02.03 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As a tech lead, I want automated checks on image size and user, so that image
  quality does not regress.
- **Acceptance criteria:**
  - [ ] AC1 — Given built images, when `infra/tests/check_images.sh` runs, then it fails if any image
    runs as root or exceeds the size budgets of D02.1.
  - [ ] AC2 — Given the script, when run in CI (WP03), then its output is attached to the job summary.
- **Tasks:** script using `docker image inspect`.
- **Tests:** run against built images.
- **Done when:** script merged and passing.

### D02.2 — Compose stack

#### US-02.04 — Base compose file

- [ ] **US-02.04 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As an operator, I want a production-like `docker-compose.yml` with all five services and
  jobs, so that `docker compose up` starts Virtual Office.
- **Acceptance criteria:**
  - [ ] AC1 — Given `docker-compose.yml`, when validated with `docker compose config`, then it declares
    services `frontend`, `core`, `catalog`, `ollama`, `postgres` and jobs
    `migrate-core`, `migrate-catalog`, `catalog-seed`, `ollama-init`, `rebuild-projections`
    (profile `admin`), `backup` (profile `backup`).
  - [ ] AC2 — Given every long-running service, when inspected, then it has a healthcheck, and every
    dependency uses `service_healthy` / `service_completed_successfully`.
  - [ ] AC3 — Given app services, when inspected, then `x-app-defaults` applies `read_only`, `tmpfs`,
    `cap_drop: [ALL]`, `no-new-privileges`, `init`, log rotation; exceptions are commented.
  - [ ] AC4 — Given ports, when inspected, then only `frontend` publishes `127.0.0.1:8080:8080`.
  - [ ] AC5 — Given required variables, when missing from `.env`, then `docker compose config` fails
    naming the variable (`${VAR:?}` syntax).
  - [ ] AC6 — Given the root `Makefile` created in US-01.01, when `make up`, `make status`,
    `make logs`, `make down` run against the hardened stack, then they still work unchanged.
  - [ ] AC7 — Given the compose file, when inspected, then every app image builds from its own
    subproject folder (`build.context: frontend | services/core | services/catalog`).
- **Tasks:** harden the compose file started in WP01; placeholder commands for jobs whose implementation arrives later
  (`migrate-*` runs `alembic upgrade head` on an empty history).
- **Tests:** `docker compose config` in CI; smoke test.
- **Done when:** stack starts (with dev overlay or prebuilt images).

#### US-02.05 — Dev overlay with live sync

- [ ] **US-02.05 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a developer, I want `docker-compose.dev.yml` with `develop.watch`, so that code changes
  appear in running containers without rebuilds.
- **Acceptance criteria:**
  - [ ] AC1 — Given `docker compose -f docker-compose.yml -f docker-compose.dev.yml watch`, when a file in
    `services/core/src` changes, then uvicorn reloads within 3 s.
  - [ ] AC2 — Given a change in `frontend/src`, when saved, then the Vite dev server hot-reloads.
  - [ ] AC3 — Given a change in `uv.lock` or `pnpm-lock.yaml`, when saved, then the affected image
    rebuilds.
  - [ ] AC4 — Given the dev overlay, when running, then Postgres is reachable on `127.0.0.1:5432` and
    Vite on `127.0.0.1:5173`; nothing binds to `0.0.0.0` on the host.
- **Tasks:** write overlay; Vite proxy config for `/api` and `/ws`.
- **Tests:** manual verification checklist recorded in the PR; CI validates config.
- **Done when:** live sync verified for both stacks.

#### US-02.06 — GPU overlay

- [ ] **US-02.06 completed** · **Points:** 1 · **Priority:** Could · **ADR:** —
- **Story:** As a user with an NVIDIA GPU, I want `docker-compose.gpu.yml`, so that Ollama uses my GPU.
- **Acceptance criteria:**
  - [ ] AC1 — Given the overlay, when combined with the base file, then `ollama` reserves all NVIDIA GPUs
    (DOCKER.md §5.4) and `docker compose config` is valid.
  - [ ] AC2 — Given a machine without GPU, when the base file alone is used, then nothing GPU-related is
    required.
- **Tasks:** write overlay.
- **Tests:** config validation.
- **Done when:** merged.

### D02.3 — Data and model init

#### US-02.07 — Postgres databases and roles

- [ ] **US-02.07 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As an operator, I want the Postgres container to create the databases and least-
  privilege roles on first start, so that services never use the superuser.
- **Acceptance criteria:**
  - [ ] AC1 — Given an empty `pgdata` volume, when `postgres` starts, then databases `core` and
    `catalog` and roles `core_owner`, `core_app`, `catalog_owner`, `catalog_app` exist with
    passwords from env.
  - [ ] AC2 — Given `core_app`, when it tries `CREATE TABLE`, then it is denied.
  - [ ] AC3 — Given `public` schema, when any app role tries to create objects in it, then it is denied.
  - [ ] AC4 — Given runtime roles, when inspected, then `statement_timeout=5s`, `lock_timeout=2s`.
  - [ ] AC5 — Given server settings of POSTGRES.md §1.1, when queried with `SHOW`, then they match.
- **Tasks:** `infra/postgres/initdb/01-roles-and-databases.sh` (idempotent, `set -euo pipefail`),
  `command:` settings in compose.
- **Tests:** integration test script running SQL assertions against the started container.
- **Done when:** assertions pass on a fresh volume.

#### US-02.08 — Ollama init with locked models

- [ ] **US-02.08 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As an operator, I want an `ollama-init` job that pulls exactly the locked models and
  verifies digests, so that every environment runs the same model bits.
- **Acceptance criteria:**
  - [ ] AC1 — Given `infra/ollama/models.lock` with tag + digest entries, when `ollama-init` runs, then
    every tag is pulled and its digest compared; on match it exits 0.
  - [ ] AC2 — Given a digest mismatch, when `ollama-init` runs, then it exits non-zero naming the tag.
  - [ ] AC3 — Given a tag without explicit size/variant or with `latest`, when the lock is parsed, then
    the job fails before pulling.
  - [ ] AC4 — Given `VO_LLM_MODE=fake`, when compose starts with the CI profile, then `core` does not
    depend on `ollama-init`.
- **Tasks:** lock file with the three default models of OLLAMA.md §2.2 (digests filled by
  running the job with `--lock` once, reviewed in PR); init script in the Ollama image.
- **Tests:** script unit tests (parser) + a CI job pulling only in the nightly workflow.
- **Done when:** lock committed, job verified locally.

### D02.4 — Health

#### US-02.09 — Health endpoints in Python services

- [ ] **US-02.09 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As an operator, I want liveness and readiness endpoints, so that compose and CI know
  when services are really ready.
- **Acceptance criteria:**
  - [ ] AC1 — Given `GET /health/live`, when the process is up, then it returns 200 `{"status":"ok"}`.
  - [ ] AC2 — Given `GET /health/ready` on `core`, when Postgres, catalog and (unless fake mode) Ollama
    are reachable, then 200 with per-dependency status; otherwise 503 with the failing ones.
  - [ ] AC3 — Given `catalog`, when Postgres is reachable, then ready is 200.
  - [ ] AC4 — Given readiness checks, when a dependency hangs, then the check times out in ≤ 2 s.
- **Tasks:** router `api/routers/health.py` in both services; dependency probes as ports.
- **Tests:** unit tests with fake probes; smoke test in compose.
- **Done when:** compose healthchecks use these endpoints.

#### US-02.10 — One-command startup verification

- [ ] **US-02.10 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want proof that a clean machine can start the system with
  one command, so that M0's promise is kept.
- **Acceptance criteria:**
  - [ ] AC1 — Given a clean clone and a filled `.env`, when `docker compose up --build -d` runs, then all
    long-running services are healthy in ≤ 120 s (models pre-pulled) and all jobs completed.
  - [ ] AC2 — Given the browser at `http://127.0.0.1:8080`, when opened, then the placeholder Workbench
    title renders and `/api/health/ready` (proxied) returns 200.
  - [ ] AC3 — Given `docker compose down` then `up`, when restarted, then data volumes persist.
- **Tasks:** `infra/tests/smoke.sh` used by CI (WP03); DOCKER.md §6 verified and corrected.
- **Tests:** smoke script.
- **Done when:** smoke script passes locally and in CI.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WPNN closing: …`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; DOCKER.md, POSTGRES.md, OLLAMA.md updated if reality differed.
- [ ] No floating tags anywhere; digests filled.
- [ ] Security defaults applied or justified per service.
- [ ] Smoke test passes from a clean clone.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Large model pulls make startup slow | Pulls happen once in `ollama-init` into a named volume; CI uses fake mode |
| Docker on macOS cannot use the GPU | Documented host-Ollama alternative (OLLAMA.md §6) |
| `read_only` breaks a dependency writing to disk | Add specific `tmpfs` mounts, documented in compose comments |

## 7. Blockers

None.

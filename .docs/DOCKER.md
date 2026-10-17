# Virtual Office — Docker Guide

| Field   | Value                                                                                  |
| ------- | -------------------------------------------------------------------------------------- |
| Scope   | Dockerfiles, Compose files, images, volumes, networks, one-off jobs, local workflow    |
| Related | [STACK.md](STACK.md) §2 · [PRINCIPLES.md](PRINCIPLES.md) §5 (Twelve-Factor) · [OLLAMA.md](OLLAMA.md) · [POSTGRES.md](POSTGRES.md) |

**Everything runs in containers.** The only host requirement is Docker. This guide fixes how
every image and compose entry is written so that all services look and behave the same.

---

## 1. Host requirements

| Tool            | Minimum version | Notes |
| --------------- | --------------- | ----- |
| Docker Engine   | 29.9.1          | Or Docker Desktop shipping this engine |
| Docker Compose  | v5.6.0          | Compose v2 plugin syntax (`docker compose`), Compose Specification |
| BuildKit        | default builder | Required for cache mounts and `--mount=type=secret` |
| GNU Make        | 3.81            | Only to run the root `Makefile` shortcuts (macOS ships 3.81); every target is a plain `docker compose` command that also works without `make` |

Versions verified on 2026-10-16 (see STACK.md policy). Older Engine/Compose releases are not
supported: upgrade before reporting a problem.

---

## 2. Files

```
docker-compose.yml                  # base: production-like, no bind mounts, only frontend published
docker-compose.dev.yml              # overlay: develop.watch, debug logging, Postgres port on 127.0.0.1
docker-compose.gpu.yml              # overlay: NVIDIA GPU reservation for ollama
.env.example                        # every variable, documented; copied to .env (git-ignored) locally
Makefile                            # entry point: `make` (help), up, down, logs, status
frontend/Dockerfile                 # build context: frontend/
services/core/Dockerfile            # build context: services/core/ (own pyproject.toml + uv.lock)
services/catalog/Dockerfile         # build context: services/catalog/
infra/postgres/initdb/              # init scripts: databases and roles (see POSTGRES.md)
infra/ollama/models.lock            # pinned model tags and digests (see OLLAMA.md)
```

Every build context has a `.dockerignore` that excludes at least: `.git`, `node_modules`,
`.venv`, `__pycache__`, `dist`, `coverage`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`,
`.env*` (except `.env.example`), `*.log`, `.docs`, `.agents`.

---

## 3. Image tags — the rules

1. **Base images**: full version tag **and** digest:
   `FROM python:3.15.0-slim-trixie@sha256:<digest>`.
2. **Never** `latest`, never major-only or floating tags (`python:3`, `node:24`, `postgres:18`,
   `nginx:mainline`, `ollama/ollama:latest`). CI `no-latest` check enforces it.
3. **Our images** are tagged `virtual-office/<service>:<git-sha>`; in compose the tag comes from
   `${VO_IMAGE_TAG:?}` (set by CI or the dev script to the current commit).
4. Digests are bumped only by Renovate PRs, which run the full pipeline.
5. Images are built for `linux/amd64` and `linux/arm64`.

---

## 4. Dockerfile standards

### 4.1 Common rules (every Dockerfile)

- First line: `# syntax=docker/dockerfile:<pinned version>@sha256:<digest>` (exact version from
  STACK.md §2.3 plus digest, never `1`).
- **Multi-stage**: `base` → `deps` → `build` → `runtime` (and `dev` target for the dev overlay).
- **Non-root**: create a dedicated user with fixed UID/GID `10001:10001`; `USER 10001` in
  runtime stages.
- `WORKDIR /app`; no `ADD` (use `COPY`); `COPY --chown=10001:10001` for app files.
- Copy dependency manifests first, install, then copy sources (layer caching).
- BuildKit cache mounts for package caches (`--mount=type=cache,target=…`).
- No secrets in layers: build-time secrets only via `--mount=type=secret`.
- OCI labels: `org.opencontainers.image.title`, `.source`, `.revision` (`ARG VCS_REF`),
  `.version`, `.licenses`.
- `HEALTHCHECK` defined in compose (not in Dockerfile) so all checks live in one place.
- `EXPOSE` the service port; `ENTRYPOINT` in exec form; one process per container.
- `STOPSIGNAL SIGTERM` (default) and the app handles graceful shutdown (twelve-factor IX).

### 4.2 Python services (`core`, `catalog`)

```dockerfile
# syntax=docker/dockerfile:<pinned>
ARG PYTHON_IMAGE=python:3.15.0-slim-trixie@sha256:<digest>
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.13.1@sha256:<digest>

FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --no-create-home app
WORKDIR /app

FROM base AS deps
COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

FROM deps AS build
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM base AS runtime
COPY --from=build --chown=10001:10001 /app /app
ENV PATH="/app/.venv/bin:${PATH}"
USER 10001
EXPOSE 8000
ENTRYPOINT ["uvicorn", "virtual_office.main:create_app", "--factory", "--host", "0.0.0.0", \
            "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*", "--no-server-header"]

FROM build AS dev
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen
COPY --from=uv /uv /usr/local/bin/uv
# UID 10001 has no home directory: uv needs a writable cache.
ENV UV_CACHE_DIR=/tmp/uv-cache
USER 10001
ENTRYPOINT ["uvicorn", "virtual_office.main:create_app", "--factory", "--host", "0.0.0.0", \
            "--port", "8000", "--reload"]
```

- The build context is the **service folder** (`services/core/`, `services/catalog/`):
  each service is an independent uv project with its own `pyproject.toml` and `uv.lock`, and
  no Python manifest exists at the repository root
  ([ADR-0004](adr/0004-per-service-python-projects.md)).
- uvicorn starts the app through the `create_app` **factory** (`--factory`): settings are read
  from the environment when the server starts, never at import time (BACKEND.md §4.3).
- Same image runs the one-off jobs (`alembic upgrade head`, `rebuild-projections`, seeds) by
  overriding `command`.

### 4.3 Frontend

```dockerfile
# syntax=docker/dockerfile:<pinned>
ARG NODE_IMAGE=node:24.22.0-trixie-slim@sha256:<digest>
ARG NGINX_IMAGE=nginxinc/nginx-unprivileged:1.31.7-alpine3.24@sha256:<digest>

FROM ${NODE_IMAGE} AS base
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 COREPACK_HOME=/opt/corepack
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --no-create-home app
WORKDIR /app
RUN corepack enable

FROM base AS deps
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
RUN corepack install && chmod -R a+rX /opt/corepack
RUN --mount=type=cache,target=/pnpm-store pnpm install --frozen-lockfile --store-dir /pnpm-store

FROM deps AS build
COPY . ./
ARG VITE_APP_VERSION
RUN pnpm build

FROM ${NGINX_IMAGE} AS runtime
USER root
RUN addgroup -g 10001 -S app && adduser -u 10001 -G app -S -D -H app \
    && chown -R 10001:10001 /var/cache/nginx
# Root-owned, read-only for the runtime user: only the nginx cache is writable.
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY security-headers.conf /etc/nginx/security-headers.conf
COPY --from=build /app/dist /usr/share/nginx/html
USER 10001
EXPOSE 8080

FROM deps AS dev
# UID 10001 has no home directory: pnpm and corepack need a writable HOME.
ENV HOME=/tmp
COPY --chown=10001:10001 . ./
# The 0600 pnpm state file must be readable by UID 10001, or `verifyDepsBeforeRun` fails.
RUN chown 10001:10001 /app /app/node_modules /app/node_modules/.pnpm-workspace-state-v1.json
USER 10001
EXPOSE 5173
ENTRYPOINT ["pnpm", "dev", "--host", "0.0.0.0"]
```

`nginx.conf` rules: `location = /healthz` returns `200` (used by the healthcheck); SPA fallback
to `index.html`; `location /api/` and `location = /ws` proxied
to `http://core:8000`, both forwarding `X-Forwarded-For`/`X-Forwarded-Proto` (WebSocket upgrade
headers, `proxy_read_timeout 3600s` for `/ws`); `location = /favicon.ico` returns `404` until a
favicon exists in `public/`;
`Cache-Control: public, max-age=31536000, immutable` for `/assets/`; `no-cache` for
`index.html`; security headers (`Content-Security-Policy`, `X-Content-Type-Options`,
`Referrer-Policy`, `Permissions-Policy`, kept in `security-headers.conf` and included by every
location that sets its own `add_header`); `server_tokens off`; JSON access log to stdout.

---

## 5. Compose standards

### 5.1 Skeleton (`docker-compose.yml`)

```yaml
name: virtual-office

x-app-defaults: &app-defaults
  restart: unless-stopped
  init: true
  read_only: true
  tmpfs: ["/tmp"]
  security_opt: ["no-new-privileges:true"]
  cap_drop: ["ALL"]
  networks: [office]
  logging:
    driver: json-file
    options: { max-size: "10m", max-file: "3" }

services:
  frontend:
    <<: *app-defaults
    image: virtual-office/frontend:${VO_IMAGE_TAG:?}
    build: { context: frontend, target: runtime }
    ports: ["127.0.0.1:8080:8080"]
    depends_on:
      core: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:8080/healthz"]
      interval: 10s
      timeout: 3s
      retries: 5
      start_period: 5s

  core:
    <<: *app-defaults
    image: virtual-office/core:${VO_IMAGE_TAG:?}
    build: { context: services/core, target: runtime }
    env_file: [.env]
    environment:
      VO_DATABASE_URL: postgresql+asyncpg://core_app:${VO_CORE_DB_PASSWORD:?}@postgres:5432/core
      VO_CATALOG_URL: http://catalog:8001/
      VO_OLLAMA_BASE_URL: ${VO_OLLAMA_BASE_URL:-http://ollama:11434/}
    depends_on:
      postgres: { condition: service_healthy }
      migrate-core: { condition: service_completed_successfully }
      catalog: { condition: service_healthy }
      ollama-init: { condition: service_completed_successfully }
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request,sys; sys.exit(urllib.request.urlopen('http://127.0.0.1:8000/health/ready').status!=200)"]
      interval: 10s
      timeout: 5s
      retries: 6
      start_period: 15s
    deploy:
      resources:
        limits: { cpus: "2", memory: 1g }

  # catalog, ollama, ollama-init, postgres, migrate-core, migrate-catalog, catalog-seed …

networks:
  office: {}

volumes:
  pgdata: {}
  ollama-models: {}
```

### 5.2 Rules

1. Top-level `name: virtual-office`; **no** `version:` key.
2. Service names are exactly: `frontend`, `core`, `catalog`, `ollama`, `postgres`, plus
   one-off jobs `migrate-core`, `migrate-catalog`, `catalog-seed`, `ollama-init`,
   `rebuild-projections` (profile `admin`), `backup` (profile `backup`).
3. Shared defaults through the `x-app-defaults` anchor; services may relax `read_only` /
   `cap_drop` only with a comment explaining why (e.g. `postgres`, `ollama` need writable
   data dirs, mounted as volumes).
4. **Only `frontend` publishes a port**, always bound to `127.0.0.1`. The dev overlay may
   additionally publish `postgres` and `core` on `127.0.0.1`.
5. Every long-running service has a `healthcheck`; every dependency uses
   `condition: service_healthy` or `service_completed_successfully`.
6. Configuration via environment only (twelve-factor III). Required variables use
   `${VAR:?}` so compose fails fast when missing. No secrets in compose files.
7. Named volumes only in the base file; bind mounts only in `docker-compose.dev.yml`.
8. Resource limits for `frontend`, `core`, `catalog`; `ollama` limits are documented in
   OLLAMA.md.
9. Logs go to stdout/stderr; rotation via the `json-file` options above.
10. One internal network `office`; containers address each other by service name.

### 5.3 Dev overlay (`docker-compose.dev.yml`)

- Builds the `dev` targets; uses `develop.watch`:
  - `sync` source folders (`frontend/src`, `services/*/src`) into containers;
  - `rebuild` on lockfile or manifest changes (`pnpm-lock.yaml`, `uv.lock`, `pyproject.toml`).
- `VO_ENV=dev`, `VO_LOG_LEVEL=DEBUG`, API docs enabled.
- Vite dev server on `127.0.0.1:5173` proxying `/api` and `/ws` to `core`.

### 5.4 GPU overlay (`docker-compose.gpu.yml`)

Adds to `ollama`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

---

## 6. Everyday workflow

All commands run from the repository root. They are documented here (not in AGENTS.md).

The root `Makefile` is the everyday entry point. It is a thin wrapper over `docker compose`
(no logic of its own, no host tools besides Docker and `make`); `make` alone prints the help.

| Target        | Runs |
| ------------- | ---- |
| `make` / `make help` | Lists the targets with a one-line description (default goal) |
| `make up`     | `docker compose up --build -d` |
| `make down`   | `docker compose down` |
| `make logs`   | `docker compose logs -f` (`make logs s=core` for one service) |
| `make status` | `docker compose ps` |

Raw commands, for everything the Makefile does not wrap:

| Goal                                 | Command |
| ------------------------------------ | ------- |
| First setup                          | `cp .env.example .env` then fill the required values |
| Start everything (prod-like)         | `docker compose up --build -d` |
| Start dev mode with live sync        | `docker compose -f docker-compose.yml -f docker-compose.dev.yml watch` |
| Start with NVIDIA GPU                | `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d` |
| Follow logs of one service           | `docker compose logs -f core` |
| Backend tests                        | `docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm core pytest` |
| Backend lint and types               | `docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm core sh -c "ruff check && ruff format --check && mypy && lint-imports"` |
| Frontend tests and checks            | `docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm frontend sh -c "pnpm lint && pnpm typecheck && pnpm test"` |
| Frontend checks until the dev overlay exists (WP02) | `docker build --target dev -t vo-frontend-dev frontend && docker run --rm --entrypoint sh vo-frontend-dev -c "pnpm typecheck && pnpm test && pnpm build"` |
| Run migrations manually              | `docker compose run --rm migrate-core` |
| Rebuild projections                  | `docker compose --profile admin run --rm rebuild-projections` |
| Backup database                      | `docker compose --profile backup run --rm backup` |
| Stop                                 | `docker compose down` |
| Reset everything (deletes data!)     | `docker compose down --volumes` |

Integration tests that use testcontainers need access to the Docker socket; they run in CI
and locally through the dedicated `core` dev container with `/var/run/docker.sock` mounted
read-only (dev overlay only).

---

## 7. CI usage

- Build with `docker buildx bake` (targets mirror compose services), push nothing in v1.
- Pipeline order (STACK.md §8): build → unit tests in images → `docker compose up` with
  `VO_LLM_MODE=fake` → health gate → Playwright → Trivy scan of every image (fail on fixable
  HIGH/CRITICAL).
- `no-latest` check scans Dockerfiles, compose files and workflows.

---

## 8. Review checklist (Docker)

```
- [ ] Base images: exact tag + digest; no latest/floating tags
- [ ] Multi-stage; non-root UID 10001; no secrets in layers; .dockerignore present
- [ ] Healthcheck + depends_on conditions for every new service
- [ ] Only frontend published (127.0.0.1); named volumes in base file
- [ ] Env-only configuration; .env.example updated; required vars use ${VAR:?}
- [ ] Security defaults kept (read_only, cap_drop, no-new-privileges) or justified
- [ ] `docker compose up --build` from a clean clone is healthy
- [ ] Build context is the subproject folder; no Python/Node manifest at the repository root
- [ ] New everyday commands added to the `Makefile` help only if they wrap `docker compose`
```

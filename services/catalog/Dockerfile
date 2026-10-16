# syntax=docker/dockerfile:1.28.0@sha256:bb22d9815c728170f72750f4e5b0d672e06176142e1d602c7e66c050100b7e5b
# Image of the catalog service. Build context: services/catalog (ADR-0004);
# standards: DOCKER.md §4.
ARG PYTHON_IMAGE=python:3.15.0-slim-trixie@sha256:f48fda6d59b2b3437781d1c3ccf4aa0e26ae871de3cdd758b49ab45ee7291619
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.13.1@sha256:4a1f3666816dafadd20ceb71eac9a7d56d7ef30279f7d64048519ab901ada336

FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS base
ARG VCS_REF=unknown
LABEL org.opencontainers.image.title="virtual-office-catalog" \
      org.opencontainers.image.source="https://github.com/massimobiagioli/virtual-office" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.licenses="UNLICENSED"
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
    uv sync --frozen --no-dev --no-editable

FROM base AS runtime
COPY --from=build --chown=10001:10001 /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:${PATH}"
USER 10001
EXPOSE 8001
ENTRYPOINT ["uvicorn", "catalog.main:create_app", "--factory", "--host", "0.0.0.0", \
            "--port", "8001", "--proxy-headers", "--forwarded-allow-ips", "*", "--no-server-header"]

# Toolchain image: dev group installed, sources editable; runs tests, linters and the dev server.
FROM build AS dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen && chown -R 10001:10001 /app
# UID 10001 has no home directory: uv needs a writable cache for `uv sync`/`uv lock --check`.
ENV PATH="/app/.venv/bin:${PATH}" UV_CACHE_DIR=/tmp/uv-cache
USER 10001
EXPOSE 8001
ENTRYPOINT ["uvicorn", "catalog.main:create_app", "--factory", "--host", "0.0.0.0", \
            "--port", "8001", "--reload"]

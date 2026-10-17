# syntax=docker/dockerfile:1.28.0@sha256:bb22d9815c728170f72750f4e5b0d672e06176142e1d602c7e66c050100b7e5b
# Image of the frontend service. Build context: frontend (ADR-0004); standards: DOCKER.md §4.
ARG NODE_IMAGE=node:24.22.0-trixie-slim@sha256:7f486cabe892bff8fef04c0f7da8dba84a560be3e4e2740b7a86afc57ebec315
ARG NGINX_IMAGE=nginxinc/nginx-unprivileged:1.31.7-alpine3.24@sha256:378d0c32f6562f7fd9629170797f57d2b953aa09be983b3daaf4809bb039ca00

FROM ${NODE_IMAGE} AS deps
# Corepack installs the pnpm version pinned by `packageManager` without asking, into a
# shared folder so that the non-root dev stage can run it too.
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 COREPACK_HOME=/opt/corepack
WORKDIR /app
RUN corepack enable
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
RUN corepack install && chmod -R a+rX /opt/corepack
RUN --mount=type=cache,target=/pnpm-store \
    pnpm install --frozen-lockfile --store-dir /pnpm-store

FROM deps AS build
COPY . ./
ARG VITE_APP_VERSION
RUN pnpm build

FROM ${NGINX_IMAGE} AS runtime
ARG VCS_REF=unknown
LABEL org.opencontainers.image.title="virtual-office-frontend" \
      org.opencontainers.image.source="https://github.com/massimobiagioli/virtual-office" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.licenses="UNLICENSED"
# Dedicated non-root user 10001 (DOCKER.md §4.1) instead of the image's nginx user 101.
USER root
RUN addgroup -g 10001 -S app && adduser -u 10001 -G app -S -D -H app \
    && chown -R 10001:10001 /var/cache/nginx
COPY --chown=10001:10001 nginx.conf /etc/nginx/conf.d/default.conf
COPY --chown=10001:10001 security-headers.conf /etc/nginx/security-headers.conf
COPY --from=build --chown=10001:10001 /app/dist /usr/share/nginx/html
USER 10001
EXPOSE 8080

# Toolchain image: dependencies installed, sources copied; runs tests, type-check and Vite dev.
FROM deps AS dev
COPY . ./
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --no-create-home app \
    && chown -R 10001:10001 /app
USER 10001
EXPOSE 5173
ENTRYPOINT ["pnpm", "dev", "--host", "0.0.0.0"]

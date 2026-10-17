# ADR-0010: US-01.05: Frontend scaffold with pnpm-enforced exact pins, a stdlib pin check and a least-privilege nginx image

- Status: Proposed
- Date: 2026-10-17
- Deciders: Project owner
- Related: Constitution §14.10, §15.2, §18.2; [STACK.md](../STACK.md) §1.4, §3;
  [FRONTEND.md](../FRONTEND.md) §1, §3, §6; [DOCKER.md](../DOCKER.md) §4.1, §4.3, §5.2;
  [DESIGN.md](../DESIGN.md); [ADR-0004](0004-per-service-python-projects.md),
  [ADR-0005](0005-us-01-01-root-compose-and-makefile-first.md),
  [ADR-0006](0006-us-01-02-core-settings-and-app-factory.md),
  [ADR-0008](0008-us-01-03-catalog-mirrors-core-with-minimal-settings.md),
  [ADR-0009](0009-us-01-04-quality-gates-as-tool-config-and-stdlib-scripts.md); US-01.05

## Context

US-01.05 creates `frontend/`: a Vue + Vite + TypeScript app with the FRONTEND.md §1 layout,
exact pins from STACK.md §3, a placeholder "My Workbench" title, and a pinned two-stage image
(pnpm build, nginx runtime) served by compose on `127.0.0.1:8080`. Several forces shaped it:

1. AC2 asks for `.npmrc` with `save-exact=true` and `engine-strict=true`, but pnpm 12 ignores
   both keys in `.npmrc`; it reads its own settings from `pnpm-workspace.yaml`.
2. Exact pins were only checked by inspection; `scripts/check_python_pins.py` covers Python only.
3. CI (WP03) and compose healthchecks (WP02) do not exist yet, so the built image can only be
   verified by hand (AC3, AC4).
4. Design tokens arrive in WP07 and the Workbench screen in WP08; the placeholder must not
   anticipate them.
5. nginx refuses to start when a `proxy_pass` host does not resolve, and the hardened network,
   healthchecks and required image tag arrive in WP02.
6. Images run as UID 10001 with least privilege (DOCKER.md §4.1); the dev user has no home,
   which breaks corepack and pnpm state (the same class of issue as ADR-0008 `UV_CACHE_DIR`).

## Decision

We will:

1. **Enforce exact pins with pnpm's own settings.** `frontend/pnpm-workspace.yaml` sets
   `saveExact: true` and `engineStrict: true`; `frontend/.npmrc` keeps `save-exact=true` and
   `engine-strict=true` as AC2 requires and for npm-based tools. Both files say to keep them in
   sync; STACK.md §1.4 names both.
2. **Check frontend pins with a stdlib script**, `scripts/check_frontend_pins.py` (run with
   `python -I`, tests in `scripts/tests`, same pattern as ADR-0009): every dependency of
   `frontend/package.json` must be an exact version equal to its STACK.md §3 row, and
   `packageManager`/`engines` must match the Node.js and pnpm rows.
3. **Add no `@` path alias yet.** `vite.config.ts` resolving `@` needs `node:path`/`node:url`
   and therefore `@types/node`, a dependency not in STACK.md; relative imports are enough for
   the skeleton. US-01.06 (strict TS/ESLint) may add it with its dependency.
4. **Inject the router history.** `createWorkbenchRouter(history: RouterHistory =
   createWebHistory())`; specs pass `createMemoryHistory()`. No test switch in production code.
5. **Keep a root-route placeholder SFC**, `src/windows/WorkbenchDesktop.vue`, rendered through
   `<RouterView/>` in `App.vue`, until WP08 reshapes or moves it (FRONTEND.md §1 shows it).
6. **Use browser defaults in the placeholder `App.vue`**: no DESIGN.md tokens, colors or fonts
   until the WP07 tokens exist; a comment in `App.vue` says so.
7. **Proxy `/api/` and `= /ws` to `core:8000` in nginx now**, forwarding `Host`,
   `X-Forwarded-For` and `X-Forwarded-Proto`, with `depends_on: [core]` in compose because nginx
   needs a resolvable upstream at start-up. `location = /ws` (exact match) avoids catching
   `/wsfoo`. WP02 replaces the plain `depends_on` with a health condition.
8. **Answer `404` on `/favicon.ico`** instead of the SPA fallback's HTML, until the WP12 asset
   pipeline adds a favicon in `public/`.
9. **Use the temporary `${VO_IMAGE_TAG:-dev}` image tag default**, as ADR-0006 does for `core`;
   WP02 makes it required.
10. **Least-privilege runtime image**: a dedicated UID/GID 10001 replaces nginx's user 101;
    `nginx.conf`, `security-headers.conf` and `dist/` are copied root-owned (0644), and only
    `/var/cache/nginx` is writable by UID 10001.
11. **Dev toolchain stage as UID 10001**: `base → deps → build → runtime` plus `dev`;
    `COREPACK_HOME=/opt/corepack` (shared, readable) so the non-root user can run the pinned
    pnpm; `HOME=/tmp` in `dev` for pnpm and corepack state; sources copied with
    `COPY --chown=10001:10001`; a non-recursive chown of `/app`, `/app/node_modules` and
    `node_modules/.pnpm-workspace-state-v1.json` (written 0600 by root, otherwise unreadable, so
    `verifyDepsBeforeRun` assumes stale deps and attempts a reinstall).
12. **Verify AC3 and AC4 by hand for this story**: `pnpm build` in the dev image (hashed
    `dist/assets/index-<hash>.js`) and `make up` plus a curl smoke on `http://127.0.0.1:8080/`
    (title, deep link, `/healthz`, favicon 404, immutable assets, security headers, UID 10001).
    WP02 (compose healthchecks) and WP03 (CI smoke) automate these checks.

## Alternatives Considered

1. **Only `.npmrc` for exact pins** — matches AC2 literally, but pnpm 12 silently ignores the
   keys, so `pnpm add` would write `^` ranges; rejected. **Only `pnpm-workspace.yaml`** — one
   source, but breaks AC2 and leaves npm-based tools without the rule; rejected.
2. **Defer the frontend pin check to US-01.09/US-01.10** — less code now, but AC2 would rest on
   inspection for several stories while `^` ranges can slip in; a Node-based checker would need
   its own dependencies, whereas the stdlib script reuses the ADR-0009 pattern.
3. **Add the `@` alias with `@types/node`** — the FRONTEND.md convention from day one, but adds
   an unlisted dependency to a skeleton that has no deep imports yet.
4. **No proxy and no `depends_on` until WP02** — a frontend that starts alone, but WP02 would
   have to change nginx config shipped and smoke-tested here; a resolvable upstream costs one
   compose line.
5. **Keep the image's nginx user 101 and a `chown -R` of config and web root** — simpler
   Dockerfile, but the runtime could rewrite its own config and content (DOCKER.md §4.1) and a
   recursive chown duplicates layers.
6. **Recursive `chown -R /app` in the dev stage** — no ownership surprises, but it duplicates
   `node_modules` in a second layer; the targeted chown keeps the layer at a few hundred bytes.

## Consequences

- Positive: `pnpm add` writes exact versions and engine mismatches fail; a `^` range or drift
  from STACK.md fails `check_frontend_pins.py`; the runtime cannot modify its config or
  content; dev gates run as non-root without pnpm errors; deep links, `/ws` and `/api/` behave
  as they will in WP06.
- Negative: two files carry the same pnpm rules and must stay in sync; AC3/AC4 have no
  automated test until WP02/WP03; the stack cannot start the frontend without `core`; the
  placeholder looks like a plain browser page until WP07; imports are relative until an alias
  arrives; the dev Dockerfile depends on a pnpm-internal state file name, which a pnpm upgrade
  may change.
- Risks and mitigations: a pnpm upgrade renaming the state file would bring back the reinstall
  error → the `pnpm typecheck && pnpm test && pnpm build` run as UID 10001 shows `ERR_PNPM`
  output and the review checks it; the STACK.md table format could hide a row from the parser →
  the script fails explicitly when the Node.js or pnpm row is missing (tested).

## Compliance

- `python -I scripts/check_frontend_pins.py` exits 0 on `main`; `pytest scripts/tests` covers
  every failure path (range, drift, missing rows, `packageManager`/`engines`).
- `frontend/src/App.spec.ts` asserts the "My Workbench" title and the `WorkbenchDesktop` route;
  `frontend/src/router.spec.ts` injects a memory history.
- In the `dev` image as UID 10001, `pnpm typecheck && pnpm test && pnpm build` exit 0 with no
  `ERR_PNPM` lines and produce hashed assets.
- `make up` + curl smoke as in Decision 12; WP02 adds compose healthchecks and WP03 a CI smoke
  that must cover the same checks.
- Review checklist: `nginx.conf` and `dist/` root-owned in the runtime image, only
  `/var/cache/nginx` writable; no DESIGN.md token in `App.vue` before WP07.

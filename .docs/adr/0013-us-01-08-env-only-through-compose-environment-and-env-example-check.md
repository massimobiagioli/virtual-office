# ADR-0013: US-01.08: Services get only their compose `environment:`, `.env.example` is checked by a stdlib script, root dotfiles allowed

- Status: Proposed
- Date: 2026-10-17
- Deciders: Project owner
- Related: Constitution §15.2, §15.11, §18.2; [DOCKER.md](../DOCKER.md) §2, §5.1, §5.2;
  [BACKEND.md](../BACKEND.md) §11.1; [FRONTEND.md](../FRONTEND.md) §11;
  [ADR-0004](0004-per-service-python-projects.md) (§3, root layout),
  [ADR-0006](0006-us-01-02-core-settings-and-app-factory.md) (extends its temporary compose
  defaults), [ADR-0009](0009-us-01-04-quality-gates-as-tool-config-and-stdlib-scripts.md)
  (pattern of the new check); US-01.08, US-01.09; review findings R1, R2, R4, R6, R8, R16, R17
  (`.project/execution/wp01-repository-and-toolchain.review.md`)

## Context

US-01.08 adds `.editorconfig`, `.gitignore` coverage and a documented `.env.example`. The forces:

1. Constitution §15.11: all configuration is a `VO_`-prefixed environment variable documented in
   `.env.example`. A list that nobody checks drifts as soon as a story adds a `Settings` field or
   a compose interpolation (ADR-0009: a rule nobody has seen fail is not a rule).
2. DOCKER.md said two things: §2 that services receive only their `environment:` keys, the §5.1
   skeleton that `core` gets `env_file: [.env]` (R1). With `env_file`, every `.env` line reaches
   every container, so the `.env.example` text about what each value does would be wrong, and the
   WP02 secrets plan (`${VO_*_PASSWORD:?}` interpolation) would be bypassed.
3. AC3 asks that `.env.example` "passes the `no-latest` check", which arrives in US-01.09 (R2).
4. `docker-compose.yml` already passed `VO_OLLAMA_BASE_URL` with a `:-` default (ADR-0006
   temporary defaults); `VO_LOG_LEVEL` is read by both services' `Settings` but was not passed, so
   it could not be changed in the stack (R6).
5. Constitution §15.2 and ADR-0004 §3 list only orchestration files at the repository root
   (`docker-compose*.yml`, `Makefile`, `.env.example`); `.gitignore` and `.editorconfig` are
   repository-wide and must live there to apply to every subproject (R8).
6. Each subproject is its own build context (ADR-0004): the frontend image never sees the root
   `.editorconfig`, so Prettier there falls back to its own defaults (R16).
7. The dev images contain no `git` (R17).

## Decision

We will:

1. **Pass configuration to services only through compose `environment:`** — no `env_file:`
   anywhere. The root `.env` (copied from `.env.example`, git-ignored) only fills `${…}` and
   `$NAME` interpolations of the compose files. The DOCKER.md §5.1 skeleton is aligned (no
   `env_file`, variables listed per service) and §2 states the rule. This is consistent with
   Constitution §15.11, DOCKER.md §5.2 rule 6 and the WP02 secrets plan (`${VO_*_PASSWORD:?}`).
2. **Write `.env.example` in two forms**: a variable compose interpolates as `NAME=value`; a
   per-service value compose fixes itself as a commented reference entry `# VO_NAME=value`. Every
   entry has comment text directly above it. **Only the variables read today are listed**; each
   future variable is added by the story that starts reading it.
3. **Add the stdlib check `scripts/check_env_example.py`** (ADR-0009 pattern: stdlib only,
   `python -I`, `--root`, `main(argv)`, `file:line` messages, a real-repository test plus failing
   fixtures in `scripts/tests/test_check_env_example.py`). It enforces that:
   - every field of every `services/*/src/*/settings.py` `Settings` class is listed, named by the
     module's `ENV_PREFIX` plus the field name or by a string `validation_alias`/`alias` (in that
     precedence); a non-string alias (e.g. `AliasChoices`) fails as unresolvable; `model_config`
     and `ClassVar`s are not fields;
   - every `VO_*` or `Settings` name and every `${NAME}`/`$NAME` interpolation (`$$` escapes) in
     the root `docker-compose*.yml` files is listed;
   - each entry has comment text above it (not a bare `#` or a ruler), and the comment is not
     carried across a blank line or reused by the next entry;
   - interpolated variables use `NAME=value`, compose-fixed ones `# VO_NAME=value`;
   - a `Settings` variable no compose file passes fails in either form (the services never read
     `.env`);
   - an entry nothing reads fails, and no variable is listed twice.
   Known limitation: compose files are read line by line, not parsed as YAML, so a ` #` inside a
   quoted or block scalar is taken as a comment and a variable after it is missed; we keep ` #`
   out of compose values (documented in the script docstring). ROADMAP D01.3 lists the check and
   its evidence; BACKEND.md §11.1 and DOCKER.md §2 document it.
4. **Pass `VO_LOG_LEVEL: ${VO_LOG_LEVEL:-INFO}` to `core` and `catalog`**, as an extension of
   ADR-0006's temporary compose defaults: an optional variable gets a `:-` default; WP02 decides
   which variables become required (`:?`). The DOCKER.md §5.1 skeleton shows it.
5. **Cover AC3's `no-latest` part with a stand-in test until US-01.09**:
   `test_the_repository_env_example_never_names_a_floating_tag` asserts that `.env.example` does
   not contain `latest`. US-01.09's tasks were refined so the real check scans `.env.example` and
   replaces the stand-in.
6. **Allow repository-wide dotfiles at the root** — `.gitignore` and `.editorconfig` — alongside
   the orchestration files of Constitution §15.2 / ADR-0004 §3. They are not ecosystem manifests
   (no dependencies, no build context) and cannot work from a subproject folder. Ecosystem
   manifests, lockfiles and Dockerfiles stay forbidden at the root.
7. **Choose these `.editorconfig` settings**: UTF-8, LF, final newline, trimmed trailing
   whitespace, 2 spaces by default (TS, Vue, JS, JSON, YAML, HTML, CSS, nginx); 4 spaces for
   Python, TOML, `uv.lock` (`[{*.{py,pyi,toml},uv.lock}]`) and `Dockerfile` continuation lines;
   tabs for the `Makefile`; `max_line_length = 100` (ruff `line-length` and Prettier `printWidth`),
   `off` for Markdown, where trailing whitespace is also kept.
8. **Set Prettier's `tabWidth: 2` and `endOfLine: "lf"` explicitly** in
   `frontend/.prettierrc.json`, because the root `.editorconfig` is outside the frontend build
   context and Prettier in the image would otherwise rely on its defaults (FRONTEND.md §11).
9. **Keep AC1/AC2 without an automated test** (R17, won't fix): a `git check-ignore` test cannot
   run in the dockerized gate because the dev images have no `git`. AC2 keeps the manual
   `git check-ignore` evidence of the review; `.editorconfig` conformance is a review item.

## Alternatives Considered

1. **`env_file: [.env]` per service** (the old DOCKER.md skeleton) — one place for all values,
   less compose text; but every container gets every variable, secrets leak to services that do
   not need them, `${VO_*:?}` stops guarding required values, and `.env.example` cannot say what
   reaches whom. Rejected.
2. **No check, `.env.example` maintained by review only** — no new script; but drift is silent
   and review findings showed how easy it is to miss a field or an alias. Rejected. **A check
   based on a YAML parser or on importing `Settings`** — exact parsing, but needs third-party
   packages or the service environments, against ADR-0009's stdlib, `python -I` pattern.
   Rejected; the line-based limitation is documented instead.
3. **List future variables now** (e.g. database passwords, LLM mode) — a fuller reference; but
   entries nothing reads mislead and cannot be checked. Rejected.
4. **Leave `VO_LOG_LEVEL` unpassed** — no compose change; but the log level could not be changed
   in the stack, and the check would fail it as "not passed by compose". **Make it required
   (`:?`)** — breaks a clean clone without `.env`. Both rejected.
5. **Tick AC3 only after US-01.09** — strictly honest, but blocks a finished story on the next
   one; the stand-in plus the US-01.09 refinement keeps the gap visible and closed. Rejected.
6. **Move `.editorconfig` into each subproject** — no root exception; but four copies drift and
   root files (compose, Makefile, docs) would be uncovered. Rejected.

## Consequences

- Positive: what each service receives is visible in `docker-compose.yml`; `.env.example` is
  machine-checked on every gate run and fails the moment a story adds an undocumented variable;
  the log level is configurable; every editor and the frontend image format files the same way.
- Negative: every variable a service needs must be written under its `environment:` key (more
  compose text); a new repository script to maintain; the `no-latest` part of AC3 rests on a
  substring test until US-01.09; the root exception for dotfiles is one more rule to remember.
- Risks and mitigations: the line-based compose reading can miss a variable after ` #` in a
  scalar — documented, and review keeps ` #` out of compose values; a new `Settings` style (e.g.
  `AliasChoices`) fails loudly instead of passing; the stand-in test is replaced by the real
  `no-latest` check in US-01.09; WP02 revisits which `:-` defaults become `:?`.

## Compliance

- `python -I scripts/check_env_example.py` exits 0 on the repository;
  `pytest scripts/tests` (`test_check_env_example.py`) runs it on the real repository and on a
  failing fixture for each rule above, plus the `no-latest` stand-in test.
- `docker compose config -q` and `docker compose --env-file .env.example config -q` pass.
- `pnpm format:check` in the frontend `dev` image uses the explicit Prettier settings.
- Review checks (DOCKER.md §8): no `env_file:` in any compose file; new variables are added to
  `.env.example` by the story that reads them; only orchestration files and repository-wide
  dotfiles at the root; files conform to `.editorconfig`.
- US-01.09 acceptance: the real `no-latest` check scans `.env.example` and the stand-in test is
  removed.

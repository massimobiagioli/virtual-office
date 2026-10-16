# Virtual Office — Engineering Principles

| Field   | Value                                                                  |
| ------- | ---------------------------------------------------------------------- |
| Status  | Accepted                                                               |
| Date    | 2026-10-16                                                             |
| Related | [CONSTITUTION.md](CONSTITUTION.md) (Articles III and XVIII), [STACK.md](STACK.md) |

The Constitution says **what** Virtual Office is and which rules it obeys. This document says
**how we work** to build it. It applies to every contributor, human or AI coding agent. Where
it conflicts with the Constitution, the Constitution wins.

We follow six schools of thought. They reinforce each other:

| School                        | Gives us                                   |
| ----------------------------- | ------------------------------------------ |
| Agile                         | Short feedback loops with the product owner |
| Extreme Programming (XP)      | Engineering practices that make change cheap |
| Test-Driven Development (TDD) | Design pressure and a safety net            |
| Domain-Driven Design (DDD)    | A model that matches how the office works   |
| The Twelve-Factor App         | Services that run the same everywhere       |
| Technical Excellence          | The standard all of the above is held to    |

---

## 1. Agile

We value the [Agile Manifesto](https://agilemanifesto.org/): individuals and interactions,
working software, customer collaboration and responding to change.

### Practices

1. **Vertical slices.** Every increment is usable end to end (UI → API → domain → storage),
   even if thin. No "backend done, frontend later" increments.
2. **Small batches.** A change should be reviewable in under 30 minutes. Bigger work is split.
3. **Working software every iteration.** `main` is always releasable: `docker compose up`
   gives a running office at any commit.
4. **User stories with acceptance criteria** in Given/When/Then; criteria become tests.
5. **Definition of Ready / Done** for our own work mirror the ones in the product
   (Constitution §8.3–8.4): we eat our own dog food.
6. **Iterations map to milestones** (Constitution Article XXII). Each milestone ends with a
   demo to the product owner and a short retrospective, recorded in `.docs/retros/` when held.
7. **Inspect and adapt.** When a practice slows us down without adding value, we change it —
   through an ADR, not by quietly ignoring it.

---

## 2. Extreme Programming (XP)

### Values

Communication, simplicity, feedback, courage, respect.

### Practices we adopt

| Practice                 | How we apply it |
| ------------------------ | --------------- |
| **Test-first**           | See §3. |
| **Pair / mob programming** | Human + AI coding agent is a pair: the human sets direction and reviews, the agent drives. Non-trivial domain changes get a second reviewer. |
| **Continuous integration** | Integrate to `main` at least daily; short-lived branches (≤ 2 days); CI is green or fixing it is the top priority. |
| **Collective code ownership** | Anyone may improve any code, respecting the boundaries and the gate. |
| **Simple design** (Kent Beck's rules, in order) | 1. passes the tests; 2. reveals intention; 3. no duplication; 4. fewest elements. |
| **Refactoring**          | Continuous, in small safe steps, always under green tests. Never mixed with behavior changes in the same commit. |
| **YAGNI**                | Build what the current story needs. Extension points only when a second real use exists. |
| **Small releases**       | Every merge to `main` is deployable. |
| **Coding standards**     | Enforced by tools (ruff, mypy, eslint, prettier, vue-tsc), not by debate. |
| **Sustainable pace**     | No heroics; scope is cut before quality is. |
| **Spikes**               | Time-boxed experiments on throwaway branches; the outcome is knowledge or an ADR, not production code. |
| **Customer on site**     | The product owner is available to answer questions; open questions are asked, not guessed. |

---

## 3. Test-Driven Development (TDD)

### The cycle

1. **Red** — write the smallest failing test that expresses the next bit of behavior.
2. **Green** — write the simplest code that makes it pass.
3. **Refactor** — clean up code and tests while staying green.

Commit at green. Never commit red to `main`.

### Rules

1. **No production code without a failing test first** in `domain`, `application` and
   `office-engine`. For UI components and adapters, tests may follow immediately but must land
   in the same change.
2. **Test behavior, not implementation.** Assert on outputs, emitted events and observable
   state — not on private methods or call counts (except at port boundaries).
3. **Domain tests are Given/When/Then over events:**
   given past events → when a command → then expected new events *or* a domain error.
4. **Fast tests.** The domain suite runs in seconds, with no I/O, no clock, no randomness
   (inject them).
5. **Test doubles only at ports.** Fakes for repositories/event store in unit tests; real
   Postgres (testcontainers) in integration tests; Pydantic AI `TestModel`/`FunctionModel` for
   agents. Never mock what you don't own — wrap it in a port first.
6. **Property-based tests** for invariants (WIP limit, review gate, pathfinding) with
   Hypothesis (Python) and fast-check (TypeScript).
7. **Test pyramid:** many unit tests, fewer integration tests, few E2E tests (only Constitution
   Appendix E scenarios). Visual regression for the Amiga UI kit and the office scene.
8. **Bug fixes start with a test that reproduces the bug.**
9. **Coverage is a signal, not a goal** — but thresholds in Constitution §18.2 are enforced.
   Mutation testing may be run on the domain to verify test strength.
10. **Tests are documentation.** Names read as sentences:
    `test_pull_is_rejected_when_todo_is_full`, `it('walks the card to the QA bench')`.

---

## 4. Domain-Driven Design (DDD)

### Strategic design

**Ubiquitous language:** the Glossary (Constitution Article II) is the language of code, tests,
UI copy, events and conversations. If a term is missing, add it there first.

**Bounded contexts** (modules of `core`, plus the catalog service):

| Context        | Responsibility                                     | Lives in                    |
| -------------- | -------------------------------------------------- | --------------------------- |
| **Kanban**     | Projects, cards, columns, workflow rules, reviews  | `core/domain/kanban`        |
| **Staff**      | Office, agents, personas, status, memory           | `core/domain/staff`         |
| **Intake**     | Notes, classification, triage                      | `core/domain/intake`        |
| **Decisions**  | Project ADRs                                       | `core/domain/decisions`     |
| **Conversation** | PM chat, proposed commands                      | `core/application/chat`     |
| **Agent Catalog** | Role definitions, prompts, characters           | `catalog` service    |
| **Office Scene** | Visual projection: map, sprites, choreographies (generic subdomain, read-only) | `frontend/src/office-engine` |

**Context map:**

- Kanban ↔ Staff: **partnership** inside `core`, coordinated by application services in one
  transaction (Constitution §15.5).
- Core → Agent Catalog: **customer/supplier** with an **anti-corruption layer** in
  `core/infrastructure/catalog` (catalog DTOs never leak into the domain).
- Core → LLM providers: **anti-corruption layer** through Pydantic AI and the agents module.
- Office Scene: **conformist** to the published event language (`core`'s OpenAPI/event schemas).

### Tactical design

1. **Aggregates** protect invariants and are the only entry point to change state: `Project`,
   `Card`, `Agent`, `Office`, `Note`, `Adr`. One transaction changes one aggregate, except
   documented cross-aggregate application services.
2. **Value objects** for everything with no identity: `CardId`, `ProjectKey`, `Priority`,
   `Estimate`, `Column`, `PersonaName`, `FaceId`, `TilePosition`. Immutable, self-validating
   (Pydantic `frozen=True` models or `dataclass(frozen=True)`).
3. **Domain events** are first-class (Constitution Appendix B), past tense, immutable.
4. **Domain services** only for logic that belongs to no single aggregate (e.g. assignment
   scoring).
5. **Repositories** per aggregate, defined as `Protocol`s in `application`, implemented in
   `infrastructure` (event-sourced).
6. **Application services** orchestrate: load → decide → append → publish. No business rules
   there.
7. **No anemic model.** Rules live on aggregates/value objects, not in handlers, routers, Vue
   components or prompts.
8. **Persistence ignorance.** The domain never imports SQLAlchemy, FastAPI, Pydantic AI or
   httpx.
9. **Errors are values** in the domain (typed results / domain error types), not HTTP codes.
   The API layer maps them.

---

## 5. The Twelve-Factor App

| # | Factor               | How Virtual Office complies |
| - | -------------------- | --------------------------- |
| I | **Codebase**         | One repository, many deploys (dev, CI, local prod-like). Each service builds from its directory. |
| II | **Dependencies**    | Declared and pinned exactly (`pyproject.toml` + `uv.lock`, `package.json` + `pnpm-lock.yaml`); isolated in containers; nothing relies on host tools. |
| III | **Config**         | All config in environment variables (`pydantic-settings`, Vite build-time vars only for non-secret values). `.env.example` documents every variable. No config in code, no secrets in the repo. |
| IV | **Backing services** | Postgres, Ollama, catalog and optional cloud LLMs are attached resources addressed by URL from env (`VO_DATABASE_URL`, `VO_OLLAMA_BASE_URL`, `VO_CATALOG_URL`). Swapping one requires no code change. |
| V | **Build, release, run** | Strict separation: images are built once (build), combined with env config (release), and run by compose (run). Images are immutable and tagged with the git SHA. |
| VI | **Processes**       | Services are stateless; all state lives in Postgres (and the Ollama model volume). No sticky sessions; WebSocket clients resync from `lastEventId`. |
| VII | **Port binding**   | Each service is self-contained and exports HTTP on its port (`core:8000`, `catalog:8001`, `frontend:8080`). |
| VIII | **Concurrency**   | Scale by process type: `core` web, Orchestrator worker loop (same image, separate command when needed), catalog. Concurrency of LLM jobs is configurable. |
| IX | **Disposability**   | Fast startup (< 5 s excluding model pulls), graceful shutdown on SIGTERM: stop accepting work, finish/checkpoint running agent jobs (Constitution §15.6), close connections. |
| X | **Dev/prod parity**  | Same images and same Postgres version in dev, CI and prod-like; tests use real Postgres via testcontainers, not SQLite. |
| XI | **Logs**            | Logs are event streams to stdout as JSON (structlog / nginx JSON format); never written to files by the app. |
| XII | **Admin processes** | Migrations, model pulls, catalog seeding, projection rebuilds and backups are one-off containers (`migrate-*`, `ollama-init`, `catalog-seed`, `rebuild-projections`, `backup`) using the same images. |

---

## 6. Technical Excellence

1. **Clean Code.** Intention-revealing names in the ubiquitous language; small functions;
   one level of abstraction per function; no dead code; no commented-out code.
2. **SOLID**, applied pragmatically — especially Single Responsibility and Dependency
   Inversion (ports and adapters).
3. **Hexagonal architecture** with enforced boundaries (import-linter in Python, ESLint
   boundary rules in the frontend).
4. **Type safety everywhere.** mypy `--strict`, TypeScript `strict` + `noUncheckedIndexedAccess`;
   no `Any`/`any` without a written justification.
5. **Make illegal states unrepresentable.** Use enums, discriminated unions and value objects
   instead of loose strings and booleans.
6. **Fail fast and loudly** at boundaries (validation at the edge with Pydantic), and
   gracefully toward the user (requesters, Guru Meditation with correlation ID).
7. **Observability by design.** Structured logs with correlation IDs, OpenTelemetry traces
   across `frontend → core → catalog/ollama`, metrics for job durations, queue sizes, token
   usage.
8. **Security by default.** Least privilege (DB roles, agent toolsets, non-root containers),
   secrets only in env, dependency and image scanning, untrusted-input discipline for LLMs.
9. **Performance budgets** (Constitution §18.6) are tested, not hoped for.
10. **Accessibility is a feature**, verified with automated checks (axe in Playwright) and
    keyboard-only walkthroughs.
11. **Documentation as code.** Markdown in `.docs/`, Mermaid diagrams, ADRs for decisions;
    updated in the same change as the code.
12. **Boy Scout Rule.** Leave every file a little better than you found it — in a separate
    refactoring commit.
13. **Code review** checks behavior, tests, naming, boundaries, docs and ADRs — not style
    (tools do that).
14. **Latest stable, never obsolete, never `latest`** (see [STACK.md §1](STACK.md#1-version-policy-non-negotiable)).
15. **Everything in English** (Constitution Article XIX).

---

## 7. Quick checklist before declaring a change done

```
- [ ] Story has Given/When/Then criteria and each one has a test
- [ ] Tests were written first (red → green → refactor) where TDD applies
- [ ] Domain logic is in aggregates/value objects, named in the ubiquitous language
- [ ] Boundaries respected (import-linter / eslint boundaries green)
- [ ] Config via env only; nothing host-specific; works with `docker compose up`
- [ ] Lint, format, type-check, unit, integration, E2E all green (and actually run)
- [ ] Docs / Glossary / ADRs updated; new .md files referenced in AGENTS.md
- [ ] Commit messages: Conventional Commits, English
```

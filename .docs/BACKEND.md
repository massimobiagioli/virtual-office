# Virtual Office — Backend Guide

| Field   | Value                                                                                   |
| ------- | --------------------------------------------------------------------------------------- |
| Scope   | `services/core` and `services/catalog` (Python, FastAPI, Pydantic, Pydantic AI)  |
| Related | [CONSTITUTION.md](CONSTITUTION.md) · [STACK.md](STACK.md) · [PRINCIPLES.md](PRINCIPLES.md) · [POSTGRES.md](POSTGRES.md) · [OLLAMA.md](OLLAMA.md) · [DOCKER.md](DOCKER.md) |

This guide is the **standard** for writing backend code. Two services, one style: a reader
must not be able to tell who wrote which file. Versions come from [STACK.md](STACK.md); this
file never repeats them.

---

## 1. Service projects

Each service is an **independent uv project**; there is no Python manifest at the repository
root ([ADR-0004](adr/0004-per-service-python-projects.md)).

```
services/
├── core/                         # Docker build context of the core image
│   ├── pyproject.toml            # name = "virtual-office-core", deps, dev group, tool config
│   ├── uv.lock                   # committed
│   ├── Dockerfile
│   ├── alembic.ini · alembic/
│   ├── src/virtual_office/       # import package
│   └── tests/
└── catalog/                      # Docker build context of the catalog image
    ├── pyproject.toml            # name = "virtual-office-catalog", same tool config
    ├── uv.lock                   # committed
    ├── Dockerfile
    ├── alembic.ini · alembic/
    ├── catalog/                  # source definitions (YAML, Markdown prompts, evals)
    ├── src/catalog/
    └── tests/
```

Rules:

1. **`src/` layout** for every service; tests live outside the package.
2. Direct dependencies pinned with `==` in the service `pyproject.toml`; dev tools in a
   `[dependency-groups] dev` group. Never add a dependency without updating STACK.md.
3. Tool configuration (`ruff`, `mypy`, `pytest`, `coverage`, `importlinter`) lives in each
   service `pyproject.toml` and is **identical** in both services except for package names
   and paths; a tooling check fails on drift. `[tool.uv] required-version` pins the STACK.md
   uv version.
4. `requires-python` is the exact minor of the runtime in STACK.md (e.g. `">=3.15,<3.16"`).
5. All commands run inside the service container (see [DOCKER.md](DOCKER.md)), from the
   service folder (`uv sync --frozen`, `uv lock --check`); the host has no Python toolchain
   requirement.

---

## 2. `core` package layout (DDD + hexagonal)

```
virtual_office/
├── domain/
│   ├── shared/                   # base classes: ValueObject, DomainEvent, DomainError, Clock protocol, ids
│   ├── kanban/                   # Project, Card, Column, WorkflowPolicy, events.py, errors.py
│   ├── staff/                    # Office, Agent, Persona, events.py, errors.py
│   ├── intake/                   # Note, TriageReport, events.py, errors.py
│   └── decisions/                # Adr, events.py, errors.py
├── application/
│   ├── ports.py                  # Protocols: EventStore, UnitOfWork, Clock, IdGenerator, CatalogClient, …
│   ├── commands/                 # one module per use case: <verb>_<noun>.py (command model + handler)
│   ├── queries/                  # read models access (projections)
│   ├── orchestrator/             # tick loop, scheduling, assignment service
│   └── chat/                     # PM conversation use cases
├── agents/
│   ├── shared/                   # base deps, untrusted-data wrapper, usage recording
│   └── <role>/                   # outputs.py, deps.py, tools.py, context_pack.py, to_commands.py, factory.py
├── infrastructure/
│   ├── db/                       # engine, session, metadata, tables
│   ├── event_store/              # Postgres event store, upcasters
│   ├── projections/              # projectors + projection repositories
│   ├── catalog/                  # HTTP client + anti-corruption layer for catalog
│   ├── llm/                      # model factory (Ollama / optional cloud)
│   └── workspace/                # sandboxed git + command runner
├── api/
│   ├── app.py                    # create_app() factory, lifespan
│   ├── dependencies.py           # FastAPI Depends providers
│   ├── errors.py                 # domain error → problem details mapping
│   ├── routers/                  # one router per resource
│   ├── schemas/                  # request/response DTOs (never domain objects)
│   └── ws/                       # WebSocket gateway and message models
├── settings.py                   # pydantic-settings
└── main.py                       # uvicorn factory: create_app() reads Settings from the env
```

`catalog` uses the same shape, minus `agents/` and `orchestrator/`.

### 2.1 Dependency rule (import-linter contracts, CI-enforced)

```toml
[tool.importlinter]
root_packages = ["virtual_office"]

[[tool.importlinter.contracts]]
name = "Hexagonal layers"
type = "layers"
layers = [
  "virtual_office.api | virtual_office.infrastructure",
  "virtual_office.agents",
  "virtual_office.application",
  "virtual_office.domain",
]

[[tool.importlinter.contracts]]
name = "Domain is pure"
type = "forbidden"
source_modules = ["virtual_office.domain"]
forbidden_modules = ["fastapi", "sqlalchemy", "asyncpg", "pydantic_ai", "httpx", "structlog"]

[[tool.importlinter.contracts]]
name = "Bounded contexts are independent"
type = "independence"
modules = [
  "virtual_office.domain.kanban",
  "virtual_office.domain.staff",
  "virtual_office.domain.intake",
  "virtual_office.domain.decisions",
]
```

Contexts talk to each other only through `domain.shared` types (ids, events) or application
services.

---

## 3. Python style

| Topic          | Standard |
| -------------- | -------- |
| Formatter      | `ruff format` (line length 100, double quotes) |
| Linter         | `ruff check` with rule sets `E, W, F, I, B, UP, SIM, RUF, N, ASYNC, S, PT, PL, C4, DTZ, T20, ERA, TRY, PERF, FURB` |
| Types          | `mypy --strict` with the `pydantic.mypy` plugin; zero errors; `# type: ignore[code]` only with a comment explaining why |
| Imports        | Absolute imports only; `from __future__ import annotations` is **not** used (PEP 649 semantics are native) |
| Naming         | `snake_case` modules/functions/variables, `PascalCase` classes, `UPPER_SNAKE` constants; names come from the Glossary |
| Docstrings     | Only for public application/API symbols and non-obvious domain rules; explain *why* |
| `print`        | Forbidden (T20); use the logger |
| Time           | Never `datetime.now()`; inject `Clock`. Always timezone-aware UTC (DTZ rules) |
| Ids            | ULID via the injected `IdGenerator`; persisted as `uuid` (see POSTGRES.md) |
| Collections    | Domain uses immutable `tuple`/`frozenset`; no mutable default arguments |
| Enums          | `enum.StrEnum` for closed vocabularies (`Column`, `Priority`, `Role`) |
| Pattern matching | Preferred over `isinstance` chains for events and commands |

---

## 4. Pydantic conventions

### 4.1 Base models (defined once in `domain/shared` and `api/schemas`)

```python
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ValueObject(BaseModel):
    """Immutable, self-validating domain value."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class ApiModel(BaseModel):
    """Every API/WebSocket DTO: snake_case in Python, camelCase on the wire."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True,
    )
```

Rules:

1. Every model is **frozen** and **`extra="forbid"`**. Mutation = new instance
   (`model_copy(update=...)`).
2. Domain value objects validate their invariants in `field_validator` / `model_validator`
   (e.g. `ProjectKey` matches `^[A-Z]{2,6}$`, `Estimate ∈ {1,2,3,5,8}`).
3. **Domain models never leave the domain.** The API maps them to `ApiModel` DTOs in
   `api/schemas`; agents map them to their own output models.
4. Use `Annotated` types for reusable constraints (`Title = Annotated[str, StringConstraints(min_length=5, max_length=100)]`).
5. Discriminated unions with `Field(discriminator="kind")` for commands, events, deliverables
   and WebSocket messages.
6. No `Any`, no `dict[str, Any]` payloads in public models — define a model.

### 4.2 Domain events

```python
class CardRejected(DomainEvent):
    type: Literal["CardRejected"] = "CardRejected"
    version: Literal[1] = 1
    card_id: CardId
    review: Review
    rework_count: NonNegativeInt
```

- Class name = event type = past tense (Constitution Appendix B).
- `version` is a `Literal`; a new shape is a new class version plus an upcaster
  (skill `tracing-events`).

### 4.3 Settings

```python
from pydantic import AliasGenerator, HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_name(field_name: str) -> str:
    return f"VO_{field_name.upper()}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        alias_generator=AliasGenerator(validation_alias=_env_name),  # errors name VO_* vars
        validate_by_name=True,
        extra="forbid",
        frozen=True,
    )

    database_url: PostgresDsn
    catalog_url: HttpUrl
    ollama_base_url: HttpUrl
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    office_tick_ms: int = Field(default=2000, ge=500, le=10000)
```

- Twelve-factor: **environment only**. No `.env` file is read in production images; compose
  injects variables. Every variable is documented in `.env.example`.
- Prefix `VO_` for application variables, applied through the validation alias so that a
  missing or invalid variable is reported by its environment name (`VO_DATABASE_URL`);
  third-party standard names (e.g. `ANTHROPIC_API_KEY`) are read as-is.
- Secrets use `SecretStr` and are never logged.
- `Settings` is created once by the `main.create_app()` factory when uvicorn starts, passed
  to `api.app.create_app(settings)` and kept on `app.state`; never imported as a global.

---

## 5. Domain layer patterns

1. **Decide / evolve.** Each aggregate exposes pure functions:
   - `decide(state, command, context) -> tuple[DomainEvent, ...] | DomainError`
   - `evolve(state, event) -> state`
   Aggregates are rebuilt by folding `evolve` over their events.
2. **Errors as values.** `DomainError` subclasses are frozen models with a stable `code`
   (`WipLimitReached`, `TransitionNotAllowed`, … — skill `enforcing-kanban-workflow`).
   Domain code never raises for business outcomes; exceptions are for bugs only.
3. **Policies as small objects** (`WorkflowPolicy`, `AssignmentPolicy`) with pure methods,
   injected into `decide` via `context` when they need configuration.
4. No I/O, no logging, no clock, no randomness in the domain.

---

## 6. Application layer patterns

1. **One use case per module**: `application/commands/pull_card.py` contains `PullCard`
   (command model) and `PullCardHandler`.
2. Handler shape — always the same:

   ```python
   class PullCardHandler:
       def __init__(self, uow: UnitOfWork, clock: Clock, ids: IdGenerator) -> None: ...

       async def __call__(self, command: PullCard, actor: Actor) -> CommandResult:
           async with self._uow as uow:
               project = await uow.projects.load(command.project_id)
               card = await uow.cards.load(command.card_id)
               outcome = kanban.decide_pull(project, card, command, self._context())
               if isinstance(outcome, DomainError):
                   await uow.diagnostics.command_rejected(command, outcome, actor)
                   return CommandResult.rejected(outcome)
               await uow.events.append(outcome, actor=actor, expected_versions=...)
               await uow.commit()          # appends + projections in ONE transaction
           return CommandResult.accepted(outcome)
   ```

3. **Ports are `typing.Protocol`s** in `application/ports.py`; adapters live in
   `infrastructure`. Tests use in-memory fakes of the same Protocols.
4. **Unit of Work** owns the transaction; after commit it hands events to the broadcaster.
5. **Authorization** (Constitution §5.9) is checked in the handler before `decide`, by an
   `ActorPolicy` from the domain.
6. **Queries** read projections only and return DTO-ready models; they never load aggregates.

---

## 7. API layer (FastAPI)

| Topic              | Standard |
| ------------------ | -------- |
| App creation       | `create_app(settings) -> FastAPI` factory + `lifespan` async context manager (no `on_event`) |
| Routers            | One `APIRouter` per resource, prefix `/api/<resource>`, `tags=[<resource>]` |
| Operation IDs      | Explicit `operation_id="<resource>_<action>"` (stable names for generated TS clients) |
| Request/response   | Always `ApiModel` DTOs, declared via return type annotations; `response_model_exclude_none` is not used (explicit `null`) |
| Dependencies       | `Annotated[..., Depends(...)]` aliases in `api/dependencies.py` |
| Errors             | RFC 9457 **Problem Details** (`application/problem+json`): `type`, `title`, `status`, `detail`, `code` (domain error code), `correlationId` |
| Status codes       | 200 read, 201 create, 202 command accepted asynchronously, 409 domain rule violation / concurrency, 422 validation, 404 not found |
| Commands           | `POST /api/commands` with a discriminated union body; specific convenience endpoints delegate to the same handlers |
| Pagination         | Cursor-based (`?cursor=&limit=`), response `{ items, nextCursor }`; never offset pagination on event lists |
| Correlation        | Middleware reads/creates `X-Correlation-Id`, binds it to structlog context and returns it |
| OpenAPI            | Published at `/api/openapi.json`; WebSocket message models added to `components.schemas` via a custom `openapi()` hook; CI exports it and regenerates frontend types |
| Docs UI            | `/api/docs` enabled only when `VO_ENV=dev` |
| Health             | `GET /health/live` (process up) and `GET /health/ready` (DB + catalog + ollama reachable) |

### 7.1 WebSocket gateway

- Single endpoint `/ws`; messages are `ApiModel` discriminated unions with `v: 1`.
- Protocol from Constitution §15.10 (`hello`, delta or `resync`, heartbeat 15 s).
- Broadcast only after commit; one `asyncio.Queue` per connection with a bounded size —
  a slow client gets `resync` instead of unbounded buffering.
- Commands received over WS go through the **same** handlers as REST.

---

## 8. Async rules

1. All I/O is async (asyncpg, httpx, Pydantic AI). Blocking calls (git subprocess, file
   hashing) run via `anyio.to_thread.run_sync` or `anyio.run_process`.
2. Use **anyio** primitives (task groups, cancel scopes, `fail_after`) — no bare
   `asyncio.create_task` without a supervising task group.
3. Every outbound call has a timeout (catalog 5 s, LLM per role setting, workspace commands
   5 min — Constitution §17.3).
4. The Orchestrator tick runs in a task group started in the app lifespan and stops cleanly on
   SIGTERM (twelve-factor IX): stop pulling, checkpoint jobs, drain.

---

## 9. Agents with Pydantic AI

### 9.1 Building an agent

```python
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider


@dataclass(frozen=True)
class QaDeps:
    board: BoardQueries          # ports only — least privilege (Constitution §15.7)
    workspace: ReadOnlyWorkspace


def build_qa_agent(definition: RoleDefinition, model: OllamaModel) -> Agent[QaDeps, ReviewVerdict]:
    agent = Agent(
        model,
        deps_type=QaDeps,
        output_type=ReviewVerdict,          # Pydantic model = structured output
        instructions=definition.instructions,
        name=f"qa@{definition.version}",
        retries=1,
    )

    @agent.tool
    async def read_file(ctx: RunContext[QaDeps], path: str) -> str:
        """Read a file from the card's workspace branch (max 64 KB)."""
        return await ctx.deps.workspace.read_text(path, max_bytes=65_536)

    return agent
```

Model construction lives in `infrastructure/llm`:

```python
def ollama_model(settings: Settings, tag: ModelTag) -> OllamaModel:
    provider = OllamaProvider(base_url=f"{settings.ollama_base_url}v1")
    return OllamaModel(str(tag), provider=provider)
```

### 9.2 Rules

1. Agents are **built by factories** from the catalog definition; no module-level global
   agents.
2. `deps_type` is a frozen dataclass exposing only the ports allowed for the role.
3. Tools call **application** ports; they never touch SQLAlchemy or the event store.
4. Tool docstrings are written for the model (what it does, limits); they are part of the
   prompt and reviewed like prompts.
5. `output_type` is always a Pydantic model from `agents/<role>/outputs.py`.
6. Untrusted content is wrapped with the shared `untrusted_block(label, text)` helper before
   being passed to the model (Constitution §16.6).
7. After every run, record `result.usage()` into the job events (tokens, requests).
8. Tool and output retries: default `retries=1`; raise `ModelRetry` from a tool only for
   recoverable model mistakes (bad path, missing id).
9. Model tags come from settings/catalog — never string literals in code.

### 9.3 Testing agents

```python
import pydantic_ai.models
from pydantic_ai.models.test import TestModel

pydantic_ai.models.ALLOW_MODEL_REQUESTS = False   # in tests/conftest.py: no real LLM, ever


async def test_qa_rejects_when_a_criterion_fails(qa_agent, qa_deps):
    with qa_agent.override(model=TestModel(custom_output_args=REJECTION)):
        result = await qa_agent.run("Review SHOP-12", deps=qa_deps)
    assert result.output.verdict == "changes_requested"
```

- `TestModel` for structural tests, `FunctionModel` for scripted conversations.
- Role evaluation sets use **pydantic-evals** (same version line as Pydantic AI, see
  STACK.md), run against the real Ollama service only in the dedicated eval job, never in
  the unit suite.

---

## 10. Logging and observability

- **structlog**, JSON renderer to stdout, one event per line; keys in `snake_case`.
- Mandatory context keys: `service`, `env`, `correlation_id`; plus `agent_id`, `job_id`,
  `card_id`, `project_key` when known (bound with `structlog.contextvars`).
- Log levels: `debug` dev only; `info` lifecycle and accepted commands; `warning` rejected
  commands and retries; `error` failures with stack trace.
- A redaction processor removes secrets before rendering.
- OpenTelemetry: FastAPI, httpx, SQLAlchemy and Pydantic AI instrumentation; exporter enabled
  only if `OTEL_EXPORTER_OTLP_ENDPOINT` is set.

---

## 11. Testing

| Level        | Location                     | Tools                               | Rules |
| ------------ | ---------------------------- | ----------------------------------- | ----- |
| Domain       | `tests/unit/domain/<context>/` | pytest, Hypothesis                | Given events / When command / Then events or error; no fixtures with I/O |
| Application  | `tests/unit/application/`    | pytest, in-memory fakes, fake clock | Handlers and Orchestrator ticks |
| Agents       | `tests/unit/agents/<role>/`  | Pydantic AI `TestModel`/`FunctionModel` | Output → commands mapping, tool permissions |
| Integration  | `tests/integration/`         | testcontainers Postgres, respx      | Event store, projections, migrations, API with real DB |
| Contract     | `tests/contract/`            | OpenAPI snapshot                    | Breaking API changes fail unless intentional |

- Test names: `test_<behavior>_when_<condition>`.
- Markers: `@pytest.mark.integration`, `@pytest.mark.eval` (excluded by default).
- Async tests use the **anyio** pytest plugin (`@pytest.mark.anyio`), backend `asyncio`.
- Factories with polyfactory in `tests/factories/`; no hand-built giant fixtures.
- Coverage thresholds from Constitution §18.2 enforced by `pytest-cov` (`--cov-fail-under`
  per package via separate runs).

---

## 12. Review checklist (backend)

```
- [ ] Layer and context boundaries respected (import-linter green)
- [ ] Domain change has Given/When/Then tests and, if it is an invariant, a Hypothesis test
- [ ] New/changed events: versioned, upcaster if needed, Appendix B updated
- [ ] DTOs are ApiModel (camelCase on the wire); operation_id set; problem details for errors
- [ ] No blocking I/O in async code; every outbound call has a timeout
- [ ] Settings via env only; .env.example updated
- [ ] Agents: least-privilege deps, Pydantic output_type, usage recorded, tests with TestModel
- [ ] ruff, mypy --strict, pytest (unit + integration) green
```

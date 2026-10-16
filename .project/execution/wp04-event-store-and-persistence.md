# WP04 — Event Store & Persistence

| Field        | Value |
| ------------ | ----- |
| Milestone    | M1 — Kickstart |
| Status       | READY |
| Depends on   | WP02, WP03 |
| Enables      | WP05, WP06, every event-sourced feature |
| Constitution | Article XII (§12.1), §15.4, §15.5, Appendix A (`DomainEvent`) |
| Guides       | [POSTGRES.md](../../.docs/POSTGRES.md) · [BACKEND.md](../../.docs/BACKEND.md) §5–6, §11 · [DOCKER.md](../../.docs/DOCKER.md) §6 |
| Skills       | `tracing-events`, `delivering-features`, `writing-adrs` |
| Estimate     | 37 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-04.01 — Alembic environments for both services (3 pts)
- [ ] US-04.02 — Event store schema, append-only trigger and privileges (5 pts)
- [ ] US-04.03 — Projection and runtime schemas baseline (2 pts)
- [ ] US-04.04 — Append events with optimistic concurrency (5 pts)
- [ ] US-04.05 — Load streams and read all from a position (3 pts)
- [ ] US-04.06 — Event serialization and upcaster registry (3 pts)
- [ ] US-04.07 — Unit of Work with post-commit publication (5 pts)
- [ ] US-04.08 — Projector framework with checkpoints and idempotency (5 pts)
- [ ] US-04.09 — Rebuild-projections job (3 pts)
- [ ] US-04.10 — In-process event bus for post-commit subscribers (3 pts)

## 1. Objective

Provide the persistence backbone of Virtual Office: an append-only, optimistically concurrent
Postgres event store; a Unit of Work that appends events and updates projections in one
transaction; a projector framework; and a rebuild job. After WP04 every later feature only has
to define events, decisions and projections.

## 2. Scope

**In:** Alembic setup for `core` and `catalog`; schemas `event_store`, `projection`,
`runtime`; event store adapter; serialization and upcasting; Unit of Work; projector base;
checkpoints; rebuild job; in-process post-commit bus; integration tests with testcontainers.

**Out:** concrete domain events and projections (WP05, WP06); WebSocket broadcast (WP06 uses
the bus); snapshots (only the table is created, usage deferred until measured need).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D04.1 | Migrations | Alembic async environments for both services; `core` baseline creating the three schemas, the `events` table (POSTGRES.md §5), the append-only trigger and runtime privileges | Migrations up/down on a fresh container; `core_app` cannot UPDATE/DELETE events | US-04.01 – US-04.03 |
| D04.2 | Event store adapter | `PostgresEventStore` implementing the `EventStore` port: append with expected versions, load stream, read all from position, serialization, upcasting | Integration tests incl. concurrent append conflict | US-04.04 – US-04.06 |
| D04.3 | Unit of Work & projections | `UnitOfWork` port + SQLAlchemy implementation; projector framework with checkpoints, idempotency, same-transaction updates; in-process post-commit bus | Tests prove atomicity (failure rolls back events and projections) and idempotency | US-04.07, US-04.08, US-04.10 |
| D04.4 | Rebuild job | `rebuild-projections` one-off container replaying all events into fresh projections | Equality test incremental vs rebuilt | US-04.09 |

## 4. User stories

### D04.1 — Migrations

#### US-04.01 — Alembic environments for both services

- [ ] **US-04.01 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a backend developer, I want an async Alembic environment per service with the
  project naming convention, so that every schema change is versioned the same way.
- **Acceptance criteria:**
  - [ ] AC1 — Given `services/core/alembic/` and `services/catalog/alembic/`, when
    `alembic upgrade head` runs in the `migrate-*` job, then it connects with the **owner**
    role DSN from env and succeeds on an empty database.
  - [ ] AC2 — Given `alembic.ini`, when a revision is created, then its file name follows
    `YYYYMMDD_HHMM_<slug>.py`.
  - [ ] AC3 — Given the shared `MetaData`, when constraints are generated, then names follow
    the naming convention of POSTGRES.md §4.1.
  - [ ] AC4 — Given `alembic downgrade base` then `upgrade head`, when run in an integration
    test, then both succeed.
- **Tasks:**
  - [ ] Create async `env.py` using `VO_DATABASE_OWNER_URL`.
  - [ ] Define `infrastructure/db/metadata.py` with `NAMING_CONVENTION`.
  - [ ] Wire `migrate-core` / `migrate-catalog` commands in compose.
  - [ ] Add `.env.example` entries for owner DSNs/passwords.
- **Tests:** integration test `test_migrations_roundtrip` (testcontainers).
- **Done when:** both jobs complete in the compose stack.

#### US-04.02 — Event store schema, append-only trigger and privileges

- [ ] **US-04.02 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want the event store to be physically append-only, so that
  history can never be rewritten (Constitution P3).
- **Acceptance criteria:**
  - [ ] AC1 — Given the baseline migration, when applied, then `event_store.events` exists with
    exactly the columns, constraints and indexes of POSTGRES.md §5.
  - [ ] AC2 — Given `core_app`, when it executes `UPDATE` or `DELETE` on `event_store.events`,
    then Postgres raises a permission error.
  - [ ] AC3 — Given the owner role outside a migration, when it executes `UPDATE`/`DELETE` on
    events, then the trigger raises `events are append-only`.
  - [ ] AC4 — Given `core_app`, when it inserts a valid row and selects it, then both succeed.
  - [ ] AC5 — Given two rows with the same `(aggregate_type, aggregate_id, aggregate_version)`,
    when inserted, then the unique constraint rejects the second.
- **Tasks:**
  - [ ] Migration: schema, table, indexes, trigger function, trigger.
  - [ ] Grants: `SELECT, INSERT` for `core_app`; default privileges for future tables.
  - [ ] `event_store.snapshots` and `event_store.projection_checkpoints` tables.
- **Tests:** SQL-level integration tests for AC1–AC5.
- **Done when:** tests green against the `postgres` image of STACK.md.

#### US-04.03 — Projection and runtime schemas baseline

- [ ] **US-04.03 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a backend developer, I want the `projection` and `runtime` schemas ready with
  privileges, so that later WPs only add tables.
- **Acceptance criteria:**
  - [ ] AC1 — Given the baseline, when applied, then schemas `projection` and `runtime` exist,
    owned by `core_owner`.
  - [ ] AC2 — Given a table later created in `projection`, when `core_app` accesses it, then it
    has `SELECT, INSERT, UPDATE, DELETE` via default privileges.
  - [ ] AC3 — Given `runtime.diagnostics` (rejected commands log), when created, then it has
    columns `id`, `occurred_at`, `command_type`, `actor`, `error_code`, `detail`,
    `correlation_id`.
- **Tasks:**
  - [ ] Migration creating both schemas and `runtime.diagnostics`.
  - [ ] Default privileges for `core_app`.
- **Tests:** integration test creating a temp table and checking privileges.
- **Done when:** migration merged and tested.

### D04.2 — Event store adapter

#### US-04.04 — Append events with optimistic concurrency

- [ ] **US-04.04 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As a command handler, I want to append events to an aggregate stream with the
  expected version, so that concurrent writers never silently overwrite each other.
- **Acceptance criteria:**
  - [ ] AC1 — Given a stream at version 3, when appending 2 events with `expected_version=3`,
    then they are stored with versions 4 and 5 and increasing `global_position`.
  - [ ] AC2 — Given a stream at version 3, when appending with `expected_version=2`, then
    `ConcurrencyConflict` is returned and nothing is stored.
  - [ ] AC3 — Given two concurrent appends with the same expected version, when executed in
    parallel transactions, then exactly one succeeds and the other gets `ConcurrencyConflict`.
  - [ ] AC4 — Given a new stream, when appending with `expected_version=0`, then versions start
    at 1.
  - [ ] AC5 — Given an append, when stored, then every envelope field of Constitution §12.1 is
    persisted (actor, correlation, causation, meta).
- **Tasks:**
  - [ ] Define the `EventStore` Protocol in `application/ports.py`.
  - [ ] Implement `PostgresEventStore.append` with SQLAlchemy Core `insert`.
  - [ ] Map the unique violation to `ConcurrencyConflict`.
- **Tests:** integration tests incl. parallel transactions (anyio task group).
- **Done when:** all AC green.

#### US-04.05 — Load streams and read all from a position

- [ ] **US-04.05 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the application, I want to load one aggregate's events and to read the global
  log from a position, so that aggregates can be rebuilt and projections/clients can catch up.
- **Acceptance criteria:**
  - [ ] AC1 — Given a stream, when loaded, then events come back ordered by
    `aggregate_version` with their stored metadata.
  - [ ] AC2 — Given `read_all(after_position, limit)`, when called, then it returns at most
    `limit` events with `global_position > after_position` in ascending order and the next
    position.
  - [ ] AC3 — Given an `event_id`, when resolved, then its `global_position` is returned (used
    by WebSocket resume).
  - [ ] AC4 — Given an unknown stream, when loaded, then an empty sequence is returned.
- **Tasks:**
  - [ ] Implement `load_stream`, `read_all`, `position_of`.
- **Tests:** integration tests with 1 000 seeded events (pagination correctness).
- **Done when:** all AC green.

#### US-04.06 — Event serialization and upcaster registry

- [ ] **US-04.06 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a backend developer, I want typed events serialized and deserialized through a
  registry with upcasters, so that event schemas can evolve without rewriting history.
- **Acceptance criteria:**
  - [ ] AC1 — Given a registered event class, when serialized, then the payload is JSON with
    `snake_case` keys and `type`/`version` columns set from the class.
  - [ ] AC2 — Given a stored `v1` row and a registered `v1→v2` upcaster, when loaded, then the
    application receives a `v2` instance.
  - [ ] AC3 — Given an unknown `type`, when loaded, then a clear `UnknownEventType` error is
    raised (programmer error, never silently skipped).
  - [ ] AC4 — Given two upcasters `v1→v2`, `v2→v3`, when loading `v1`, then both apply in order.
- **Tasks:**
  - [ ] `infrastructure/event_store/registry.py` and `upcasters.py`.
  - [ ] Test-only sample events.
- **Tests:** unit tests (no DB) + one integration round trip.
- **Done when:** registry used by the adapter.

### D04.3 — Unit of Work & projections

#### US-04.07 — Unit of Work with post-commit publication

- [ ] **US-04.07 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As a command handler, I want one Unit of Work that appends events and updates
  projections in a single transaction and publishes events only after commit, so that state and
  notifications are always consistent.
- **Acceptance criteria:**
  - [ ] AC1 — Given a handler appending events, when `commit()` succeeds, then events and
    projection rows are both visible and subscribers receive the events after commit.
  - [ ] AC2 — Given a projector raising an exception, when committing, then the transaction is
    rolled back: no events, no projection changes, no publication.
  - [ ] AC3 — Given a `ConcurrencyConflict`, when the handler retries (≤ 3 times by reloading),
    then a later attempt can succeed; after 3 failures the conflict is returned.
  - [ ] AC4 — Given the UoW used outside `async with`, when called, then it raises a programmer
    error.
- **Tasks:**
  - [ ] `UnitOfWork` Protocol and `SqlAlchemyUnitOfWork`.
  - [ ] Retry helper for handlers.
- **Tests:** integration tests for AC1–AC3; unit test for AC4 with fakes.
- **Done when:** used by a sample handler in tests.

#### US-04.08 — Projector framework with checkpoints and idempotency

- [ ] **US-04.08 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As a backend developer, I want projectors declared as handlers per event type with
  checkpoints, so that read models are easy to write and safe to replay.
- **Acceptance criteria:**
  - [ ] AC1 — Given a projector with handlers for some event types, when an unrelated event is
    committed, then the projector ignores it and its checkpoint still advances.
  - [ ] AC2 — Given the same event applied twice (replay), when processed, then the projection
    state is unchanged after the second time (idempotent by position).
  - [ ] AC3 — Given `projection_checkpoints`, when a projector processes an event, then its
    last position is stored in the same transaction.
  - [ ] AC4 — Given the projector registry, when the app starts, then every projector is logged
    with its name and handled types at `info`.
- **Tasks:**
  - [ ] `Projector` base class and handler decorator.
  - [ ] Registry and checkpoint repository.
- **Tests:** unit tests with an in-memory projection; integration test for checkpoints.
- **Done when:** a sample projector works end to end in tests.

#### US-04.10 — In-process event bus for post-commit subscribers

- [ ] **US-04.10 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a developer of realtime and orchestration features, I want to subscribe to
  committed events in-process, so that the WebSocket gateway and the Orchestrator react without
  polling.
- **Acceptance criteria:**
  - [ ] AC1 — Given a subscriber, when events are committed, then it receives them in commit
    order with their global positions.
  - [ ] AC2 — Given a slow subscriber, when events arrive, then other subscribers are not
    delayed (bounded queue per subscriber; overflow marks it `lagging`).
  - [ ] AC3 — Given a subscriber raising, when notified, then the error is logged and other
    subscribers still receive the event.
  - [ ] AC4 — Given app shutdown, when the lifespan ends, then subscriber tasks stop cleanly.
- **Tasks:**
  - [ ] `EventSubscriber` port; `infrastructure/bus.py` with anyio memory object streams.
  - [ ] Lifespan integration.
- **Tests:** unit tests with fake subscribers.
- **Done when:** the UoW publishes through the bus.

### D04.4 — Rebuild job

#### US-04.09 — Rebuild-projections job

- [ ] **US-04.09 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As an operator, I want to rebuild all projections from the event log with one
  command, so that read models can be fixed or reshaped safely.
- **Acceptance criteria:**
  - [ ] AC1 — Given `docker compose --profile admin run --rm rebuild-projections`, when run,
    then every projection table is truncated, checkpoints reset, all events replayed in
    position order, and a summary (events, duration, per projector) is logged.
  - [ ] AC2 — Given a seeded event log, when projections built incrementally are compared with
    rebuilt ones, then they are identical row by row.
  - [ ] AC3 — Given `core` running, when the job starts, then it refuses unless `--force` is
    passed (documented in DOCKER.md §6).
  - [ ] AC4 — Given a projector failure mid-rebuild, when it happens, then the job exits
    non-zero with a clear message.
- **Tasks:**
  - [ ] CLI entrypoint `python -m virtual_office.infrastructure.projections.rebuild`.
  - [ ] Compose job wiring and DOCKER.md row.
  - [ ] Equality test helper.
- **Tests:** integration equality test (AC2).
- **Done when:** job documented and tested.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP04 closing: Event store & persistence`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; coverage thresholds met.
- [ ] POSTGRES.md and skill `tracing-events` updated with any deviation.
- [ ] `docker compose up` still healthy; migrations run in jobs only.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Same-transaction projections become slow as projections grow | Measure in WP24; option to move to async projectors via ADR |
| Trigger blocks a legitimate migration | Migrations disable the trigger explicitly inside the migration, documented |
| Bus overflow loses notifications | Subscribers resync from the event store using positions (WebSocket `resync`) |

## 7. Blockers

None.

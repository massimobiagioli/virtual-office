# Virtual Office — PostgreSQL Guide

| Field   | Value                                                                                  |
| ------- | -------------------------------------------------------------------------------------- |
| Scope   | The `postgres` service, databases, roles, schema design, event store, projections, migrations, SQLAlchemy usage, backups |
| Related | [STACK.md](STACK.md) §7 · [BACKEND.md](BACKEND.md) · [DOCKER.md](DOCKER.md) · [CONSTITUTION.md](CONSTITUTION.md) Article XII · skill `tracing-events` |

---

## 1. Service

| Item          | Standard |
| ------------- | -------- |
| Image         | `postgres:<version from STACK.md>-trixie@sha256:<digest>` |
| Volume        | `pgdata:/var/lib/postgresql` |
| Port          | `5432` internal only; dev overlay publishes `127.0.0.1:5432` |
| Superuser     | `postgres`, password from `VO_POSTGRES_PASSWORD` — used **only** by init scripts and backups |
| Init scripts  | `infra/postgres/initdb/*.sh` mounted read-only into `/docker-entrypoint-initdb.d/` |
| Healthcheck   | `["CMD-SHELL", "pg_isready -U postgres -d postgres"]`, interval 5 s |
| Settings      | Passed as `command: ["postgres", "-c", "key=value", …]` (no custom `postgresql.conf` file) |

### 1.1 Server settings (base)

| Setting                       | Value          | Why |
| ----------------------------- | -------------- | --- |
| `timezone`                    | `UTC`          | Constitution: UTC everywhere |
| `log_min_duration_statement`  | `250ms`        | Surface slow queries |
| `log_line_prefix`             | `%m [%p] %u@%d ` | Readable logs on stdout |
| `shared_buffers`              | `256MB`        | Local single-node default |
| `max_connections`             | `100`          | Pools are small (§6) |
| `idle_in_transaction_session_timeout` | `30s`  | Never hold locks by mistake |
| `statement_timeout`           | set per role (§2) | |

---

## 2. Databases and roles

**One database per service** (STACK.md §2.1). Created by the init scripts:

| Database  | Owner role (DDL, migrations) | Runtime role (DML)  | Used by |
| --------- | ---------------------------- | ------------------- | ------- |
| `core`    | `core_owner`                 | `core_app`          | `core`, `migrate-core`, `rebuild-projections` |
| `catalog` | `catalog_owner`              | `catalog_app`       | `agents-catalog`, `migrate-catalog`, `catalog-seed` |

Rules:

1. Runtime roles **cannot** create or alter objects; they get `SELECT, INSERT, UPDATE, DELETE`
   on projection tables and **only `SELECT, INSERT`** on `event_store.events` (append-only by
   permission, Constitution §12.1).
2. Migrations run as the owner role in the one-off `migrate-*` jobs; services never run DDL.
3. `ALTER DEFAULT PRIVILEGES` in the init scripts grants runtime privileges on future tables
   per schema.
4. Runtime roles: `statement_timeout = '5s'`, `lock_timeout = '2s'`. Owner roles: no statement
   timeout (long migrations allowed).
5. `public` schema: `REVOKE CREATE ON SCHEMA public FROM PUBLIC`; application objects never
   live in `public`.
6. Passwords come from env (`VO_CORE_DB_PASSWORD`, `VO_CORE_DB_OWNER_PASSWORD`, …); never
   committed.

---

## 3. Schemas (core database)

| Schema         | Content |
| -------------- | ------- |
| `event_store`  | `events`, `snapshots`, `projection_checkpoints` |
| `projection`   | Read models: `board_cards`, `projects`, `agents`, `notes`, `adrs`, `work_log`, `chat_messages`, … |
| `runtime`      | `agent_jobs`, `agent_runs` (transcripts with retention), `diagnostics` (rejected commands) |

The catalog database uses schema `catalog` (role definitions, prompts, characters, eval sets).

---

## 4. Naming and types

| Topic            | Standard |
| ---------------- | -------- |
| Identifiers      | `snake_case`, lowercase, no quotes; tables **plural** (`board_cards`), columns singular |
| Primary keys     | `id` (or natural key when stable, e.g. `card_id` text `SHOP-12`) |
| IDs              | ULIDs stored as `uuid` (128-bit, sortable); converted at the infrastructure boundary |
| Timestamps       | `timestamptz` only, column suffix `_at` (`occurred_at`, `created_at`) |
| Text             | `text` + `CHECK` constraints for length; no `varchar(n)` |
| Enums            | `text` + `CHECK (col IN (...))` (easier to migrate than `CREATE TYPE … AS ENUM`) |
| JSON             | `jsonb` only for event payload/meta and genuinely schemaless data; never for relational data |
| Money            | `numeric(12,6)` for LLM costs in USD |
| Booleans         | `boolean NOT NULL DEFAULT false`, names `is_`/`has_` prefixed |
| Nullability      | `NOT NULL` by default; nullable only when absence is meaningful |

### 4.1 Constraint naming (SQLAlchemy `MetaData(naming_convention=…)`)

```python
NAMING_CONVENTION = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
}
```

---

## 5. Event store

```sql
CREATE TABLE event_store.events (
    global_position   bigint GENERATED ALWAYS AS IDENTITY,
    event_id          uuid        NOT NULL,
    aggregate_type    text        NOT NULL,
    aggregate_id      text        NOT NULL,
    aggregate_version integer     NOT NULL CHECK (aggregate_version > 0),
    type              text        NOT NULL,
    version           smallint    NOT NULL CHECK (version > 0),
    occurred_at       timestamptz NOT NULL,
    actor             jsonb       NOT NULL,
    correlation_id    uuid        NOT NULL,
    causation_id      uuid,
    payload           jsonb       NOT NULL,
    meta              jsonb       NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT pk_events PRIMARY KEY (global_position),
    CONSTRAINT uq_events_event_id UNIQUE (event_id),
    CONSTRAINT uq_events_aggregate_type_aggregate_id_aggregate_version
        UNIQUE (aggregate_type, aggregate_id, aggregate_version)
);
CREATE INDEX ix_events_correlation_id ON event_store.events (correlation_id);
CREATE INDEX ix_events_type_global_position ON event_store.events (type, global_position);
```

Rules:

1. **Append-only**: enforced by privileges (§2.1) and by a trigger that raises on `UPDATE` /
   `DELETE` (defense in depth, also blocks the owner role outside migrations).
2. **Optimistic concurrency**: the unique `(aggregate_type, aggregate_id, aggregate_version)`
   constraint; a violation maps to `ConcurrencyConflict` and the handler retries (≤ 3).
3. `global_position` gives a total order for projections and for the WebSocket `lastEventId`
   resume (the client receives `event_id`; the server maps it to the position).
4. Payloads are serialized from Pydantic with `mode="json"` (camelCase aliases **not** used
   in storage: stored keys are `snake_case`).
5. **Snapshots** (optional per aggregate) in `event_store.snapshots` keyed by
   `(aggregate_type, aggregate_id, aggregate_version)`; always rebuildable, never authoritative.

---

## 6. Access from Python (SQLAlchemy 2.1 async + asyncpg)

1. One `AsyncEngine` per process, created in the app lifespan from `VO_DATABASE_URL`
   (`postgresql+asyncpg://…`), disposed on shutdown.
2. Pool: `pool_size=5`, `max_overflow=5`, `pool_pre_ping=True`, `pool_recycle=1800`.
3. `async_sessionmaker(expire_on_commit=False)`; sessions are owned by the **Unit of Work**
   (BACKEND.md §6) — never created in routers or tools.
4. **Event store** uses SQLAlchemy **Core** (`insert`, `select`) for explicit SQL; projections
   may use the ORM with typed `Mapped[...]` declarative models.
5. Isolation level `READ COMMITTED` (default) + optimistic concurrency. `SERIALIZABLE` is not
   used.
6. Append + projection updates happen in **one transaction** (Constitution §15.4).
7. No lazy loading in async code: relationships use `lazy="raise"`; load explicitly with
   `selectinload`.
8. No raw SQL strings with interpolation; use bound parameters (`text()` with params only for
   migrations or reporting queries).

---

## 7. Migrations (Alembic)

1. One Alembic environment per service (`services/<service>/alembic/`), async template, using
   the same `MetaData` and naming convention.
2. File naming: `YYYYMMDD_HHMM_<slug>.py` (set `file_template` in `alembic.ini`).
3. `alembic revision --autogenerate` is a **starting point**; every migration is reviewed and
   edited by hand (check types, constraints, indexes, data migrations).
4. Every migration has a working `downgrade()` for local development; production-like
   environments only move forward.
5. **Expand → migrate → contract** for breaking changes: add new structure, backfill, switch
   code, remove old structure in a later release.
6. Migrations never modify `event_store.events` rows. Event shape changes are handled by
   **upcasters** in code (skill `tracing-events`).
7. Projection schema changes may be handled by dropping and **rebuilding** the projection
   (`rebuild-projections` job) instead of complex data migrations.
8. Integration tests run all migrations up and down on a fresh testcontainers database.

---

## 8. Indexing and performance

- Every foreign key has an index. Every query used by an API endpoint has a supporting index
  (checked with `EXPLAIN` in the PR when adding a new query).
- Cursor pagination uses `(occurred_at, id)` or `global_position`; never `OFFSET`.
- Keep projection tables narrow and purpose-built per screen (board, logbook, agent card).
- `jsonb` columns get GIN indexes only when queried by key (e.g. Logbook free-text search uses
  a generated `tsvector` column instead).

---

## 9. Testing

- Integration tests use **testcontainers** with the same image tag as compose (read from one
  constant/env so they never diverge).
- One database per test session; each test runs inside a transaction rolled back at the end,
  except migration tests and tests of commit behavior (they use a fresh database).
- Never mock SQLAlchemy; unit tests use in-memory fakes of the application ports instead
  (BACKEND.md §11).

---

## 10. Backup and restore

| Task       | How |
| ---------- | --- |
| Backup     | `docker compose --profile backup run --rm backup` → `pg_dump --format=custom` of `core` and `catalog` into the `backups` volume, file name `<db>-<UTC timestamp>.dump` |
| Restore    | `pg_restore --clean --if-exists` into a stopped stack (documented script `infra/postgres/restore.sh`) |
| Retention  | Keep the last 14 backups (pruned by the backup job) |

Events are the source of truth: a restore of `event_store` followed by `rebuild-projections`
recreates every read model.

---

## 11. Review checklist (Postgres)

```
- [ ] New tables in the right schema, plural snake_case names, NOT NULL by default
- [ ] Constraints follow the naming convention; FKs indexed
- [ ] Runtime role privileges granted (and nothing more)
- [ ] Migration reviewed by hand, downgrade works, expand/contract for breaking changes
- [ ] No UPDATE/DELETE on events; event shape changes via upcasters
- [ ] Append + projections in one transaction; no lazy loading in async code
- [ ] Integration tests run migrations on a fresh container
```

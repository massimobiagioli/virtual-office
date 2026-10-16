# WP06 — Board API & Realtime

| Field        | Value |
| ------------ | ----- |
| Milestone    | M1 — Kickstart |
| Status       | READY |
| Depends on   | WP04, WP05 |
| Enables      | WP08, WP09, WP10, WP14 |
| Constitution | §4.3.1–4.3.2, §8.9 (human overrides), §15.4, §15.9, §15.10, Appendix E (E1–E4 via API, E18) |
| Guides       | [BACKEND.md](../../.docs/BACKEND.md) §6–7, §11 · [FRONTEND.md](../../.docs/FRONTEND.md) §4–5 · [POSTGRES.md](../../.docs/POSTGRES.md) §4, §6, §8 |
| Skills       | `tracing-events`, `enforcing-kanban-workflow`, `delivering-features`, `writing-adrs` |
| Estimate     | 42 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-06.01 — Command bus and handler pattern with diagnostics (5 pts)
- [ ] US-06.02 — Project endpoints (3 pts)
- [ ] US-06.03 — Card command endpoints and generic command endpoint (5 pts)
- [ ] US-06.04 — Problem details and correlation middleware (2 pts)
- [ ] US-06.05 — Office bootstrap at first start (2 pts)
- [ ] US-06.06 — Project list projection and query (2 pts)
- [ ] US-06.07 — Board projection and query (3 pts)
- [ ] US-06.08 — Card detail projection and query (3 pts)
- [ ] US-06.09 — Staff projection (minimal) and query (2 pts)
- [ ] US-06.10 — WebSocket gateway: hello, delta, resync (5 pts)
- [ ] US-06.11 — WebSocket heartbeat, ordering and backpressure (3 pts)
- [ ] US-06.12 — OpenAPI publication including WebSocket schemas (2 pts)
- [ ] US-06.13 — Frontend API client, realtime client and store reducers (5 pts)

## 1. Objective

Expose the Kanban domain to the outside world: command handlers that load, decide and append
in one transaction; REST endpoints and queries backed by projections; a WebSocket stream of
committed events with resume; OpenAPI as the contract; and the frontend's typed client, realtime
client and Pinia reducers. After WP06 any client can operate a board and see changes live.

## 2. Scope

**In:** application handlers for every Kanban command; office bootstrap; projections
`projects`, `board_cards`, `card_details`, `agents` (minimal); REST routers; problem details;
correlation ids; WebSocket gateway; OpenAPI export; TS generation; `api/client.ts`,
`api/realtime.ts`; Pinia stores `kanban` and `staff` with `apply(event)`.

**Out:** UI windows (WP08), Logbook projection (WP10), staff customization endpoints (WP09).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D06.1 | Commands & REST | Handlers following BACKEND.md §6 for all Kanban commands, REST endpoints, problem details, correlation, bootstrap | API integration tests E1–E4 through HTTP; diagnostics rows for rejections | US-06.01 – US-06.05 |
| D06.2 | Projections & queries | Read models and query endpoints for project list, board, card detail, staff | Query tests; rebuild equality holds | US-06.06 – US-06.09 |
| D06.3 | WebSocket gateway | `/ws` with hello/delta/resync, heartbeat, ordered delivery after commit, bounded queues | E18 integration test; latency measurement ≤ 500 ms p95 locally | US-06.10, US-06.11 |
| D06.4 | Contract & client | OpenAPI incl. WS models; generated TS types; typed REST client; realtime client; Pinia reducers | Drift check green; reducer unit tests | US-06.12, US-06.13 |

## 4. User stories

### D06.1 — Commands & REST

#### US-06.01 — Command bus and handler pattern with diagnostics

- [ ] **US-06.01 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As a backend developer, I want every command to go through one bus with the same
  handler shape, so that authorization, decision, persistence and diagnostics are uniform.
- **Acceptance criteria:**
  - [ ] AC1 — Given any Kanban command, when dispatched with an actor, then the handler loads
    the needed aggregates, checks `ActorPolicy`, calls the domain, appends with expected
    versions and commits via the UoW (BACKEND.md §6 shape).
  - [ ] AC2 — Given a domain error, when returned, then no event is stored and a row is written
    to `runtime.diagnostics` with command type, actor, error code, correlation id.
  - [ ] AC3 — Given a pull, when handled, then the **project** stream is appended (a
    `TodoSlotTaken`-style project event or version bump) so that concurrent pulls conflict;
    with two parallel pulls for the last slot, exactly one succeeds (E1 under concurrency).
  - [ ] AC4 — Given a `ConcurrencyConflict`, when it happens, then the handler retries ≤ 3 times
    before returning the conflict.
- **Tasks:**
  - [ ] `application/commands/` modules per command; `CommandBus` dispatching by type.
  - [ ] Diagnostics repository.
  - [ ] Project-level pull serialization event (Appendix B row added).
- **Tests:** unit tests with fakes; integration test for concurrent pulls.
- **Done when:** all Kanban commands dispatchable.

#### US-06.02 — Project endpoints

- [ ] **US-06.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the frontend, I want REST endpoints to create and manage projects.
- **Acceptance criteria:**
  - [ ] AC1 — `POST /api/projects` with `{key, name, description?}` → 201 with the project DTO;
    duplicate key → 409 problem with `code=ProjectKeyAlreadyUsed`.
  - [ ] AC2 — `PATCH /api/projects/{key}` renames; `POST /api/projects/{key}/archive` and
    `/restore` archive/restore; `PATCH /api/projects/{key}/settings` changes `todoLimit`.
  - [ ] AC3 — All responses are `ApiModel` DTOs in camelCase with explicit `operation_id`s.
  - [ ] AC4 — Validation errors → 422 problem details listing fields.
- **Tasks:** router `api/routers/projects.py`; DTOs in `api/schemas/projects.py`.
- **Tests:** API tests with httpx `AsyncClient` against the app with a test DB.
- **Done when:** all AC green.

#### US-06.03 — Card command endpoints and generic command endpoint

- [ ] **US-06.03 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the frontend, I want to send every card command over REST, so that the user can
  operate the board manually.
- **Acceptance criteria:**
  - [ ] AC1 — `POST /api/commands` accepts a discriminated union of all Kanban commands
    (`kind` field) and returns 202 with `{accepted: true, eventIds}` or a problem.
  - [ ] AC2 — Convenience endpoints exist for frequent actions (`POST /api/projects/{key}/cards`,
    `POST /api/cards/{id}/move`) and delegate to the same handlers.
  - [ ] AC3 — Given TODO full, when pulling via HTTP, then 409 with `code=WipLimitReached` and a
    human message (E1); TODO → DONE via HTTP → 409 `TransitionNotAllowed` (E4); assignee
    approving → 409 `ReviewerIsAssignee` (E3).
  - [ ] AC4 — Every accepted command responds within 50 ms p95 locally (excluding LLM).
- **Tasks:** router `api/routers/commands.py`, `cards.py`; DTO union.
- **Tests:** API tests E1, E3, E4; timing assertion in a benchmark test (not flaky: p95 over 200).
- **Done when:** all AC green.

#### US-06.04 — Problem details and correlation middleware

- [ ] **US-06.04 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As an operator and a frontend developer, I want consistent errors and a correlation
  id on every request, so that errors are explainable and traceable.
- **Acceptance criteria:**
  - [ ] AC1 — Every error response is `application/problem+json` with `type`, `title`,
    `status`, `detail`, `code`, `correlationId`.
  - [ ] AC2 — `X-Correlation-Id` is accepted from the request or generated, returned in the
    response, and bound to structlog context and to events' `correlation_id`.
  - [ ] AC3 — Unhandled exceptions → 500 problem without stack traces; full trace in logs.
- **Tasks:** `api/errors.py`, middleware, domain error → status mapping table.
- **Tests:** API tests per case.
- **Done when:** all routers use it.

#### US-06.05 — Office bootstrap at first start

- [ ] **US-06.05 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want the default staff to exist automatically, so that I can assign
  cards on first use.
- **Acceptance criteria:**
  - [ ] AC1 — Given an empty event store, when `core` starts, then `InitializeOffice` is
    dispatched by the `system` actor and `OfficeInitialized` is stored once.
  - [ ] AC2 — Given restarts, when `core` starts again, then no duplicate initialization occurs.
  - [ ] AC3 — Given two `core` processes starting simultaneously (test), then only one
    initialization succeeds (concurrency on the office stream).
- **Tasks:** lifespan hook calling the handler.
- **Tests:** integration tests.
- **Done when:** default staff visible via US-06.09.

### D06.2 — Projections & queries

#### US-06.06 — Project list projection and query

- [ ] **US-06.06 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want a list of projects with counters, so that I see the health of
  all work at a glance (Constitution §4.3.1).
- **Acceptance criteria:**
  - [ ] AC1 — `GET /api/projects` returns key, name, archived, counts per column, `todo`
    `{count, limit}`, last activity time, health (`flowing`/`blocked`/`error`).
  - [ ] AC2 — Archived projects excluded unless `?includeArchived=true`.
  - [ ] AC3 — Counters update in the same transaction as the card events.
- **Tasks:** table `projection.projects`; projector; query.
- **Tests:** projector unit tests; API test.
- **Done when:** all AC green.

#### US-06.07 — Board projection and query

- [ ] **US-06.07 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the frontend, I want one call that returns a whole board ordered by column and
  rank, so that the board window renders fast.
- **Acceptance criteria:**
  - [ ] AC1 — `GET /api/projects/{key}/board` returns columns in order with card summaries
    (id, type, title, priority, estimate, assignee id, rework count, blocked, rank) and
    `lastEventId`.
  - [ ] AC2 — Board for 200 cards returns in < 50 ms locally.
  - [ ] AC3 — Rebuild equality test covers this projection.
- **Tasks:** table `projection.board_cards` with indexes `(project_id, column, rank)`.
- **Tests:** projector tests; API test; performance test.
- **Done when:** all AC green.

#### US-06.08 — Card detail projection and query

- [ ] **US-06.08 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want the full card in one call, so that the Card Detail window can
  show everything (Constitution §4.3.2).
- **Acceptance criteria:**
  - [ ] AC1 — `GET /api/cards/{id}` returns all Appendix A card fields incl. tasks,
    deliverables, reviews, dependencies, labels, `sourceNoteId`, `adrIds`, `version`.
  - [ ] AC2 — Unknown id → 404 problem.
  - [ ] AC3 — Includes `allowedTransitions` for the requesting actor (computed by the domain
    policy) so the UI can enable/disable controls.
- **Tasks:** table `projection.card_details` (jsonb for nested lists where appropriate).
- **Tests:** projector and API tests.
- **Done when:** all AC green.

#### US-06.09 — Staff projection (minimal) and query

- [ ] **US-06.09 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the frontend, I want the list of agents with roles and status, so that the user
  can pick an assignee.
- **Acceptance criteria:**
  - [ ] AC1 — `GET /api/agents` returns id, role, slot, name, faceId, enabled, competence tags,
    `domainStatus`, `currentCardId`, `queue`.
  - [ ] AC2 — `domainStatus` and `currentCardId` update on `WorkStarted`, `WorkSubmitted`,
    `WorkHandedBack`, `CardApproved` (reviewer), `CardRejected`.
- **Tasks:** table `projection.agents`; projector.
- **Tests:** projector and API tests.
- **Done when:** all AC green.

### D06.3 — WebSocket gateway

#### US-06.10 — WebSocket gateway: hello, delta, resync

- [ ] **US-06.10 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As a connected client, I want to receive every committed event in order and catch
  up after a disconnect, so that my screen always matches the server (E18).
- **Acceptance criteria:**
  - [ ] AC1 — On connect, the client sends `{"v":1,"type":"hello","lastEventId":…}`; if
    `lastEventId` is known and ≤ 1 000 events behind, the server sends those events in order,
    then live events.
  - [ ] AC2 — If unknown or > 1 000 behind, the server sends `{"type":"resync"}` and then live
    events; the client refetches projections.
  - [ ] AC3 — Events are sent only after commit, as `ApiModel` messages with `eventId`, `type`,
    `occurredAt`, `actor`, `aggregate`, `payload` (camelCase).
  - [ ] AC4 — E18: client disconnected while 20 events happen → on reconnect receives exactly
    those 20 → its board equals the server projection.
- **Tasks:** `api/ws/gateway.py`, message models, bus subscription.
- **Tests:** integration test with two clients (httpx-ws or Starlette test client).
- **Done when:** all AC green.

#### US-06.11 — WebSocket heartbeat, ordering and backpressure

- [ ] **US-06.11 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As an operator, I want connections to be healthy and bounded, so that one slow tab
  never harms the server.
- **Acceptance criteria:**
  - [ ] AC1 — Server sends `heartbeat` every 15 s; client absence of pong for 45 s closes the
    connection.
  - [ ] AC2 — Per-connection queue bounded (e.g. 1 000 messages); on overflow the server sends
    `resync` and drops the backlog.
  - [ ] AC3 — Messages on one connection are strictly ordered by global position.
  - [ ] AC4 — Event → client latency measured in tests: p95 ≤ 500 ms with 5 clients and 50
    events/s locally.
- **Tasks:** queue, heartbeat task, latency test harness.
- **Tests:** integration tests.
- **Done when:** all AC green.

### D06.4 — Contract & client

#### US-06.12 — OpenAPI publication including WebSocket schemas

- [ ] **US-06.12 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a frontend developer, I want every REST DTO and WebSocket message in OpenAPI, so
  that TypeScript types are generated, not hand-written.
- **Acceptance criteria:**
  - [ ] AC1 — `/api/openapi.json` contains all routers with stable `operationId`s and all WS
    message models under `components.schemas`.
  - [ ] AC2 — `python -m virtual_office.api.export_openapi` writes the schema deterministically
    (sorted keys) for CI.
  - [ ] AC3 — The drift check of WP03 passes with regenerated `schema.d.ts`.
- **Tasks:** custom `openapi()` hook; exporter.
- **Tests:** snapshot test of the schema (contract test).
- **Done when:** all AC green.

#### US-06.13 — Frontend API client, realtime client and store reducers

- [ ] **US-06.13 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As a frontend developer, I want a typed REST client, a resilient realtime client
  and stores that apply events, so that windows only bind to state.
- **Acceptance criteria:**
  - [ ] AC1 — `api/client.ts` uses `openapi-fetch` with generated `paths`; errors mapped to a
    typed `ProblemError` with `code`.
  - [ ] AC2 — `api/realtime.ts` implements hello/delta/resync, heartbeat, exponential backoff
    1 s → 30 s, and exposes connection state (`connected`/`reconnecting`/`offline`).
  - [ ] AC3 — `useKanbanStore` loads projects/board/card via REST and exposes `apply(event)`
    reducers for every card/project event; unit tests per event type.
  - [ ] AC4 — `useStaffStore` loads agents and applies agent-affecting events.
  - [ ] AC5 — No UI state changes optimistically for domain data; the store changes only on
    events or refetch.
- **Tasks:** clients, stores, `api/types.ts` friendly re-exports, `api/error-messages.ts`.
- **Tests:** Vitest unit tests with mocked fetch/WebSocket.
- **Done when:** all AC green.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP06 closing: Board API & realtime`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; application coverage ≥ 90 %.
- [ ] OpenAPI contract test and drift check green; Constitution §15.9 table updated if paths
  changed.
- [ ] E1, E3, E4 pass through HTTP; E18 passes through WebSocket.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Concurrent pulls exceed the limit | Project-stream serialization (US-06.01 AC3) with a concurrency integration test |
| WebSocket latency spikes under load | Bounded queues, resync on overflow, latency test in CI |
| DTO drift between Python and TS | Generated types + drift check |

## 7. Blockers

None.

---
name: tracing-events
description: Event sourcing and traceability conventions for Virtual Office - event envelope, naming, versioning and upcasting, append with optimistic concurrency, projections and rebuilds, work log sentences, LLM job and tool-call tracing, realtime broadcast. Use when adding or changing a domain event, a projection, the event store, the Logbook, or anything that must be audited.
---

# Tracing events

Authoritative source: Constitution Article XII, §15.4, §15.10, Appendices A and B. Storage
details: `.docs/POSTGRES.md` §5.

## Adding a new event — checklist

```
- [ ] Name: past tense, PascalCase, domain language (e.g. CardRejected) — check Appendix B first
- [ ] Payload Pydantic model (frozen) in core/domain/<context>/events.py with `version: 1`, exported in OpenAPI components
- [ ] Emitted only by a domain decision function (never by adapters/UI)
- [ ] Frontend types regenerated from OpenAPI (no drift)
- [ ] Projection handlers updated (board, agent, work log, office if relevant)
- [ ] Work log sentence template added (English, "<actor> <verb> <object>: <reason>")
- [ ] If it moves or changes an agent's work/location → choreography added (building-office-scene)
- [ ] Constitution Appendix B updated (PATCH amendment + Amendment Log line)
- [ ] Tests: decision emits it; projection applies it; rebuild from scratch yields same state
```

## Envelope (never omit fields; Python `snake_case`, JSON `camelCase`)

`eventId` (ULID), `type`, `version`, `occurredAt` (UTC ms), `actor`, `aggregate {type,id}`,
`aggregateVersion`, `correlationId`, `causationId`, `payload`, `meta`
(`reason`, `via`, `model`, `promptVersion`, `tokensIn`, `tokensOut`, `costUsd`, `durationMs`).

- `correlationId` groups everything that started from the same trigger (e.g. one note).
- `causationId` is the event/command that directly caused this one.

## Immutability and versioning

- Events are never updated or deleted. Corrections are new events (`CardEdited`, `EventAnnotated`).
- Changing a payload shape → new `version`, plus an **upcaster** `vN → vN+1` with tests. Old
  events stay as stored.

## Append

- Load aggregate → decide → append with expected `aggregateVersion` in one Postgres transaction
  together with projection updates (v1). On `ConcurrencyConflict` reload and retry ≤ 3 times.
- Broadcast to WebSocket **after** commit only.

## Projections

- Pure reducers `(projection_state, event) → projection_state`.
- Event store: Postgres table `events`, unique `(aggregate_type, aggregate_id,
  aggregate_version)`; `UPDATE`/`DELETE` revoked for the runtime DB role.
- Must be rebuildable: the one-off `rebuild-projections` admin container drops and replays; a test asserts equality
  with incrementally built projections.
- Idempotent by `eventId` (store last applied event per projection).

## LLM and tool tracing

- `AgentJobStarted/Progressed/Completed/Failed` carry model, prompt version, usage, cost,
  duration.
- `AgentToolCalled` carries tool name, **sanitized** args (no secrets, file contents
  truncated to 2 KB), result summary, duration.
- Full transcripts go to `agent_runs` storage (retention 90 days), linked by `jobId`.

## Redaction

Run the secret redactor (a structlog processor) on every `meta`, tool arg and log line before
persisting. Never log API keys or env values.

## Realtime

Client `hello {lastEventId}` → server sends delta (≤ 1 000 events) or `resync`. Messages are
versioned `v: 1`. Scenario E18 covers reconnects.

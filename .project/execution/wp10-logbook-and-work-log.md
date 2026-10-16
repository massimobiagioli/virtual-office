# WP10 — Logbook & Work Log

| Field        | Value |
| ------------ | ----- |
| Milestone    | M2 — Workbench |
| Status       | READY |
| Depends on   | WP06 (events, diagnostics), WP08 (shell, card window), WP09 (agent names) |
| Enables      | WP18 (PM answers grounded in the log), WP24 (export) |
| Constitution | §4.3.7, Article XII (§12.2–12.3), §11.2 |
| Guides       | [BACKEND.md](../../.docs/BACKEND.md) §7 · [POSTGRES.md](../../.docs/POSTGRES.md) §8 · [FRONTEND.md](../../.docs/FRONTEND.md) |
| Skills       | `tracing-events`, `designing-amiga-ui`, `delivering-features`, `writing-adrs` |
| Estimate     | 28 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-10.01 — Sentence templates for every event type (3 pts)
- [ ] US-10.02 — Work-log projection (3 pts)
- [ ] US-10.03 — Rejected commands in the log (2 pts)
- [ ] US-10.04 — Logbook API with filters and cursor pagination (3 pts)
- [ ] US-10.05 — Free-text search (3 pts)
- [ ] US-10.06 — Export to JSON and Markdown (2 pts)
- [ ] US-10.07 — Logbook window (5 pts)
- [ ] US-10.08 — Live tail and accessibility (2 pts)
- [ ] US-10.09 — Card history tab (3 pts)
- [ ] US-10.10 — Agent activity in the Staff Room (2 pts)

## 1. Objective

Make every event readable by humans: a work-log projection that renders each event as an English
sentence with actor, verb, object and reason; a filterable, searchable, exportable Logbook API
and window; and per-card and per-agent histories — the foundation of traceability and of the
PM's grounded answers.

## 2. Scope

**In:** template registry with completeness test; `projection.work_log`; diagnostics in the log;
`GET /api/events`; search; export; Logbook window; card History tab; agent activity list.

**Out:** LLM transcripts viewer (WP15 links them), PM chat (WP18).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D10.1 | Work-log projection | One English sentence template per event type (completeness test), projection indexed by project/card/agent/time, rejected commands included | Completeness test; projector tests | US-10.01 – US-10.03 |
| D10.2 | Logbook API | Filters (project, card, agent, role, type, time range, text), cursor pagination, JSON/Markdown export | API tests; pagination property test | US-10.04 – US-10.06 |
| D10.3 | Logbook UI | Logbook window with filters and live tail; card History tab; agent activity | E2E filter + export flows | US-10.07 – US-10.10 |

## 4. User stories

### D10.1 — Work-log projection

#### US-10.01 — Sentence templates for every event type

- [ ] **US-10.01 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want each event described in plain English, so that I can read the
  office history like a diary.
- **Acceptance criteria:**
  - [ ] AC1 — A registry maps each event type to a template producing
    `{actor} ({role}) {verb} {object}: {reason}`; e.g. `Guru (QA) sent SHOP-12 back to TODO:
    "Missing null check on cart total"`.
  - [ ] AC2 — A completeness test fails if any registered event type lacks a template.
  - [ ] AC3 — Templates use the agent's name **at the time of the event** (rename-safe) and show
    the current name in a tooltip when different.
- **Tasks:** `application/worklog/templates.py`; tests.
- **Tests:** unit tests per template; completeness test.
- **Done when:** all AC green.

#### US-10.02 — Work-log projection

- [ ] **US-10.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the system, I want a work-log table optimized for reading, so that the Logbook is
  fast at any size.
- **Acceptance criteria:**
  - [ ] AC1 — `projection.work_log(position, event_id, occurred_at, project_key, card_id,
    agent_id, role, event_type, sentence, reason, actor_kind)` with indexes for each filter.
  - [ ] AC2 — Rebuild equality covers it.
  - [ ] AC3 — 100 000 rows: filtered page of 50 in < 50 ms locally.
- **Tasks:** migration, projector.
- **Tests:** projector and performance tests.
- **Done when:** all AC green.

#### US-10.03 — Rejected commands in the log

- [ ] **US-10.03 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want to see refused attempts too (e.g. an agent trying to break a
  rule), so that nothing relevant is hidden (Constitution P1).
- **Acceptance criteria:**
  - [ ] AC1 — Diagnostics rows appear in the Logbook as `refused` lines with the error message.
  - [ ] AC2 — A filter "Show refused attempts" (default on) toggles them.
- **Tasks:** union query or diagnostics projection.
- **Tests:** API test.
- **Done when:** all AC green.

### D10.2 — Logbook API

#### US-10.04 — Logbook API with filters and cursor pagination

- [ ] **US-10.04 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the frontend, I want to query the log with filters and stable pagination.
- **Acceptance criteria:**
  - [ ] AC1 — `GET /api/events?project=&card=&agent=&role=&type=&from=&to=&cursor=&limit=` returns
    `{items, nextCursor}` newest first.
  - [ ] AC2 — Cursor pagination is stable while new events arrive (cursor encodes position).
  - [ ] AC3 — Property test: paging through all pages returns every matching row exactly once.
- **Tasks:** router, query.
- **Tests:** API + Hypothesis pagination test.
- **Done when:** all AC green.

#### US-10.05 — Free-text search

- [ ] **US-10.05 completed** · **Points:** 3 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want to search the log by words (e.g. "null check").
- **Acceptance criteria:**
  - [ ] AC1 — `q=` parameter uses a generated `tsvector` column (English config) with GIN index.
  - [ ] AC2 — Results highlight matching terms (server returns ranges).
- **Tasks:** migration, query.
- **Tests:** integration tests.
- **Done when:** all AC green.

#### US-10.06 — Export to JSON and Markdown

- [ ] **US-10.06 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want to export the log, so that I can archive or share it.
- **Acceptance criteria:**
  - [ ] AC1 — `GET /api/events/export?format=json|markdown&<filters>` streams the result
    (`application/x-ndjson` raw events for JSON; Markdown human log).
  - [ ] AC2 — The UI offers the export through a visible link-styled button (download handled by
    the browser from the API response).
- **Tasks:** streaming endpoint.
- **Tests:** API tests.
- **Done when:** all AC green.

### D10.3 — Logbook UI

#### US-10.07 — Logbook window

- [ ] **US-10.07 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want a Logbook window to browse everything that happened.
- **Acceptance criteria:**
  - [ ] AC1 — Lines show time, face, name, role, sentence; clicking IDs opens cards/agents/ADRs.
  - [ ] AC2 — Filters panel (project, card, agent, role, type, time range, text, refused) with
    Amiga gadgets; filters reflected in the URL `/logbook?...`.
  - [ ] AC3 — Infinite scroll with Amiga scroller loads next pages.
- **Tasks:** `windows/logbook/`; Logbook icon enabled.
- **Tests:** component tests; E2E filter flow.
- **Done when:** all AC green.

#### US-10.08 — Live tail and accessibility

- [ ] **US-10.08 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want new lines to appear live without losing my scroll position.
- **Acceptance criteria:**
  - [ ] AC1 — When scrolled to top, new matching events appear live; otherwise a "n new lines"
    pill appears.
  - [ ] AC2 — New lines are announced politely to screen readers (rate-limited).
- **Tasks:** live merge in the store.
- **Tests:** component tests.
- **Done when:** all AC green.

#### US-10.09 — Card history tab

- [ ] **US-10.09 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want a card's full history inside its window.
- **Acceptance criteria:**
  - [ ] AC1 — Card Detail "History" tab lists the card's work-log lines (oldest first) with diffs
    for `CardEdited`.
  - [ ] AC2 — Lines linked to LLM runs show a "transcript" link placeholder (filled in WP15).
- **Tasks:** tab component.
- **Tests:** component tests; E2E.
- **Done when:** all AC green.

#### US-10.10 — Agent activity in the Staff Room

- [ ] **US-10.10 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want to see what an agent did recently.
- **Acceptance criteria:**
  - [ ] AC1 — The Staff Room detail shows the last 10 events of the agent with a link "Open in
    Logbook" (pre-filtered).
- **Tasks:** component.
- **Tests:** component test.
- **Done when:** all AC green.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP10 closing: Logbook & work log`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; template completeness test part of CI.
- [ ] Performance budget of US-10.02 met; axe zero violations.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Templates drift from events | Completeness test fails on missing templates |
| Large exports overload the server | Streaming responses with limits |
| Names change after events | Store the name at event time in the projection |

## 7. Blockers

None.

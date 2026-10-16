# WP17 — Orchestrator & Assignment

| Field        | Value |
| ------------ | ----- |
| Milestone    | M4 — Paula |
| Status       | READY |
| Depends on   | WP15, WP16, WP14 (visible choreographies) |
| Enables      | WP18, WP20, WP21, WP22 |
| Constitution | §5.3 (items 4–5, 8), §8.6–8.8, Article IX, §10.4, Appendix E (E2, E8, E11 groundwork) |
| Guides       | [BACKEND.md](../../.docs/BACKEND.md) §6, §8 · [PRINCIPLES.md](../../.docs/PRINCIPLES.md) |
| Skills       | `enforcing-kanban-workflow`, `authoring-office-agents`, `tracing-events`, `delivering-features`, `writing-adrs` |
| Estimate     | 34 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-17.01 — Orchestrator tick loop with pause and graceful shutdown (5 pts)
- [ ] US-17.02 — Realtime heartbeat of the office (1 pt)
- [ ] US-17.03 — Pull selection (3 pts)
- [ ] US-17.04 — Assignment scoring with explanation (3 pts)
- [ ] US-17.05 — PM pulls within one tick (3 pts)
- [ ] US-17.06 — Assignee pickup, rework priority and cross-project fairness (5 pts)
- [ ] US-17.07 — Reviewer pickup order (2 pts)
- [ ] US-17.08 — Stale DOING detection (2 pts)
- [ ] US-17.09 — Blocked-card SLA (3 pts)
- [ ] US-17.10 — Rework escalation (2 pts)
- [ ] US-17.11 — Budget thresholds in scheduling (2 pts)
- [ ] US-17.12 — Scheduling scenarios E2 and E8 (3 pts)

## 1. Objective

Make the office run by itself: an Orchestrator loop that, every tick, lets the PM fill free TODO
slots with the best Ready cards assigned to the most competent available agents (deterministic,
explained), lets agents pick up their next card or review, and detects anomalies (stale work,
blocked SLAs, rework loops, budgets) — always respecting pauses and the domain rules.

## 2. Scope

**In:** tick loop; heartbeat; pure selection and scoring; PM pull execution; pickup triggers for
executor and reviewer jobs (job kinds start in WP20–WP22); anomaly detection and events;
scenarios E2, E8.

**Out:** executor/reviewer job behavior (WP20–WP22); PM chat messages (WP18 consumes escalation
events).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D17.1 | Tick loop | Supervised loop every `VO_OFFICE_TICK_MS` (default 2 s) with ordered phases, pause, graceful shutdown, heartbeat | Fake-clock tests of phase order; shutdown test | US-17.01, US-17.02 |
| D17.2 | Selection & scoring | Pure selection (§9.2) and scoring (§9.3) with breakdown stored in `CardPulled`; PM pulls one card per free slot within one tick | Unit/property tests; E2 | US-17.03 – US-17.05 |
| D17.3 | Pickup rules | Agents start their next card (rework first, P0, oldest), fairness across projects; reviewers pick REVIEW cards FIFO with P0 first | Unit tests; integration with fake jobs | US-17.06, US-17.07 |
| D17.4 | Anomalies | Stale DOING, blocked SLA, rework escalation (3), budget thresholds → events for PM and UI | GWT + integration tests | US-17.08 – US-17.12 |

## 4. User stories

### D17.1 — Tick loop

#### US-17.01 — Orchestrator tick loop with pause and graceful shutdown

- [ ] **US-17.01 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want the office to advance on a steady heartbeat, so that work
  flows without anyone pressing buttons.
- **Acceptance criteria:**
  - [ ] AC1 — The Orchestrator runs in a task group started in the app lifespan; each tick runs
    phases in order: (1) user commands are already handled synchronously, (2) collect finished
    job results, (3) PM pulls per project, (4) assignee pickups, (5) reviewer pickups,
    (6) anomaly detection.
  - [ ] AC2 — If the office is paused, phases 3–6 are skipped; pause takes effect within one tick.
  - [ ] AC3 — A tick never overlaps the next; long ticks log a warning and the next tick starts
    immediately after.
  - [ ] AC4 — SIGTERM: stop scheduling new jobs, let running jobs checkpoint, exit within 10 s.
  - [ ] AC5 — Only one Orchestrator per database (advisory lock); a second `core` instance runs
    without it and logs that.
- **Tasks:** `application/orchestrator/loop.py`; advisory lock adapter.
- **Tests:** fake clock tests; shutdown test; lock test (integration).
- **Done when:** all AC green.

#### US-17.02 — Realtime heartbeat of the office

- [ ] **US-17.02 completed** · **Points:** 1 · **Priority:** Should · **ADR:** —
- **Story:** As the frontend, I want a lightweight `OfficeTicked` heartbeat, so that the title bar
  status stays fresh.
- **Acceptance criteria:**
  - [ ] AC1 — Each tick sends `officeTicked{busyAgents, inReview, runningJobs}` over WebSocket
    only (not persisted).
- **Tasks:** gateway message.
- **Tests:** unit test.
- **Done when:** title bar uses it.

### D17.2 — Selection & scoring

#### US-17.03 — Pull selection

- [ ] **US-17.03 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the PM, I want to choose the best Ready card for a free slot (Constitution §9.2).
- **Acceptance criteria:**
  - [ ] AC1 — `select_card(ready_cards)` orders by priority (P0 first), number of dependents
    (desc), rank, creation time; pure function.
  - [ ] AC2 — Only Ready cards (domain `is_ready`) are candidates.
  - [ ] AC3 — Property test: the selected card is never dominated by another candidate on the
    ordering keys.
- **Tasks:** `application/orchestrator/selection.py`.
- **Tests:** unit + Hypothesis.
- **Done when:** all AC green.

#### US-17.04 — Assignment scoring with explanation

- [ ] **US-17.04 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to know why a card went to a given agent.
- **Acceptance criteria:**
  - [ ] AC1 — `score(agent, card, context) = 3·competence + 2·availability + 1·continuity −
    1·load` exactly as §9.3, returning a breakdown object.
  - [ ] AC2 — Ties → least recently assigned agent.
  - [ ] AC3 — Fallback executors (§6.3) are scored but flagged; primary-role candidates win ties.
  - [ ] AC4 — `CardPulled` stores the breakdown; the Logbook sentence includes the main reason
    ("best competence match").
- **Tasks:** `application/orchestrator/scoring.py`.
- **Tests:** table-driven unit tests.
- **Done when:** all AC green.

#### US-17.05 — PM pulls within one tick

- [ ] **US-17.05 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want the PM to fill TODO as soon as a slot frees up (Constitution
  §8.6.5).
- **Acceptance criteria:**
  - [ ] AC1 — For each non-archived project with `count(TODO) < limit`, the PM issues one
    `PullCard` per free slot in priority order, as the PM actor, with templated `meta.reason`.
  - [ ] AC2 — No LLM call is needed for pulls (deterministic); the PM's `domainStatus` shows
    `planning` during the phase.
  - [ ] AC3 — No executors enabled → no pulls; a single `OfficeIdleNoExecutors` notice per
    change (consumed by WP18).
  - [ ] AC4 — Budget exhausted for a project → no pulls for it.
- **Tasks:** phase implementation.
- **Tests:** integration with fake clock and real DB.
- **Done when:** all AC green.

### D17.3 — Pickup rules

#### US-17.06 — Assignee pickup, rework priority and cross-project fairness

- [ ] **US-17.06 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As an agent, I want to start my next card automatically when I am free.
- **Acceptance criteria:**
  - [ ] AC1 — For each enabled, unpaused, idle executor with TODO cards assigned, the
    Orchestrator issues `StartWork` for the next card: rework cards first, then P0, then oldest
    assignment (§9.4), across all projects.
  - [ ] AC2 — After `WorkStarted`, the role's work job is enqueued (job kinds implemented in
    WP20; until then a no-op job kind `noop-work` is used in tests).
  - [ ] AC3 — An agent never has more than one running work job.
  - [ ] AC4 — The PM avoids assigning one agent more than 3 TODO cards across projects (soft rule
    in scoring load).
- **Tasks:** pickup phase; job enqueue port.
- **Tests:** unit + integration tests.
- **Done when:** all AC green.

#### US-17.07 — Reviewer pickup order

- [ ] **US-17.07 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the QA, I want to review cards fairly.
- **Acceptance criteria:**
  - [ ] AC1 — For an idle reviewer (QA, or the fallback chain when QA is disabled), the next
    REVIEW card is chosen FIFO by arrival, P0 first; `ReviewStarted` + review job enqueued (WP22).
  - [ ] AC2 — The fallback reviewer is never the card's assignee; when only the user can review,
    the card waits and the PM notifies the user (WP18).
- **Tasks:** reviewer phase.
- **Tests:** unit tests.
- **Done when:** all AC green.

### D17.4 — Anomalies

#### US-17.08 — Stale DOING detection

- [ ] **US-17.08 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the PM, I want to notice work that stopped moving.
- **Acceptance criteria:**
  - [ ] AC1 — A card in DOING longer than `stale_doing_minutes` (project setting, default 60) with
    no job progress → `CardStale` event once per threshold crossing.
  - [ ] AC2 — The board tile shows a "stale" badge; WP18 PM posts a proactive message.
- **Tasks:** detector, event, projection flag.
- **Tests:** fake clock tests.
- **Done when:** all AC green.

#### US-17.09 — Blocked-card SLA

- [ ] **US-17.09 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want blocked cards handled quickly (Constitution §8.8).
- **Acceptance criteria:**
  - [ ] AC1 — On `CardBlocked`, the PM is notified; if not unblocked or unassigned within the SLA
    (default 10 min office time) → `BlockedSlaBreached`.
  - [ ] AC2 — The PM's response job (WP18 `resolve-blocker`) is enqueued; until WP18, the
    breach appears as a Logbook line and a title-bar warning.
- **Tasks:** detector, events.
- **Tests:** fake clock tests.
- **Done when:** all AC green.

#### US-17.10 — Rework escalation

- [ ] **US-17.10 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to be told when a card keeps bouncing (Constitution §8.7.3).
- **Acceptance criteria:**
  - [ ] AC1 — When `rework_count` reaches 3 → `CardEscalated{reason: rework_loop, options:[split,
    clarify, reassign, accept_with_known_issues]}` (E11 groundwork).
  - [ ] AC2 — Escalation choreography (PM to meeting table) plays (mapping exists).
- **Tasks:** detector/decision.
- **Tests:** GWT tests.
- **Done when:** all AC green.

#### US-17.11 — Budget thresholds in scheduling

- [ ] **US-17.11 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want scheduling to respect my budgets.
- **Acceptance criteria:**
  - [ ] AC1 — Projects at ≥ 100 % budget get no new jobs or pulls; at 80 % a warning badge shows on
    the project.
  - [ ] AC2 — Raising the budget resumes scheduling on the next tick.
- **Tasks:** integration with WP15 budget service.
- **Tests:** integration tests.
- **Done when:** all AC green.

#### US-17.12 — Scheduling scenarios E2 and E8

- [ ] **US-17.12 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want the key scheduling scenarios automated.
- **Acceptance criteria:**
  - [ ] AC1 — E2: TODO 2/3 and 2 Ready cards → exactly 1 pulled (highest priority) in one tick.
  - [ ] AC2 — E8: TODO 3/3, a card starts → within one tick the next Ready card is pulled and the
    `CardPulled` choreography plays (E2E with engine hook).
  - [ ] AC3 — Pause during a tick → no further pulls until resume.
- **Tasks:** integration + E2E tests.
- **Tests:** itself.
- **Done when:** all AC green.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP17 closing: Orchestrator & assignment`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; E2 and E8 green; Orchestrator documented in BACKEND.md.
- [ ] Appendix B updated (`CardStale`, `BlockedSlaBreached`, `OfficeIdleNoExecutors` if kept).

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Tick phases race with user commands | All changes go through handlers with optimistic concurrency |
| Thundering herd of jobs | Global LLM concurrency limiter (WP15) |
| Multiple core instances | Advisory lock: single Orchestrator |

## 7. Blockers

None.

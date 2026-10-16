# WP18 — PM Chat

| Field        | Value |
| ------------ | ----- |
| Milestone    | M4 — Paula |
| Status       | READY |
| Depends on   | WP15, WP16, WP17, WP10 (work log), WP11 (ADRs) |
| Enables      | WP21 (Support questions through the PM), WP22 (escalation dialogs), WP23 |
| Constitution | §4.3.5, §5.3 (items 6–8), §10.4, Article XI, §16.5, Appendix E (E7, E11) |
| Guides       | [BACKEND.md](../../.docs/BACKEND.md) §9 · [FRONTEND.md](../../.docs/FRONTEND.md) · [DESIGN.md](../../.docs/DESIGN.md) §5.4 (Shell) |
| Skills       | `authoring-office-agents`, `tracing-events`, `designing-amiga-ui`, `delivering-features`, `writing-adrs` |
| Estimate     | 39 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-18.01 — Context snapshot builder with `asOfEventId` (5 pts)
- [ ] US-18.02 — PM read tools (3 pts)
- [ ] US-18.03 — Chat aggregate, events and API (3 pts)
- [ ] US-18.04 — Grounded answers with citations (5 pts)
- [ ] US-18.05 — Labelled forecasts (2 pts)
- [ ] US-18.06 — PM chat evaluation set (3 pts)
- [ ] US-18.07 — Proposed commands with confirmation (5 pts)
- [ ] US-18.08 — New requests from chat become notes (2 pts)
- [ ] US-18.09 — PM Chat window: Shell mode (3 pts)
- [ ] US-18.10 — PM Chat window: bubble mode and citation links (3 pts)
- [ ] US-18.11 — Proactive messages and drive light (3 pts)
- [ ] US-18.12 — "Ask the PM about…" shortcuts and E7 (2 pts)

## 1. Objective

Let the user talk to the Project Manager about anything concerning the work and get truthful,
cited answers built from a reproducible snapshot of the office; let the user ask the PM to act
(with explicit confirmation); and let the PM reach out proactively for escalations and questions.

## 2. Scope

**In:** snapshot builder; PM read tools; chat aggregate; `answer-chat` job; citations and
no-record behavior; forecasts; evals; proposed commands; chat → note; PM Chat window (Shell +
bubbles); proactive messages; Agent Card / card shortcuts; E7, E11 (message part).

**Out:** voice (non-goal); multi-user chat (non-goal).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D18.1 | Awareness | Reproducible context snapshot (`asOfEventId`) of agents, boards, notes, ADRs, recent log; PM read tools | Snapshot tests; tool permission tests | US-18.01, US-18.02 |
| D18.2 | Answers | Chat events/API; `answer-chat` agent with citations, "I have no record of…", labelled forecasts; evals | E7; eval baseline | US-18.03 – US-18.06 |
| D18.3 | Actions | Proposed commands with Confirm/Cancel executed as user via pm-chat; destructive actions refused; chat → Note | GWT + E2E | US-18.07, US-18.08 |
| D18.4 | Chat UI | Shell and bubble modes, clickable citations, proactive messages with drive light, shortcuts | E2E; axe | US-18.09 – US-18.12 |

## 4. User stories

### D18.1 — Awareness

#### US-18.01 — Context snapshot builder with `asOfEventId`

- [ ] **US-18.01 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the PM, I want a compact, complete snapshot of the office for each answer, so that
  my answers are true and reproducible (Constitution §10.4).
- **Acceptance criteria:**
  - [ ] AC1 — `build_snapshot(question, as_of)` collects: all agents (status, current card,
    queue, last activity), per-project board summaries (counts, WIP, blocked, stale, rework),
    cards relevant to the question (ids mentioned or search hits), recent work-log lines (last
    50 + search hits), ADR titles/status, open notes.
  - [ ] AC2 — The snapshot records `as_of_event_id` (last committed event at build time) and is
    deterministic for the same position.
  - [ ] AC3 — Size budget: ≤ configurable tokens (default 6 000), truncating least relevant
    sections first with a note.
  - [ ] AC4 — All text from notes/cards/log is wrapped with `untrusted_block`.
- **Tasks:** `application/chat/snapshot.py`.
- **Tests:** unit tests with fixtures; determinism test.
- **Done when:** all AC green.

#### US-18.02 — PM read tools

- [ ] **US-18.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the PM, I want tools to look things up beyond the snapshot.
- **Acceptance criteria:**
  - [ ] AC1 — Tools `board.read(project, filters)`, `events.search(query, filters)`,
    `agents.readState(agent?)`, `adr.read(id)`, `card.read(id)` — read-only, bounded results.
  - [ ] AC2 — Tools are available only to the PM role (catalog allow-list) and are traced
    (`AgentToolCalled`).
- **Tasks:** tool functions calling queries.
- **Tests:** unit tests; permission test.
- **Done when:** all AC green.

### D18.2 — Answers

#### US-18.03 — Chat aggregate, events and API

- [ ] **US-18.03 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want my conversation with the PM stored.
- **Acceptance criteria:**
  - [ ] AC1 — `PostChatMessage(text)` by the user → `ChatMessagePosted{author:user}`; PM replies
    → `ChatMessagePosted{author:pm, as_of_event_id, citations[]}`.
  - [ ] AC2 — `GET /api/chat?cursor=` (history), `POST /api/chat` (new message → 202, reply via
    WebSocket).
  - [ ] AC3 — One conversation thread in v1; messages ≤ 4 000 chars.
- **Tasks:** domain `chat`, projection, router.
- **Tests:** GWT, API tests.
- **Done when:** all AC green.

#### US-18.04 — Grounded answers with citations

- [ ] **US-18.04 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to ask the PM anything about the work and get a true answer with
  references (Constitution §11.2, E7).
- **Acceptance criteria:**
  - [ ] AC1 — Output model `PmAnswer{text, citations[{kind: card|adr|note|agent|event, id}],
    confidence, needs_user_input?}`; English; concise.
  - [ ] AC2 — Every id in `citations` must exist in the snapshot or tool results (validator);
    otherwise the output is retried once, then the unsupported citation is removed with a note.
  - [ ] AC3 — If the data does not contain the answer, the text says "I have no record of…".
  - [ ] AC4 — E7: Copper working on SHOP-3; "What is Copper doing?" → answer mentions SHOP-3 and
    `as_of_event_id` is set (fake LLM test + eval case).
- **Tasks:** output model, prompt `project_manager/v3.md` (chat section), job kind `answer-chat`.
- **Tests:** unit tests; E7.
- **Done when:** all AC green.

#### US-18.05 — Labelled forecasts

- [ ] **US-18.05 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want estimates I can trust to be estimates.
- **Acceptance criteria:**
  - [ ] AC1 — Forecast questions get an answer labelled "Estimate" with the method (computed
    server-side from cycle-time stats, not invented by the model).
  - [ ] AC2 — A `forecast` tool returns throughput and cycle time per project/agent from
    projections.
- **Tasks:** stats projection/tool.
- **Tests:** unit tests.
- **Done when:** all AC green.

#### US-18.06 — PM chat evaluation set

- [ ] **US-18.06 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a maintainer, I want chat quality measured (success criterion S5).
- **Acceptance criteria:**
  - [ ] AC1 — ≥ 20 cases: status questions, why-rejected, ADR lookup, blockers, summaries,
    unknown facts (must say no record), injection attempts, forecasts.
  - [ ] AC2 — Evaluators check citations validity, presence of required ids, "no record" for
    unknowns, English.
  - [ ] AC3 — Baseline committed; target ≥ 95 % on status questions.
- **Tasks:** dataset, evaluators, baseline.
- **Tests:** harness.
- **Done when:** nightly includes PM chat evals.

### D18.3 — Actions

#### US-18.07 — Proposed commands with confirmation

- [ ] **US-18.07 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to ask the PM to do things, but only with my explicit OK
  (Constitution §11.3).
- **Acceptance criteria:**
  - [ ] AC1 — The PM output may include `proposed_command` (from an allow-list: rerank card,
    pause/resume agent, pull card, reassign, unblock with resolution, raise priority) →
    `ChatCommandProposed`.
  - [ ] AC2 — The UI shows a requester "Paula proposes: … Confirm / Cancel"; Confirm →
    `ChatCommandConfirmed` → command executed as `actor=user, via=pm-chat`; Cancel →
    `ChatCommandCancelled`.
  - [ ] AC3 — Destructive actions (archive, delete, reset, disable agents) are never proposed;
    the PM points to the right window instead (validator rejects them).
  - [ ] AC4 — Domain rejections of confirmed commands are reported back in chat.
- **Tasks:** output model, allow-list, events, UI requester.
- **Tests:** GWT + E2E.
- **Done when:** all AC green.

#### US-18.08 — New requests from chat become notes

- [ ] **US-18.08 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to ask for new work in chat, and have it go through the normal
  intake (single path to the Backlog).
- **Acceptance criteria:**
  - [ ] AC1 — When the PM detects a new request, it proposes "Create a note with this request?";
    on confirm → `NoteSubmitted` with the chat text (WP16 flow).
  - [ ] AC2 — Note questions awaiting the user (WP16) appear as PM messages with an *Answer*
    action.
- **Tasks:** proposal kind `create_note`; bridge to intake.
- **Tests:** E2E.
- **Done when:** all AC green.

### D18.4 — Chat UI

#### US-18.09 — PM Chat window: Shell mode

- [ ] **US-18.09 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to talk to Paula in an AmigaShell-style window.
- **Acceptance criteria:**
  - [ ] AC1 — "Talk to PM" icon opens an `AmigaShell`: prompt `1.SYS:> `, block cursor, history
    with ↑/↓, Enter sends.
  - [ ] AC2 — Replies appear as `Paula> …`; while thinking, a `Please wait… Paula is thinking`
    line and the drive LED.
  - [ ] AC3 — History loads with cursor pagination on scroll up.
- **Tasks:** `windows/chat/`.
- **Tests:** component tests; E2E.
- **Done when:** all AC green.

#### US-18.10 — PM Chat window: bubble mode and citation links

- [ ] **US-18.10 completed** · **Points:** 3 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want a friendlier view with clickable references.
- **Acceptance criteria:**
  - [ ] AC1 — Toggle Shell ↔ bubbles (with portraits); preference persisted.
  - [ ] AC2 — Citations render as links opening cards, ADRs, notes, agents, Logbook entries.
  - [ ] AC3 — `as_of` shown on hover ("as of 14:02:11").
- **Tasks:** bubble view, citation renderer.
- **Tests:** component tests.
- **Done when:** all AC green.

#### US-18.11 — Proactive messages and drive light

- [ ] **US-18.11 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want the PM to tell me only what needs my attention (Constitution
  §11.4).
- **Acceptance criteria:**
  - [ ] AC1 — Proactive PM messages for: `CardEscalated` (with options, E11 message part),
    `BlockedSlaBreached`, `BudgetThresholdReached`, `NoteFailed`, `NoteAwaitingUser`,
    `OfficeIdleNoExecutors`, cards waiting for user review; never for routine progress.
  - [ ] AC2 — A blinking drive-light on the "Talk to PM" icon until read (static under reduced
    motion).
  - [ ] AC3 — Escalation options are actionable (split → note, reassign → proposed command,
    accept with known issues → opens the card's review form).
- **Tasks:** proactive message job (templated text, LLM optional for summaries), icon badge.
- **Tests:** GWT + E2E.
- **Done when:** all AC green.

#### US-18.12 — "Ask the PM about…" shortcuts and E7

- [ ] **US-18.12 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want to ask about an agent or a card from where I see it.
- **Acceptance criteria:**
  - [ ] AC1 — Agent Card (WP14) and Card Detail have "Ask Paula about this" pre-filling the chat.
  - [ ] AC2 — E2E E7 passes through the UI with the fake LLM.
- **Tasks:** shortcuts.
- **Tests:** E2E.
- **Done when:** M4 exit criteria demonstrated; `v0.5.0` tagged after WP15–WP18 are DONE.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP18 closing: PM chat`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; E7 green; PM chat eval baseline committed (S5 measured).
- [ ] Constitution Article XI matches behavior; Appendix B chat events aligned.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Hallucinated facts | Snapshot grounding + citation validator + "no record" rule + evals |
| Snapshot too large for local models | Token budget with relevance ordering |
| Users over-trust forecasts | Server-computed forecasts, explicitly labelled |

## 7. Blockers

None.

# WP21 — Support Triage

| Field        | Value |
| ------------ | ----- |
| Milestone    | M5 — Chipset |
| Status       | READY |
| Depends on   | WP16 (note routing), WP18 (questions via PM chat), WP15 |
| Enables      | WP22 (better bug cards to review), WP24 (complete E6) |
| Constitution | §5.7, Article VII (§7.1–7.2), Appendix A (`TriageReport`), Appendix C (triage rows), Appendix E (E6) |
| Guides       | [BACKEND.md](../../.docs/BACKEND.md) §9 · [OLLAMA.md](../../.docs/OLLAMA.md) |
| Skills       | `authoring-office-agents`, `tracing-events`, `delivering-features`, `writing-adrs` |
| Estimate     | 19 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-21.01 — Triage report model and triage job (5 pts)
- [ ] US-21.02 — Severity scale and priority mapping (2 pts)
- [ ] US-21.03 — Delegation from the PM and hand-back for card writing (3 pts)
- [ ] US-21.04 — Missing information questions through the PM (3 pts)
- [ ] US-21.05 — Duplicate and recurrence detection across projects (3 pts)
- [ ] US-21.06 — Scenario E6 and Support evals (3 pts)

## 1. Objective

Let the Support agent triage bug and incident notes before the PM writes cards: a structured
Triage Report (severity, impact, reproduction, expected/actual, suspected areas, duplicates,
open questions), questions to the user through the PM, and cross-project pattern detection —
so bug cards are accurate and correctly prioritized.

## 2. Scope

**In:** `TriageReport` model; `triage` job; severity → priority mapping; PM delegation and
hand-back; user questions via PM chat with timeout; duplicates/recurrence; E6; evals.

**Out:** Support talking to the user directly (v1: always through the PM).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D21.1 | Triage | Report model and job; severity scale S1–S4 mapped to P0–P3 | Unit/integration tests | US-21.01, US-21.02 |
| D21.2 | Collaboration with the PM | Delegation, questions via PM chat with timeout, hand-back → PM writes cards using the report | E2E with fake LLM; office choreographies | US-21.03, US-21.04 |
| D21.3 | Patterns & quality | Duplicates/recurrence across projects; E6; evals | E6 green; eval baseline | US-21.05, US-21.06 |

## 4. User stories

### D21.1 — Triage

#### US-21.01 — Triage report model and triage job

- [ ] **US-21.01 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the PM, I want bug notes triaged into a structured report, so that I write accurate
  cards.
- **Acceptance criteria:**
  - [ ] AC1 — Output `TriageReport{summary, category, severity S1–S4, impact, steps_to_reproduce[],
    expected, actual, suspected_areas[], duplicates[], open_questions[]}` (Appendix A).
  - [ ] AC2 — `NoteSentToTriage` enqueues the `triage` job for the Support agent; the report is
    stored (`TriageCompleted{report_id, severity}`).
  - [ ] AC3 — Prompt `support/v2.md`; toolset `board.read`, `events.search`,
    `workspace.readFiles` (read-only, when a workspace exists).
- **Tasks:** model, job, prompt, projection of reports.
- **Tests:** unit + integration tests.
- **Done when:** all AC green.

#### US-21.02 — Severity scale and priority mapping

- [ ] **US-21.02 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want severity to drive priority consistently.
- **Acceptance criteria:**
  - [ ] AC1 — S1 → P0, S2 → P1, S3 → P2, S4 → P3 (Constitution §5.7), applied by the PM when
    writing cards from a report; deviations require a stated reason.
  - [ ] AC2 — Severity is shown on bug cards as a badge with text.
- **Tasks:** mapping in PM `to_commands`; UI badge.
- **Tests:** unit tests.
- **Done when:** all AC green.

### D21.2 — Collaboration with the PM

#### US-21.03 — Delegation from the PM and hand-back for card writing

- [ ] **US-21.03 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to see the PM hand bug notes to Support and get them back triaged.
- **Acceptance criteria:**
  - [ ] AC1 — Office: Paula carries the note to Gary's desk; Gary carries the report back
    (Appendix C rows).
  - [ ] AC2 — On `TriageCompleted`, the PM `process-note` job re-runs with the report in context
    and writes bug cards (priority per mapping, reproduction steps in description, criteria
    derived from expected behavior).
  - [ ] AC3 — The card links the report (`triage` deliverable).
- **Tasks:** PM context extension; mapping.
- **Tests:** integration + E2E.
- **Done when:** all AC green.

#### US-21.04 — Missing information questions through the PM

- [ ] **US-21.04 completed** · **Points:** 3 · **Priority:** Should · **ADR:** —
- **Story:** As Support, I want to ask the user for missing details without talking to them
  directly.
- **Acceptance criteria:**
  - [ ] AC1 — `open_questions` with `ask_user=true` → `NoteAwaitingUser` with the questions shown
    in PM chat attributed "Gary asks:".
  - [ ] AC2 — Answers resume triage; after `VO_TRIAGE_QUESTION_TIMEOUT_MIN` (default 30) the report
    is filed with gaps marked.
- **Tasks:** bridge with WP18 proactive messages.
- **Tests:** integration tests.
- **Done when:** all AC green.

### D21.3 — Patterns & quality

#### US-21.05 — Duplicate and recurrence detection across projects

- [ ] **US-21.05 completed** · **Points:** 3 · **Priority:** Should · **ADR:** —
- **Story:** As the PM, I want Support to spot duplicates and recurring issues.
- **Acceptance criteria:**
  - [ ] AC1 — Support searches open and recent DONE bug cards across projects; candidates listed
    in `duplicates` with similarity reason.
  - [ ] AC2 — Three or more similar reports in 14 days → `RecurringIssueDetected` event; the PM
    tells the user proactively.
- **Tasks:** search query; detector.
- **Tests:** integration tests.
- **Done when:** all AC green.

#### US-21.06 — Scenario E6 and Support evals

- [ ] **US-21.06 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want triage quality measured.
- **Acceptance criteria:**
  - [ ] AC1 — E6: a bug note with Support enabled → a Triage Report exists before the card; the
    card priority matches the severity mapping.
  - [ ] AC2 — Support eval dataset ≥ 10 cases (clear bug, vague bug, duplicate, incident,
    injection) with a committed baseline.
- **Tasks:** E2E test; dataset.
- **Tests:** itself.
- **Done when:** all AC green.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP21 closing: Support triage`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; E6 green; Support eval baseline committed.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Triage adds latency to bug intake | Only for bug/incident notes; visible status; timeout for questions |
| Wrong severity | Mapping visible; user can edit priority; evals |

## 7. Blockers

None.

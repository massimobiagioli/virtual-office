# WP22 — QA Review Gate

| Field        | Value |
| ------------ | ----- |
| Milestone    | M5 — Chipset |
| Status       | READY |
| Depends on   | WP20 (deliverables), WP17 (reviewer pickup), WP19 (checks), WP11 (ADRs), WP18 (user notifications) |
| Enables      | WP23, WP24 |
| Constitution | §5.8, §8.4, §8.7, Appendix A (`Review`), Appendix C (review rows), Appendix E (E3, E9, E10, E11, E12) |
| Guides       | [BACKEND.md](../../.docs/BACKEND.md) §9 · [OLLAMA.md](../../.docs/OLLAMA.md) |
| Skills       | `authoring-office-agents`, `enforcing-kanban-workflow`, `delivering-features`, `writing-adrs` |
| Estimate     | 31 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-22.01 — Review verdict model and review job (5 pts)
- [ ] US-22.02 — Running verification commands as evidence (3 pts)
- [ ] US-22.03 — ADR and guideline compliance checks (2 pts)
- [ ] US-22.04 — Approval flow (2 pts)
- [ ] US-22.05 — Rejection flow with numbered notes (3 pts)
- [ ] US-22.06 — Rework loop and escalation integration (3 pts)
- [ ] US-22.07 — Review fallback chain (3 pts)
- [ ] US-22.08 — User review requests (2 pts)
- [ ] US-22.09 — QA evals and review scenarios (3 pts)
- [ ] US-22.10 — End-to-end demo project (5 pts)

## 1. Objective

Make QA the real gate: the QA agent verifies every acceptance criterion with evidence, runs the
project's checks, verifies ADR compliance, and either approves (DONE) or rejects with numbered,
actionable notes (back to TODO), with escalation after three rejections and a fallback chain when
QA is disabled — closing the full loop described by the user.

## 2. Scope

**In:** `review-card` job, verdict model, checks as evidence, compliance checks, approve/reject
mapping and choreographies, rework/escalation integration, fallback chain (architect → PM →
user), user review requests, evals, scenarios E3/E9/E10/E11/E12, scripted end-to-end demo.

**Out:** code fixes by QA (forbidden).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D22.1 | Review job | Per-criterion verdicts with evidence; checks run; ADR/guideline compliance | Unit/integration tests with fixture deliverables | US-22.01 – US-22.03 |
| D22.2 | Gate flows | Approve → DONE with stamp; reject → TODO with numbered notes; rework and escalation | E9, E10, E11 | US-22.04 – US-22.06 |
| D22.3 | Fallbacks & proof | Fallback reviewers, user review requests, QA evals, full demo project | E12; demo recording | US-22.07 – US-22.10 |

## 4. User stories

### D22.1 — Review job

#### US-22.01 — Review verdict model and review job

- [ ] **US-22.01 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want QA to check each acceptance criterion with evidence, so that DONE
  means done.
- **Acceptance criteria:**
  - [ ] AC1 — Output `ReviewVerdict{verdict: approved|changes_requested, criteria[{criterion_id,
    result: pass|fail|not-verifiable, evidence}], notes[{n, severity: blocker|major|minor|nit,
    text}], summary}`.
  - [ ] AC2 — The job reads the card, deliverables (diff via tool for code, documents for
    design/architecture), linked ADRs, previous reviews.
  - [ ] AC3 — Validators: every criterion has a result; `changes_requested` needs ≥ 1
    blocker/major note; `approved` requires no fail and no blocker/major.
  - [ ] AC4 — Prompt `qa/v2.md`; toolset per §15.7 (no write tools).
- **Tasks:** models, prompt, job, mapping to `ApproveCard`/`RejectCard`.
- **Tests:** unit tests with `FunctionModel`.
- **Done when:** all AC green.

#### US-22.02 — Running verification commands as evidence

- [ ] **US-22.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As QA, I want to run the project's checks myself, not trust the developer's report.
- **Acceptance criteria:**
  - [ ] AC1 — For code deliverables with a workspace, QA runs the allow-listed verification
    commands on the card branch (read-only checkout or worktree per WP19 ADR) and cites results.
  - [ ] AC2 — Differences between developer-reported and QA-observed results are flagged as a
    `major` note.
- **Tasks:** tool use; evidence formatting.
- **Tests:** integration test on a temp repo.
- **Done when:** all AC green.

#### US-22.03 — ADR and guideline compliance checks

- [ ] **US-22.03 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the architect, I want QA to verify that work respects accepted decisions.
- **Acceptance criteria:**
  - [ ] AC1 — Accepted Project ADRs linked to the card or its epic are in context; violations are
    `major` notes citing the ADR id.
  - [ ] AC2 — For design cards, the design guideline document is checked; missing component states
    are `major` notes.
- **Tasks:** context pack extension.
- **Tests:** unit tests.
- **Done when:** all AC green.

### D22.2 — Gate flows

#### US-22.04 — Approval flow

- [ ] **US-22.04 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want approvals celebrated and recorded.
- **Acceptance criteria:**
  - [ ] AC1 — `approved` → `CardApproved` with the review → DONE; office plays stamp, archive walk
    and confetti.
  - [ ] AC2 — The Logbook line includes the summary.
- **Tasks:** mapping.
- **Tests:** integration + E2E.
- **Done when:** all AC green.

#### US-22.05 — Rejection flow with numbered notes

- [ ] **US-22.05 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a developer, I want rejections with clear, numbered, actionable notes (E9, E10).
- **Acceptance criteria:**
  - [ ] AC1 — `changes_requested` → `CardRejected` → TODO, same assignee, `rework_count + 1`; office
    plays QA walking to the assignee with `✗` and the first note title (E9).
  - [ ] AC2 — Nits-only rejection is impossible (validator + domain `RejectionRequiresMajorNote`,
    E10).
- **Tasks:** mapping.
- **Tests:** integration + E2E E9, E10.
- **Done when:** all AC green.

#### US-22.06 — Rework loop and escalation integration

- [ ] **US-22.06 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want endless review ping-pong stopped (E11).
- **Acceptance criteria:**
  - [ ] AC1 — Third rejection → `CardEscalated` (WP17) → PM proactive message with options (WP18).
  - [ ] AC2 — Choosing "accept with known issues" opens the user review form pre-filled with QA's
    notes; approving it records the known issues in the review summary.
- **Tasks:** integration wiring.
- **Tests:** E2E E11.
- **Done when:** all AC green.

### D22.3 — Fallbacks & proof

#### US-22.07 — Review fallback chain

- [ ] **US-22.07 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a user running without QA, I want reviews to still happen (E12).
- **Acceptance criteria:**
  - [ ] AC1 — QA disabled → Architect reviews (`is_fallback=true`); Architect disabled or is the
    assignee → PM reviews in review-only mode; otherwise the user.
  - [ ] AC2 — The reviewer is never the assignee; fallback reviews are labelled in UI and events.
  - [ ] AC3 — E12 automated.
- **Tasks:** reviewer resolution in WP17 phase; role prompts for review mode.
- **Tests:** unit + E2E E12.
- **Done when:** all AC green.

#### US-22.08 — User review requests

- [ ] **US-22.08 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to be asked when only I can review.
- **Acceptance criteria:**
  - [ ] AC1 — A REVIEW card with only the user as eligible reviewer → PM proactive message with a
    link opening the review form (WP08 form reused).
  - [ ] AC2 — Pending user reviews are counted in the title bar status.
- **Tasks:** notification wiring.
- **Tests:** E2E.
- **Done when:** all AC green.

#### US-22.09 — QA evals and review scenarios

- [ ] **US-22.09 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want QA quality measured.
- **Acceptance criteria:**
  - [ ] AC1 — QA eval dataset ≥ 12 cases (good change, missing test, failing check, ADR violation,
    nits only, design missing states, injection in code comments) with baseline.
  - [ ] AC2 — E3 re-verified with the QA agent (QA never reviews its own work; agents never review
    their own work).
- **Tasks:** dataset; tests.
- **Tests:** itself.
- **Done when:** all AC green.

#### US-22.10 — End-to-end demo project

- [ ] **US-22.10 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want a reproducible demo where a note becomes DONE cards
  through every role.
- **Acceptance criteria:**
  - [ ] AC1 — A fixture repository and a scripted note ("Add a /health endpoint with tests to the
    demo service") run end to end with the fake LLM in CI: intake → (triage if bug) → architecture
    → implementation → review → one rejection → rework → approval → DONE.
  - [ ] AC2 — The same script runs with the locked real models in the nightly job; result and
    timings recorded.
  - [ ] AC3 — A screen recording of the real-model run is attached to the M5 release notes.
- **Tasks:** fixture repo, script, CI wiring.
- **Tests:** itself.
- **Done when:** M5 exit criteria demonstrated; `v0.6.0` tagged after WP19–WP22 are DONE.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP22 closing: QA review gate`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; E3, E9, E10, E11, E12 green; QA eval baseline committed.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| QA too lenient/strict | Evals with both kinds of cases; severity rules enforced by domain |
| Reviews slow with real models | Checks run in parallel to reading; concurrency limits |
| Fallback PM bias reviewing its own planning | Review-only prompt; never assignee; labelled fallback |

## 7. Blockers

None.

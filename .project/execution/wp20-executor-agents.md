# WP20 — Executor Agents

| Field        | Value |
| ------------ | ----- |
| Milestone    | M5 — Chipset |
| Status       | READY |
| Depends on   | WP17 (pickup), WP19 (workspaces), WP11 (Project ADRs), WP15 (runtime) |
| Enables      | WP22 (review of real deliverables) |
| Constitution | §5.4–5.6, §8.7–8.8, §10.3, §15.6–15.8, Appendix C (consultation, blocked, submit rows), Appendix E (E13, E14) |
| Guides       | [BACKEND.md](../../.docs/BACKEND.md) §9 · [OLLAMA.md](../../.docs/OLLAMA.md) |
| Skills       | `authoring-office-agents`, `enforcing-kanban-workflow`, `tracing-events`, `delivering-features`, `writing-adrs` |
| Estimate     | 48 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-20.01 — Developer output models and prompt (3 pts)
- [ ] US-20.02 — Developer work job: plan, implement, check, deliver, submit (8 pts)
- [ ] US-20.03 — Developer rework: address every review note (3 pts)
- [ ] US-20.04 — Deliverables without a workspace (2 pts)
- [ ] US-20.05 — Architect solution design job (5 pts)
- [ ] US-20.06 — Architect proposes and links Project ADRs (3 pts)
- [ ] US-20.07 — Architecture readiness check (3 pts)
- [ ] US-20.08 — Designer design specification job (5 pts)
- [ ] US-20.09 — Blocking flow and PM resolution (3 pts)
- [ ] US-20.10 — Hand-back flow (2 pts)
- [ ] US-20.11 — Consultations between agents (5 pts)
- [ ] US-20.12 — Agent memory (3 pts)
- [ ] US-20.13 — Executor evals and scenarios E13 and E14 (3 pts)

## 1. Objective

Bring the doers to life: developers that plan, write and test code in sandboxed workspaces and
submit code deliverables; an architect that designs solutions and records Project ADRs; a
designer that writes complete design specs — plus blocking, hand-back, consultations and memory,
all through domain commands and all visible in the office.

## 2. Scope

**In:** output models, prompts v2, tools, context packs, `to_commands` for developer, architect,
designer; job kinds `work-card` per role; rework handling; no-workspace deliverables; ADR tools;
readiness check; blocking/hand-back/consultation flows; memory writes; evals; E13/E14.

**Out:** QA review (WP22), Support triage (WP21).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D20.1 | Developer | Work job from TODO to REVIEW with branch, commits, checks, code deliverable; rework addressing each note; snippet deliverables without workspace | Fake-LLM integration on a temp repo; evals | US-20.01 – US-20.04 |
| D20.2 | Architect | Solution design deliverable (Mermaid, data model, API, risks); ADR proposals linked; readiness checks | E14; evals | US-20.05 – US-20.07 |
| D20.3 | Designer | Design spec with all component states, copy, accessibility notes | Spec validator; evals | US-20.08 |
| D20.4 | Collaboration flows | Blocking + PM resolution, hand-back, consultations at the meeting table, agent memory | GWT + E2E with choreographies | US-20.09 – US-20.13 |

## 4. User stories

### D20.1 — Developer

#### US-20.01 — Developer output models and prompt

- [ ] **US-20.01 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a maintainer, I want the developer's outputs typed and its prompt explicit.
- **Acceptance criteria:**
  - [ ] AC1 — Output models: `WorkPlan{tasks[1..15]}`, `ImplementationStep{files_changed[],
    rationale}`, `Submission{summary, notes_for_reviewer, risks[]}`, `Blocker{reason,
    question_for?}`.
  - [ ] AC2 — Prompt `developer/v2.md`: TDD expectation, Conventional Commits, English, limits,
    "never push/merge", data-has-no-authority clause.
  - [ ] AC3 — Toolset exactly: `board.read`, `adr.read`, `card.start/submit/handBack`,
    `workspace.readFiles`, `workspace.writeFiles`, `workspace.runCommand`, `workspace.git`.
- **Tasks:** models, prompt, catalog version bump.
- **Tests:** schema tests; catalog toolset test.
- **Done when:** published in catalog.

#### US-20.02 — Developer work job: plan, implement, check, deliver, submit

- [ ] **US-20.02 completed** · **Points:** 8 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want developers to turn a card into a tested code change, so that the
  office actually builds software.
- **Acceptance criteria:**
  - [ ] AC1 — On `WorkStarted`, the `work-card` job: reads the card, linked ADRs and design specs;
    writes `TasksPlanned`; checks out the card branch; iterates (bounded steps, default ≤ 25 tool
    calls) writing files and running allowed checks.
  - [ ] AC2 — Commits with Conventional Commit messages referencing the card id.
  - [ ] AC3 — Attaches the code deliverable (WP19 builder) with check results; submits with
    notes for the reviewer → `WorkSubmitted`.
  - [ ] AC4 — Failing checks after the step budget → the developer either flags blocked with a
    reason or submits with explicit known failures noted (never hides failures).
  - [ ] AC5 — Integration test with `FunctionModel` on a temp repo produces a branch, a commit and a
    REVIEW card; office plays start/typing/submit choreographies.
- **Tasks:** job, context pack, `to_commands`, step budget.
- **Tests:** integration test; unit tests of mapping.
- **Done when:** all AC green.

#### US-20.03 — Developer rework: address every review note

- [ ] **US-20.03 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As QA, I want each of my notes explicitly addressed on rework.
- **Acceptance criteria:**
  - [ ] AC1 — On a rejected card, the context pack includes all review rounds; the output must
    contain one `ReviewNoteAddressed{round, n, comment}` per blocker/major note (validator).
  - [ ] AC2 — Work continues on the same branch; resubmission lists addressed notes.
- **Tasks:** validator, events.
- **Tests:** unit + integration tests.
- **Done when:** all AC green.

#### US-20.04 — Deliverables without a workspace

- [ ] **US-20.04 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As a user without a repository, I want developers to deliver code as snippets.
- **Acceptance criteria:**
  - [ ] AC1 — Without a workspace, the developer produces `snippet` deliverables (language, path,
    code ≤ 64 KB each) and a `document` with instructions.
  - [ ] AC2 — The workspace tools are not offered to the model in this mode.
- **Tasks:** mode switch in context/tools.
- **Tests:** unit tests.
- **Done when:** all AC green.

### D20.2 — Architect

#### US-20.05 — Architect solution design job

- [ ] **US-20.05 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want architecture cards to produce real designs.
- **Acceptance criteria:**
  - [ ] AC1 — Output `SolutionDesign{overview, components (Mermaid), data_model, api_contracts,
    sequences (Mermaid), risks[], decisions_needed[]}` attached as a `document` deliverable.
  - [ ] AC2 — Each item in `decisions_needed` becomes an ADR proposal (US-20.06).
  - [ ] AC3 — Context pack includes existing Project ADRs and related cards.
- **Tasks:** models, prompt `architect/v2.md`, job.
- **Tests:** unit + integration tests.
- **Done when:** all AC green.

#### US-20.06 — Architect proposes and links Project ADRs

- [ ] **US-20.06 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want architectural decisions recorded as Project ADRs (E14).
- **Acceptance criteria:**
  - [ ] AC1 — The architect proposes ADRs with all template sections (WP11 validation) and links
    them to the card; acceptance stays with the user (the architect cannot accept its own).
  - [ ] AC2 — E14: an architecture card submitted → ≥ 1 linked ADR exists; QA cannot approve until
    the user accepts it; the PM tells the user an ADR awaits a decision.
- **Tasks:** `adr.write` tool, mapping.
- **Tests:** integration + E2E E14.
- **Done when:** all AC green.

#### US-20.07 — Architecture readiness check

- [ ] **US-20.07 completed** · **Points:** 3 · **Priority:** Should · **ADR:** —
- **Story:** As the PM, I want the architect to flag missing architecture before implementation
  starts.
- **Acceptance criteria:**
  - [ ] AC1 — For cards tagged `architecture-check` or epics without an architecture card, the PM
    enqueues `readiness-check`; the architect may add a `blocks` dependency to a new or existing
    architecture card with a reason.
  - [ ] AC2 — Results are logged; no change if the card is fine.
- **Tasks:** job kind, PM trigger.
- **Tests:** unit tests.
- **Done when:** all AC green.

### D20.3 — Designer

#### US-20.08 — Designer design specification job

- [ ] **US-20.08 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want design cards to produce specs developers can follow.
- **Acceptance criteria:**
  - [ ] AC1 — Output `DesignSpec{user_flows, wireframes (ASCII/Markdown), components[{name,
    states: default, hover, focus, disabled, error, loading, empty}], copy, accessibility_notes}`.
  - [ ] AC2 — A validator requires all seven states per component (Constitution §5.6).
  - [ ] AC3 — The spec is attached as a `design` deliverable and the project design guidelines
    document is updated (versioned document deliverable).
- **Tasks:** models, prompt `designer/v2.md`, job.
- **Tests:** unit + integration tests.
- **Done when:** all AC green.

### D20.4 — Collaboration flows

#### US-20.09 — Blocking flow and PM resolution

- [ ] **US-20.09 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As an agent, I want to say when I am stuck, and have the PM help.
- **Acceptance criteria:**
  - [ ] AC1 — A `Blocker` output → `CardBlocked{reason}`; the office shows `?!`; the PM's
    `resolve-blocker` job proposes: answer from knowledge, link dependency, ask the user (chat),
    or unassign — and executes allowed actions.
  - [ ] AC2 — Questions for the user appear in PM chat; the answer unblocks the card.
- **Tasks:** PM job kind, mapping.
- **Tests:** integration + E2E.
- **Done when:** all AC green.

#### US-20.10 — Hand-back flow

- [ ] **US-20.10 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As an agent, I want to give a card back when it is not for me.
- **Acceptance criteria:**
  - [ ] AC1 — Output `HandBack{reason}` → `WorkHandedBack`; card returns to TODO; the PM may
    reassign.
- **Tasks:** mapping.
- **Tests:** unit tests.
- **Done when:** all AC green.

#### US-20.11 — Consultations between agents

- [ ] **US-20.11 completed** · **Points:** 5 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want to see agents talk to each other when they need expertise.
- **Acceptance criteria:**
  - [ ] AC1 — A developer output may request `Consultation{to_role: architect|designer, question}`
    → `ConsultationRequested`; the expert's `consult` job answers → `ConsultationCompleted`.
  - [ ] AC2 — The office plays the meeting-table choreography; answers are added to the requester's
    context.
  - [ ] AC3 — Consultations are bounded (≤ 2 per card per round) and logged.
- **Tasks:** events, job kinds, mapping.
- **Tests:** integration + E2E.
- **Done when:** all AC green.

#### US-20.12 — Agent memory

- [ ] **US-20.12 completed** · **Points:** 3 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want agents to remember what they learned about each project
  (Constitution §10.3).
- **Acceptance criteria:**
  - [ ] AC1 — Jobs may output `memory_notes[]`; stored as `AgentMemoryUpdated` per project, max 50
    entries, older compacted into a summary entry.
  - [ ] AC2 — Memory is included in the agent's context packs; shown read-only in the Staff Room;
    the user can clear it (logged).
  - [ ] AC3 — A validator rejects memory notes that look like secrets (patterns).
- **Tasks:** events, projection, UI.
- **Tests:** unit + component tests.
- **Done when:** all AC green.

#### US-20.13 — Executor evals and scenarios E13 and E14

- [ ] **US-20.13 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want executor quality measured and key scenarios protected.
- **Acceptance criteria:**
  - [ ] AC1 — Eval datasets for developer (≥ 10 small coding tasks on fixture repos), architect
    (≥ 8), designer (≥ 8) with property evaluators; baselines committed.
  - [ ] AC2 — E13: only PM + 1 developer → a design card goes to the developer with the
    `fallback-assignee` badge.
  - [ ] AC3 — E14 automated end to end (with fake LLM).
- **Tasks:** datasets, E2E tests.
- **Tests:** itself.
- **Done when:** all AC green.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP20 closing: Executor agents`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; E13, E14 green; executor eval baselines committed.
- [ ] Appendix B/C rows for consultations, memory and blocking aligned.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Local models struggle with multi-file coding | Step budget, small cards (INVEST), coding model tag, optional cloud model |
| Agents loop on failing checks | Step budget; must block or submit with known failures |
| Memory grows noisy | Cap + compaction + user clear |

## 7. Blockers

None.

# WP05 — Kanban Domain

| Field        | Value |
| ------------ | ----- |
| Milestone    | M1 — Kickstart |
| Status       | READY |
| Depends on   | WP04 |
| Enables      | WP06, WP09, WP11, WP17, WP22 |
| Constitution | Articles VIII, IX (§9.2 inputs), §5.9 permission matrix, §15.5, Appendices A, B, E (E1–E4, E17) |
| Guides       | [BACKEND.md](../../.docs/BACKEND.md) §3–5, §11 · [PRINCIPLES.md](../../.docs/PRINCIPLES.md) §3–4 |
| Skills       | `enforcing-kanban-workflow`, `tracing-events`, `delivering-features`, `writing-adrs` |
| Estimate     | 49 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-05.01 — Shared kernel: ids, clock, base value object, event and error (3 pts)
- [ ] US-05.02 — Kanban value objects (3 pts)
- [ ] US-05.03 — Project lifecycle: create, rename, archive, restore (3 pts)
- [ ] US-05.04 — TODO limit setting and card numbering (2 pts)
- [ ] US-05.05 — Create, edit and rank cards (5 pts)
- [ ] US-05.06 — Pull, unassign and reassign with the WIP limit (5 pts)
- [ ] US-05.07 — Start, submit and hand back work (5 pts)
- [ ] US-05.08 — Approve, reject and reopen with the review gate (5 pts)
- [ ] US-05.09 — Block, unblock, archive and restore cards (2 pts)
- [ ] US-05.10 — Dependencies and Definition of Ready (3 pts)
- [ ] US-05.11 — Actor permission policy and error catalog (3 pts)
- [ ] US-05.12 — Generated transition-matrix tests (2 pts)
- [ ] US-05.13 — Stateful property-based invariants (5 pts)
- [ ] US-05.14 — Minimal staff model for assignment (3 pts)

## 1. Objective

Implement the Kanban rules of Constitution Article VIII as pure, deterministic domain code:
projects, cards, the authoritative state machine, WIP limits, Definition of Ready/Done, the
review gate, rework, blocking, permissions, and a minimal staff model so cards can be assigned.
Nothing in this WP performs I/O; everything is proven by Given/When/Then and property tests.

## 2. Scope

**In:** `domain/shared`, `domain/kanban`, minimal `domain/staff` (default staff, eligibility);
decide/evolve functions; all Kanban events of Constitution Appendix B for projects and cards;
error codes of skill `enforcing-kanban-workflow`; permission policy §5.9; property tests.

**Out:** handlers, persistence wiring, API (WP06); staff customization (WP09); assignment
scoring (WP17 — the domain only validates eligibility); agents (WP15+).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D05.1 | Shared kernel | Base types used by every context: ids, clock protocol, `ValueObject`, `DomainEvent`, `DomainError`, `Actor` | Unit tests; import-linter keeps it free of infrastructure | US-05.01, US-05.02 |
| D05.2 | Project aggregate | Create/rename/archive/restore; key rules; TODO limit 1–5; card numbering | GWT tests for every command and error | US-05.03, US-05.04 |
| D05.3 | Card aggregate | Full state machine of §8.5 with DoR/DoD, WIP semantics §8.6, rework §8.7, blocking §8.8 | GWT tests for every allowed transition and guard | US-05.05 – US-05.10 |
| D05.4 | Permission policy | Actor × command matrix §5.9 and the full error catalog | Matrix-driven tests | US-05.11 |
| D05.5 | Invariant suite | Generated forbidden-transition tests + Hypothesis stateful machine (E17 domain part) | Property suite with ≥ 500 examples green | US-05.12, US-05.13 |
| D05.6 | Minimal staff model | `Office` with default staff (7 agents), agent eligibility and per-agent DOING limit inputs | GWT tests; `OfficeInitialized` event | US-05.14 |

## 4. User stories

### D05.1 — Shared kernel

#### US-05.01 — Shared kernel: ids, clock, base value object, event and error

- [ ] **US-05.01 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a domain developer, I want common base types, so that every bounded context
  models values, events and errors the same way.
- **Acceptance criteria:**
  - [ ] AC1 — Given `ValueObject`, when a subclass is instantiated with an extra field or
    mutated, then validation fails / mutation raises (frozen, `extra="forbid"`, strict).
  - [ ] AC2 — Given `DomainEvent`, when a subclass is declared, then it has `type: Literal[...]`
    and `version: Literal[n]` and is frozen.
  - [ ] AC3 — Given `DomainError`, when a subclass is declared, then it has a stable `code`
    string equal to the class name and a human `message`.
  - [ ] AC4 — Given `Clock` and `IdGenerator` protocols, when the domain needs time or ids, then
    it receives them via a `DecisionContext`; the domain never calls `datetime.now()`.
  - [ ] AC5 — Given `Actor`, when created, then it is one of `agent(id)`, `user`, `system(name)`.
- **Tasks:**
  - [ ] `domain/shared/{values.py,events.py,errors.py,actor.py,context.py,ids.py}`.
  - [ ] Fake clock and sequential id generator in `tests/support/`.
- **Tests:** unit tests per AC.
- **Done when:** used by US-05.02.

#### US-05.02 — Kanban value objects

- [ ] **US-05.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a domain developer, I want self-validating Kanban values, so that illegal values
  cannot exist (make illegal states unrepresentable).
- **Acceptance criteria:**
  - [ ] AC1 — `ProjectKey` accepts `^[A-Z]{2,6}$` only.
  - [ ] AC2 — `CardId` is `<KEY>-<n>` with `n ≥ 1`, parsed and formatted round-trip.
  - [ ] AC3 — `Column`, `CardType`, `Priority` are `StrEnum`s with exactly the Constitution values.
  - [ ] AC4 — `Estimate` accepts {1, 2, 3, 5, 8} only; 13 fails with a message suggesting a split.
  - [ ] AC5 — `CardTitle` 5–100 chars; `AcceptanceCriterion` non-empty text with id; a card
    holds 1–10 criteria.
  - [ ] AC6 — `CompetenceTag` belongs to the union of role tag sets of Constitution §5.4–5.6.
  - [ ] AC7 — `Rank` is a fractional index string with `between(a, b)` producing a value
    strictly between (property test).
- **Tasks:** `domain/kanban/values.py`; rank algorithm.
- **Tests:** unit + Hypothesis for `Rank.between` and `CardId` round trip.
- **Done when:** all values used by aggregates.

### D05.2 — Project aggregate

#### US-05.03 — Project lifecycle: create, rename, archive, restore

- [ ] **US-05.03 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to create and manage projects, so that each piece of work has
  its own board.
- **Acceptance criteria:**
  - [ ] AC1 — Given no project with key `SHOP`, when `CreateProject(key=SHOP, name=…)`, then
    `ProjectCreated` with default settings (`todo_limit=3`, `next_card_number=1`).
  - [ ] AC2 — Given an existing key (case-insensitive), when creating, then
    `ProjectKeyAlreadyUsed` (the uniqueness check uses a key index passed in the context).
  - [ ] AC3 — Given a project, when `RenameProject`, then `ProjectRenamed`; the key never
    changes (no command exists to change it).
  - [ ] AC4 — Given an active project, when `ArchiveProject`, then `ProjectArchived`; any card
    command on an archived project returns `ProjectArchived` error; `RestoreProject` reverses.
  - [ ] AC5 — Given `evolve` folded over the events, then the state equals the expected
    snapshot.
- **Tasks:** `domain/kanban/project.py` with `decide_*` and `evolve`; events in `events.py`.
- **Tests:** GWT tests per AC.
- **Done when:** all AC green.

#### US-05.04 — TODO limit setting and card numbering

- [ ] **US-05.04 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to tune the TODO limit per project and get sequential card ids,
  so that the board matches my team's capacity and ids are predictable.
- **Acceptance criteria:**
  - [ ] AC1 — Given a project, when `ChangeTodoLimit(4)`, then `ProjectSettingsChanged` with
    before/after; values outside 1–5 return `InvalidTodoLimit`.
  - [ ] AC2 — Given `next_card_number = 7`, when a card is created, then it gets `KEY-7` and
    the project's counter becomes 8 (`CardNumberAllocated` folded into `CardCreated` handling
    via a project event).
  - [ ] AC3 — Given a lowered limit below the current TODO count, when applied, then it is
    accepted; existing TODO cards stay; pulls are refused until under the limit.
- **Tasks:** extend project aggregate; document numbering in the Glossary if needed.
- **Tests:** GWT tests.
- **Done when:** all AC green.

### D05.3 — Card aggregate

#### US-05.05 — Create, edit and rank cards

- [ ] **US-05.05 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user or the PM, I want to create, edit and order Backlog cards, so that the
  Backlog expresses what matters most.
- **Acceptance criteria:**
  - [ ] AC1 — Given valid fields, when `CreateCard`, then `CardCreated` in `BACKLOG` with
    `rework_count=0`, `blocked=false`, `assignee=None`, `created_by=actor`.
  - [ ] AC2 — Given missing title/criteria/estimate, when creating, then it is still accepted
    into BACKLOG (drafts allowed) but marked not Ready (DoR evaluated in US-05.10).
  - [ ] AC3 — Given a card, when `EditCard(fields)`, then `CardEdited` contains a field-level
    diff; editing `id`, `column` or `assignee` through edit is impossible.
  - [ ] AC4 — Given cards in a column, when `RankCard(between=a,b)`, then `CardRanked` with a
    rank strictly between neighbors.
  - [ ] AC5 — Given an agent actor, when editing, then only `tasks` and notes fields are
    accepted (detailed by the policy in US-05.11).
- **Tasks:** `domain/kanban/card.py` (state, decide, evolve); events `CardCreated`, `CardEdited`,
  `CardRanked`.
- **Tests:** GWT tests.
- **Done when:** all AC green.

#### US-05.06 — Pull, unassign and reassign with the WIP limit

- [ ] **US-05.06 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the PM (or the user), I want to pull a Ready card into TODO and assign it, but
  never beyond the TODO limit, so that work in progress stays small (Constitution §8.6).
- **Acceptance criteria:**
  - [ ] AC1 — Given TODO count 2 of 3 and a Ready card, when `PullCard(assignee)`, then
    `CardPulled` with assignee and (optional) score breakdown; card in TODO.
  - [ ] AC2 — Given TODO count 3 of 3, when pulling, then `WipLimitReached` and no event (E1).
  - [ ] AC3 — Given a card not Ready, when pulling, then `CardNotReady` listing missing items.
  - [ ] AC4 — Given an assignee not eligible (disabled, unknown, wrong role without fallback),
    when pulling, then `NoEligibleAssignee`.
  - [ ] AC5 — Given a TODO card, when `UnassignCard(reason)`, then `CardUnassigned` and the card
    returns to BACKLOG; when `ReassignCard(to, reason)`, then `CardReassigned` in TODO.
  - [ ] AC6 — Given the project and card decisions combined in one application service, when
    two pulls race, then optimistic concurrency on the project version guarantees at most the
    limit (verified in WP06 integration; here: decision uses the project TODO count from state).
- **Tasks:** cross-aggregate decision `decide_pull(project, card, staff, command, ctx)` in a
  domain service; events.
- **Tests:** GWT tests incl. E1.
- **Done when:** all AC green.

#### US-05.07 — Start, submit and hand back work

- [ ] **US-05.07 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As an assignee, I want to start my card, deliver it to review, or hand it back, so
  that the board shows what I am doing (per-agent DOING limit = 1).
- **Acceptance criteria:**
  - [ ] AC1 — Given a TODO card assigned to A and A has no card in DOING, when A
    `StartWork`, then `WorkStarted`; card in DOING.
  - [ ] AC2 — Given A already has a card in DOING, when starting another, then
    `AgentAlreadyBusy`.
  - [ ] AC3 — Given an actor other than the assignee (and not the user), when starting, then
    `NotAssignee`.
  - [ ] AC4 — Given a DOING card without deliverables, when `SubmitWork`, then
    `DeliverableRequired`; with ≥ 1 deliverable (`DeliverableAttached` earlier), then
    `WorkSubmitted`; card in REVIEW.
  - [ ] AC5 — Given a DOING card, when `HandBackWork` without reason, then `ReasonRequired`;
    with reason, then `WorkHandedBack`; card in TODO even if TODO is full (§8.6.3).
  - [ ] AC6 — Given `AttachDeliverable` on a DOING card by the assignee, then
    `DeliverableAttached` with a typed deliverable (Appendix A union).
- **Tasks:** card decisions; `TasksPlanned` event for task lists.
- **Tests:** GWT tests.
- **Done when:** all AC green.

#### US-05.08 — Approve, reject and reopen with the review gate

- [ ] **US-05.08 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As a reviewer, I want approval and rejection rules enforced, so that nothing
  reaches DONE without a real review by someone else (Constitution §8.4, E3, E4).
- **Acceptance criteria:**
  - [ ] AC1 — Given a REVIEW card, when the assignee tries to review, then
    `ReviewerIsAssignee` (E3).
  - [ ] AC2 — Given a review with all criteria `pass`, when `ApproveCard`, then `CardApproved`
    and card in DONE; with any `fail` or open blocker/major note, then
    `DefinitionOfDoneNotMet`.
  - [ ] AC3 — Given a review with only `minor`/`nit` notes, when `RejectCard`, then
    `RejectionRequiresMajorNote` (E10 domain part).
  - [ ] AC4 — Given a valid rejection, when applied, then `CardRejected`, card in TODO,
    assignee unchanged, `rework_count += 1`, TODO may exceed the limit.
  - [ ] AC5 — Given a DONE card, when the user `ReopenCard(reason)`, then `CardReopened` into
    TODO; any non-user actor gets `ActorNotPermitted`.
  - [ ] AC6 — Given a card in any column other than REVIEW, when approving or rejecting, then
    `TransitionNotAllowed` (E4 family).
  - [ ] AC7 — Given `ReviewStarted` by a reviewer, when recorded, then it stores
    `reviewer_role` and `is_fallback`.
- **Tasks:** review value objects (criteria results, notes with severity); decisions; events.
- **Tests:** GWT tests incl. E3, E4.
- **Done when:** all AC green.

#### US-05.09 — Block, unblock, archive and restore cards

- [ ] **US-05.09 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As an assignee or the user, I want to flag blockers and archive cards, so that
  problems are visible and mistakes reversible.
- **Acceptance criteria:**
  - [ ] AC1 — `BlockCard(reason)` by the assignee or user → `CardBlocked`; card stays in its
    column; blocked TODO cards still count toward the limit.
  - [ ] AC2 — `UnblockCard(resolution)` → `CardUnblocked`.
  - [ ] AC3 — `ArchiveCard` by user only → `CardArchived` (soft delete); `RestoreCard` reverses;
    archiving a TODO card frees a slot.
- **Tasks:** decisions and events.
- **Tests:** GWT tests.
- **Done when:** all AC green.

#### US-05.10 — Dependencies and Definition of Ready

- [ ] **US-05.10 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the PM, I want readiness computed by the domain, so that only complete,
  unblocked cards are pulled (Constitution §8.3).
- **Acceptance criteria:**
  - [ ] AC1 — `is_ready(card, dependency_columns, eligible_assignees)` returns ok or the list
    of missing items: title, description, criteria, estimate, priority, competence tag,
    unfinished `blocks` dependencies, blocked flag, no eligible assignee.
  - [ ] AC2 — `AddDependency(card, on, kind)` rejects self-dependency and cycles of `blocks`
    (`DependencyCycle`).
  - [ ] AC3 — `RemoveDependency` emits `CardEdited` with dependency diff.
- **Tasks:** readiness function; cycle detection over provided dependency graph.
- **Tests:** unit + Hypothesis (no cycle ever accepted).
- **Done when:** used by `decide_pull`.

### D05.4 — Permission policy

#### US-05.11 — Actor permission policy and error catalog

- [ ] **US-05.11 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want the permission matrix of Constitution §5.9 encoded
  once, so that every actor — agent or human — obeys the same rules.
- **Acceptance criteria:**
  - [ ] AC1 — `ActorPolicy.allows(actor, role, command, card)` implements every row of §5.9
    (own/fallback qualifiers included).
  - [ ] AC2 — A denied command returns `ActorNotPermitted` with actor, role and command.
  - [ ] AC3 — The error catalog contains exactly: `TransitionNotAllowed`, `WipLimitReached`,
    `CardNotReady`, `NoEligibleAssignee`, `AgentAlreadyBusy`, `NotAssignee`,
    `ReviewerIsAssignee`, `RejectionRequiresMajorNote`, `DefinitionOfDoneNotMet`,
    `DeliverableRequired`, `ReasonRequired`, `ActorNotPermitted`, `ConcurrencyConflict`,
    `ProjectKeyAlreadyUsed`, `ProjectArchived`, `InvalidTodoLimit`, `DependencyCycle`, each with
    an English message template.
  - [ ] AC4 — The matrix is data (a table in code) and a test renders it to Markdown and compares
    with Constitution §5.9 (drift detector).
- **Tasks:** `domain/kanban/policy.py`, `errors.py`.
- **Tests:** table-driven tests over the matrix.
- **Done when:** all decisions consult the policy.

### D05.5 — Invariant suite

#### US-05.12 — Generated transition-matrix tests

- [ ] **US-05.12 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a tech lead, I want every (from, to) column pair tested automatically, so that
  no forbidden transition can slip in.
- **Acceptance criteria:**
  - [ ] AC1 — For each of the 25 column pairs, a parametrized test asserts allowed pairs
    succeed under valid guards and all others return `TransitionNotAllowed`.
  - [ ] AC2 — The allowed set equals the diagram of Constitution §8.5 (single source table).
- **Tasks:** parametrized test module.
- **Tests:** itself.
- **Done when:** green.

#### US-05.13 — Stateful property-based invariants

- [ ] **US-05.13 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want random command sequences to never break the core
  invariants, so that the rules hold in every situation (E17 domain part).
- **Acceptance criteria:**
  - [ ] AC1 — A Hypothesis `RuleBasedStateMachine` issues random commands from random actors
    over 1 project, ≤ 20 cards, default staff.
  - [ ] AC2 — Invariant: no successful pull ever leaves `count(TODO) > todo_limit` unless the
    excess comes from rework/hand-back/reopen events.
  - [ ] AC3 — Invariant: every DONE card has a `CardApproved` by a reviewer ≠ assignee.
  - [ ] AC4 — Invariant: per agent, cards in DOING ≤ 1.
  - [ ] AC5 — Invariant: folding events always reproduces the machine's model state.
  - [ ] AC6 — CI profile runs ≥ 500 examples; nightly ≥ 5 000.
- **Tasks:** state machine in `tests/property/test_kanban_machine.py`; Hypothesis profiles.
- **Tests:** itself.
- **Done when:** green in CI and nightly.

### D05.6 — Minimal staff model

#### US-05.14 — Minimal staff model for assignment

- [ ] **US-05.14 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want the default office staff to exist from the first boot, so that
  cards can be assigned before staff customization exists (WP09).
- **Acceptance criteria:**
  - [ ] AC1 — `InitializeOffice` on an empty office emits `OfficeInitialized` with the 7 default
    agents of Constitution §5.1 (names, roles, default faces of Appendix D, slots, home desks,
    competence tags).
  - [ ] AC2 — `InitializeOffice` twice returns `OfficeAlreadyInitialized`.
  - [ ] AC3 — `eligible_assignees(card_type, staff)` returns enabled agents of the primary role,
    or fallback executors in the order of Constitution §6.3, flagged `is_fallback`.
  - [ ] AC4 — The PM is never an eligible assignee for execution cards.
- **Tasks:** `domain/staff/office.py`, `agent.py` (minimal), events.
- **Tests:** GWT tests.
- **Done when:** used by `decide_pull`.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP05 closing: Kanban domain`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; `domain` coverage ≥ 95 % lines and branches.
- [ ] Constitution Appendix B updated for any event added or renamed; Glossary updated.
- [ ] Skill `enforcing-kanban-workflow` matches the implemented error names.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Cross-aggregate pull decision leaks into handlers | Domain service `decide_pull` owns the rule; handlers only load and save |
| Permission matrix diverges from the Constitution | Drift-detector test (US-05.11 AC4) |
| Property tests become slow | Separate CI and nightly profiles |

## 7. Blockers

None.

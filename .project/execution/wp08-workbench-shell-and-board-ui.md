# WP08 — Workbench Shell & Board UI

| Field        | Value |
| ------------ | ----- |
| Milestone    | M1 — Kickstart |
| Status       | READY |
| Depends on   | WP06, WP07 |
| Enables      | WP09, WP10, WP11, WP14, WP16, WP18, WP22 (manual review UI) |
| Constitution | §4.1–4.3.2, §8.5–8.9, §14.9, §18.6, Appendix E (E1–E4 through the UI) |
| Guides       | [FRONTEND.md](../../.docs/FRONTEND.md) · [DESIGN.md](../../.docs/DESIGN.md) §5.5, §10–11 |
| Skills       | `designing-amiga-ui`, `enforcing-kanban-workflow`, `delivering-features`, `writing-adrs` |
| Estimate     | 42 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-08.01 — Workbench desktop with icons and window registry (3 pts)
- [ ] US-08.02 — Deep-link routing to windows (2 pts)
- [ ] US-08.03 — Desktop and window layout persistence (2 pts)
- [ ] US-08.04 — Projects List window (list and icon views) (3 pts)
- [ ] US-08.05 — Create, rename, archive and restore projects (3 pts)
- [ ] US-08.06 — Board window with columns and card tiles (5 pts)
- [ ] US-08.07 — Drag-and-drop moves with refusals (5 pts)
- [ ] US-08.08 — Keyboard moves ("Move to…") (3 pts)
- [ ] US-08.09 — Pull and assign requester (3 pts)
- [ ] US-08.10 — Live board updates across tabs and connection state (2 pts)
- [ ] US-08.11 — Card Detail window: view and edit (5 pts)
- [ ] US-08.12 — Manual review form (user as reviewer) (3 pts)
- [ ] US-08.13 — E2E job and board scenarios (3 pts)

## 1. Objective

Assemble My Workbench for M1: the desktop with icons, deep links and persisted layout; the
Projects List; the Trello-style Kanban Board with drag-and-drop and keyboard moves that obey the
domain; and the Card Detail window — all live-updating from events, all built from the WP07 kit.

## 2. Scope

**In:** `App.vue` shell; desktop icons (placeholders where windows arrive later, shown disabled
with tooltip "Coming in Mx"); router; layout persistence; Projects List; Board; Card Detail;
pull/assign requester; manual review form; Playwright E2E job with E1–E4 through the UI.

**Out:** Logbook (WP10), ADR Library (WP11), Staff Room (WP09), Office (WP14), Inbox (WP16),
PM Chat (WP18), Preferences (WP23).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D08.1 | Workbench shell | Desktop with the nine icons of Constitution §4.2, window registry, deep links, persisted layout | Component + E2E tests; reload restores layout | US-08.01 – US-08.03 |
| D08.2 | Projects List | List/icon views with counters, health, create/rename/archive/restore | E2E create project flow | US-08.04, US-08.05 |
| D08.3 | Kanban Board | Columns, card tiles, WIP header, drag-and-drop + keyboard moves, refusal requesters, pull/assign, live updates | E2E E1–E4 through the UI; two-tab live test | US-08.06 – US-08.10 |
| D08.4 | Card Detail | View/edit all fields, transitions allowed for the actor, manual review | E2E edit + review flows | US-08.11, US-08.12 |
| D08.5 | E2E suite | Playwright `e2e` job against `docker-compose.ci.yml` | Required CI job | US-08.13 |

## 4. User stories

### D08.1 — Workbench shell

#### US-08.01 — Workbench desktop with icons and window registry

- [ ] **US-08.01 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want a Workbench desktop with icons that open windows, so that I
  navigate My Workbench like an Amiga.
- **Acceptance criteria:**
  - [ ] AC1 — The desktop shows the icons of Constitution §4.2 (`Projects`, `Office`, `Inbox`,
    `Talk to PM`, `Staff`, `Logbook`, `Decisions`, `Prefs`, `Trashcan`); icons whose windows are
    not built yet are disabled with an accessible tooltip.
  - [ ] AC2 — A window registry maps icon ids to window components (lazy-loaded with
    `defineAsyncComponent`); double click / Enter opens or focuses the window.
  - [ ] AC3 — The screen title shows `My Workbench` and a live status (`n agents busy · m cards
    in review`) computed from stores.
  - [ ] AC4 — The drive LED reflects the realtime connection state (offline = red).
- **Tasks:** `windows/registry.ts`, `App.vue`, desktop component, status computed.
- **Tests:** component tests; Playwright smoke.
- **Done when:** Projects window opens from its icon.

#### US-08.02 — Deep-link routing to windows

- [ ] **US-08.02 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want URLs that open specific windows, so that I can bookmark a board.
- **Acceptance criteria:**
  - [ ] AC1 — Routes `/`, `/projects/:key/board`, `/cards/:id` open/focus the corresponding
    windows; unknown ids show an error requester and return to `/`.
  - [ ] AC2 — Closing a window navigates back to `/` without reloading.
  - [ ] AC3 — Browser back/forward focuses the previous window.
- **Tasks:** router config; route → window sync composable.
- **Tests:** router unit tests; E2E deep link.
- **Done when:** all AC green.

#### US-08.03 — Desktop and window layout persistence

- [ ] **US-08.03 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want my icon positions and window geometry remembered, so that my
  Workbench looks the same after reload.
- **Acceptance criteria:**
  - [ ] AC1 — Icon positions, open windows, geometry and z-order persist in `localStorage` via
    `usePersistedPrefs` (try/catch; app works without storage).
  - [ ] AC2 — Persisted geometry is clamped to the current screen after scale changes.
  - [ ] AC3 — A "Reset layout" action exists in the Workbench menu.
- **Tasks:** composable, store integration.
- **Tests:** unit tests with storage mocked/throwing.
- **Done when:** reload restores the layout in E2E.

### D08.2 — Projects List

#### US-08.04 — Projects List window (list and icon views)

- [ ] **US-08.04 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to see all my projects with their state, so that I know where
  work is flowing or stuck (Constitution §4.3.1).
- **Acceptance criteria:**
  - [ ] AC1 — List view rows: key, name, counts per column, `TODO n/limit` (orange when ≥),
    last activity, health indicator with text label.
  - [ ] AC2 — Icon view: drawer icons labelled with key and name; toggle via a Cycle gadget.
  - [ ] AC3 — Opening a project (double click / Enter) opens its Board window.
  - [ ] AC4 — Archived projects hidden; "Show archived" checkbox reveals them.
  - [ ] AC5 — The list updates live from project/card events.
- **Tasks:** `windows/projects/ProjectsWindow.vue` and parts.
- **Tests:** component tests; E2E.
- **Done when:** all AC green.

#### US-08.05 — Create, rename, archive and restore projects

- [ ] **US-08.05 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to manage projects from the Projects window.
- **Acceptance criteria:**
  - [ ] AC1 — "New Project" requester with fields name, key (uppercase, 2–6 letters, live
    validation), description; on success the project appears via events.
  - [ ] AC2 — Duplicate key → inline error with the server message (`ProjectKeyAlreadyUsed`).
  - [ ] AC3 — Rename, archive (with confirmation requester) and restore actions available from
    the menu and buttons.
  - [ ] AC4 — The key field is read-only after creation everywhere.
- **Tasks:** form components, commands via store actions.
- **Tests:** component tests; E2E create + duplicate key.
- **Done when:** all AC green.

### D08.3 — Kanban Board

#### US-08.06 — Board window with columns and card tiles

- [ ] **US-08.06 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want a Trello-style board for each project, so that I see every card
  and its state at a glance.
- **Acceptance criteria:**
  - [ ] AC1 — Five columns `BACKLOG · TODO · DOING · REVIEW · DONE` as recessed panels with
    semantic stripe and header count; TODO header `TODO n/limit`, orange when `n ≥ limit`.
  - [ ] AC2 — Card tiles per DESIGN.md §5.5 (type icon, id, priority badge, title ≤ 2 lines,
    assignee mini-portrait placeholder, estimate, rework counter, BLOCKED stripe).
  - [ ] AC3 — "Add card" button in BACKLOG opens a creation form (title, type, description,
    criteria list, estimate, priority, competence tags).
  - [ ] AC4 — 200 cards render with smooth scrolling (Amiga scrollers) and no layout jank.
- **Tasks:** `windows/board/BoardWindow.vue`, `BoardColumn.vue`, `CardTile.vue`, `CardForm.vue`.
- **Tests:** component tests; visual baselines; performance check.
- **Done when:** all AC green.

#### US-08.07 — Drag-and-drop moves with refusals

- [ ] **US-08.07 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to drag cards between columns, and be told clearly when a move is
  not allowed, so that the rules are visible, not mysterious.
- **Acceptance criteria:**
  - [ ] AC1 — Dragging shows a dotted outline (Workbench icon-drag style); dropping sends the
    corresponding command (pull, start, submit, approve/reject via form, hand back, unassign,
    reopen, rank within column).
  - [ ] AC2 — The card moves only when the resulting event arrives (no optimistic move).
  - [ ] AC3 — Forbidden drops snap back with the visual DisplayBeep (screen border flash, 2
    frames) and a requester showing the human message for the error code (E1, E4).
  - [ ] AC4 — Drops onto TODO from BACKLOG open the pull/assign requester (US-08.09).
  - [ ] AC5 — Columns not allowed for the dragged card (from `allowedTransitions`) are shown as
    non-targets during the drag.
- **Tasks:** drag composable (pointer events, no HTML5 DnD quirks), command mapping table.
- **Tests:** component tests; E2E E1 and E4 via drag.
- **Done when:** all AC green.

#### US-08.08 — Keyboard moves ("Move to…")

- [ ] **US-08.08 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a keyboard user, I want to move cards without dragging.
- **Acceptance criteria:**
  - [ ] AC1 — Each card tile is focusable; arrow keys move focus within/between columns.
  - [ ] AC2 — `M` or the "Move to…" Cycle gadget lists only allowed target columns; Enter sends
    the command; refusals show the same requester as drag.
  - [ ] AC3 — `Alt+↑/↓` reorders within a column (rank command).
  - [ ] AC4 — Screen readers announce card moves through a live region.
- **Tasks:** keyboard handlers, live region.
- **Tests:** Playwright keyboard-only E2E.
- **Done when:** all AC green.

#### US-08.09 — Pull and assign requester

- [ ] **US-08.09 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user (acting as PM in M1), I want to choose who gets a card when I pull it.
- **Acceptance criteria:**
  - [ ] AC1 — The requester lists eligible agents (from the server, incl. fallback flag) with
    name, role, face placeholder and current load.
  - [ ] AC2 — If the card is not Ready, the requester lists missing items and offers "Edit card".
  - [ ] AC3 — Confirm sends `PullCard`; errors (WIP, not ready, no eligible assignee) shown inline.
- **Tasks:** requester component; eligibility query (`GET /api/cards/{id}/eligible-assignees`
  added to WP06 API if missing, with ADR note).
- **Tests:** component tests; E2E pull flow.
- **Done when:** all AC green.

#### US-08.10 — Live board updates across tabs and connection state

- [ ] **US-08.10 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want changes made elsewhere to appear immediately, so that the board
  is always true.
- **Acceptance criteria:**
  - [ ] AC1 — Two browser tabs: a move in tab A appears in tab B in ≤ 500 ms p95 locally.
  - [ ] AC2 — On disconnect the LED turns red and the board shows an "Offline — reconnecting"
    banner; on reconnect with `resync`, the board refetches.
- **Tasks:** wire realtime events to board; banner component.
- **Tests:** E2E with two contexts; latency assertion.
- **Done when:** all AC green.

### D08.4 — Card Detail

#### US-08.11 — Card Detail window: view and edit

- [ ] **US-08.11 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to open a card and see and edit everything about it.
- **Acceptance criteria:**
  - [ ] AC1 — Tabs: Overview (title, type, description Markdown rendered safely, criteria,
    priority, estimate, tags, labels, dependencies), Work (tasks, deliverables), Reviews,
    History (placeholder until WP10).
  - [ ] AC2 — Edit mode sends `EditCard` with only changed fields; conflicts (stale version) show
    a requester offering reload.
  - [ ] AC3 — Transition buttons reflect `allowedTransitions`; blocked toggle with reason.
  - [ ] AC4 — Markdown rendering escapes HTML (no XSS); links open in a new tab with
    `rel="noopener"`.
- **Tasks:** `windows/card/CardWindow.vue` and tabs; Markdown renderer choice → ADR (library
  must be added to STACK.md, latest stable).
- **Tests:** component tests; XSS test; E2E edit.
- **Done when:** all AC green.

#### US-08.12 — Manual review form (user as reviewer)

- [ ] **US-08.12 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to review a card myself, so that cards can reach DONE before the
  QA agent exists (and later as the final fallback reviewer).
- **Acceptance criteria:**
  - [ ] AC1 — For a REVIEW card, a form lists each acceptance criterion with pass/fail/
    not-verifiable and evidence text, plus numbered notes with severity.
  - [ ] AC2 — "Approve" enabled only when all criteria pass (or justified not-verifiable) and no
    blocker/major note; "Request changes" enabled only with ≥ 1 blocker/major note.
  - [ ] AC3 — Server errors (`ReviewerIsAssignee`, `RejectionRequiresMajorNote`,
    `DefinitionOfDoneNotMet`) are shown inline.
- **Tasks:** review form components.
- **Tests:** component tests; E2E approve and reject.
- **Done when:** all AC green.

### D08.5 — E2E suite

#### US-08.13 — E2E job and board scenarios

- [ ] **US-08.13 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want the M1 scenarios to run end to end on every PR.
- **Acceptance criteria:**
  - [ ] AC1 — CI job `e2e` starts the stack with `docker-compose.ci.yml`, runs Playwright, uploads
    traces/videos on failure.
  - [ ] AC2 — Scenarios: create project; create cards; E1 (4th pull refused); E3 (assignee
    cannot approve — via API helper since UI hides it); E4 (TODO → DONE refused); full happy path
    BACKLOG → DONE with manual review; two-tab live update.
  - [ ] AC3 — Each scenario is independent (fresh project key per test).
- **Tasks:** Playwright config for E2E project, fixtures, CI job.
- **Tests:** itself.
- **Done when:** `e2e` required in branch protection.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP08 closing: Workbench shell & board UI`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; axe zero violations on all new windows; visual baselines added.
- [ ] Initial JS gz measured and recorded (budget ≤ 350 KB tracked).
- [ ] M1 exit criteria demonstrated; `v0.2.0` tagged after WP04–WP08 are DONE.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Drag-and-drop accessibility | Keyboard "Move to…" parity (US-08.08) |
| UI duplicating domain rules | Use `allowedTransitions` and server errors only |
| Bundle grows with Markdown renderer | Choose a small, maintained library; lazy-load in Card window |

## 7. Blockers

None.

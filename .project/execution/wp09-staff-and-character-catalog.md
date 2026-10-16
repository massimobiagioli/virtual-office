# WP09 — Staff & Character Catalog

| Field        | Value |
| ------------ | ----- |
| Milestone    | M2 — Workbench |
| Status       | READY |
| Depends on   | WP05 (minimal staff), WP06 (API, projections), WP08 (shell) |
| Enables      | WP12 (faces to draw), WP14 (agents in the office), WP15 (agent runtime), WP17 (eligibility) |
| Constitution | Article V (§5.1–5.2), Article VI, §10.2, Appendix D, Appendix E (E15, E16 without animation) |
| Guides       | [BACKEND.md](../../.docs/BACKEND.md) · [FRONTEND.md](../../.docs/FRONTEND.md) · [DESIGN.md](../../.docs/DESIGN.md) §7.1 · [POSTGRES.md](../../.docs/POSTGRES.md) |
| Skills       | `authoring-office-agents`, `tracing-events`, `designing-amiga-ui`, `delivering-features`, `writing-adrs` |
| Estimate     | 41 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-09.01 — Catalog schema and character model (3 pts)
- [ ] US-09.02 — Character seed job from versioned files (3 pts)
- [ ] US-09.03 — Characters API with caching headers (2 pts)
- [ ] US-09.04 — Rename an agent (3 pts)
- [ ] US-09.05 — Change an agent's face (2 pts)
- [ ] US-09.06 — Enable and disable agents with safe hand-over (5 pts)
- [ ] US-09.07 — Edit developer competence tags (2 pts)
- [ ] US-09.08 — Pause and resume a single agent (2 pts)
- [ ] US-09.09 — Staff endpoints and extended staff projection (3 pts)
- [ ] US-09.10 — Core catalog client with anti-corruption layer (3 pts)
- [ ] US-09.11 — Staff Room window (5 pts)
- [ ] US-09.12 — Portrait picker (3 pts)
- [ ] US-09.13 — Disable flows and duplicate-face warning in the UI (3 pts)
- [ ] US-09.14 — Faces on board tiles and agent cards (2 pts)

## 1. Objective

Let the user shape the office: rename agents, choose faces from the finite Character Catalog,
enable or disable agents (with a safe hand-over of work), tune developer specializations and
pause agents — all as domain events, served by the `agents-catalog` service for characters and
by `core` for the staff, and presented in the Staff Room window.

## 2. Scope

**In:** `agents-catalog` character schema, seed, API; `core` catalog client; staff commands and
events; staff projection; Staff Room window; portrait picker; faces in tiles.

**Out:** pixel-art final portraits (WP12 — placeholders with the right ids and sizes here);
office movement on enable/disable (WP13/WP14); role definitions and prompts (WP15).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D09.1 | Character catalog service | 16 face ids (Appendix D) stored, seeded from files, served with ETag | API tests; seed idempotent | US-09.01 – US-09.03 |
| D09.2 | Staff customization domain | Rename, face, enable/disable with Finish first / Hand back now, tags, pause/resume; PM rules | GWT tests incl. E15, E16 | US-09.04 – US-09.08 |
| D09.3 | Staff API & catalog client | Staff endpoints, projection with history of names, ACL client to the catalog | API + contract tests | US-09.09, US-09.10 |
| D09.4 | Staff Room UI | Window with list, detail, picker, disable flows, warnings; faces in tiles | E2E E15/E16 (no animation) | US-09.11 – US-09.14 |

## 4. User stories

### D09.1 — Character catalog service

#### US-09.01 — Catalog schema and character model

- [ ] **US-09.01 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the catalog service, I want a typed character model and table, so that faces are
  a stable, finite set with immutable ids.
- **Acceptance criteria:**
  - [ ] AC1 — `Character` model: `face_id` (`face-01`…`face-16`, immutable), `archetype`,
    `visual_notes`, `portrait_32`, `portrait_16`, `sprite_sheet`, `atlas`, `deprecated` flag.
  - [ ] AC2 — Migration creates `catalog.characters` with PK `face_id`; runtime role
    `catalog_app` has `SELECT` only; the seed uses the owner role.
  - [ ] AC3 — A face id can be deprecated but never deleted or renamed (constraint + test).
- **Tasks:** domain model, migration, repository.
- **Tests:** unit + integration.
- **Done when:** table exists in the compose stack.

#### US-09.02 — Character seed job from versioned files

- [ ] **US-09.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a maintainer, I want characters defined in `catalog/characters/characters.yaml`
  and loaded by a seed job, so that files are the source of truth and reviewable in PRs.
- **Acceptance criteria:**
  - [ ] AC1 — The YAML lists the 16 archetypes of Constitution Appendix D with asset paths.
  - [ ] AC2 — `catalog-seed` validates the file with Pydantic and upserts rows; running twice
    changes nothing (idempotent).
  - [ ] AC3 — Removing a face from the file fails the seed with a message (deprecate instead).
- **Tasks:** YAML, seed CLI, compose job command.
- **Tests:** unit tests of validation; integration of idempotency.
- **Done when:** the seed job completes in compose.

#### US-09.03 — Characters API with caching headers

- [ ] **US-09.03 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As `core`, I want to read characters with conditional requests, so that the catalog
  is cheap to query.
- **Acceptance criteria:**
  - [ ] AC1 — `GET /characters` and `GET /characters/{faceId}` return `ApiModel` DTOs.
  - [ ] AC2 — Responses carry `ETag`; `If-None-Match` returns 304.
  - [ ] AC3 — Unknown face → 404 problem.
- **Tasks:** router, ETag helper (content hash).
- **Tests:** API tests.
- **Done when:** documented in the catalog OpenAPI.

### D09.2 — Staff customization domain

#### US-09.04 — Rename an agent

- [ ] **US-09.04 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to rename any agent, so that the office feels like my team (E15).
- **Acceptance criteria:**
  - [ ] AC1 — `RenameAgent(agent, name)` → `AgentRenamed{old_name, new_name}`; `agent_id`
    unchanged.
  - [ ] AC2 — Names 1–20 chars from letters, digits, space, `-`, `'`, `.`; trimmed; unique in the
    office case-insensitively (`AgentNameTaken`).
  - [ ] AC3 — History keeps all names; projections and future logs use the new name.
- **Tasks:** `domain/staff` decisions; `PersonaName` value object.
- **Tests:** GWT incl. E15 domain part.
- **Done when:** all AC green.

#### US-09.05 — Change an agent's face

- [ ] **US-09.05 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to choose a face from the catalog for each agent.
- **Acceptance criteria:**
  - [ ] AC1 — `ChangeAgentFace(agent, face_id)` → `AgentFaceChanged{old, new}`.
  - [ ] AC2 — Unknown or deprecated face ids → `UnknownFace` (catalog ids passed via context).
  - [ ] AC3 — Duplicate faces are allowed (the UI warns, US-09.13).
- **Tasks:** decision, `FaceId` value object.
- **Tests:** GWT.
- **Done when:** all AC green.

#### US-09.06 — Enable and disable agents with safe hand-over

- [ ] **US-09.06 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to choose which agents work in the office, without losing work,
  so that I can run with only some of them (E16).
- **Acceptance criteria:**
  - [ ] AC1 — `DisableAgent(agent, mode)` with mode `finish_first` → `AgentDisableScheduled`;
    the agent stops receiving new assignments and is disabled (`AgentDisabled`) when its DOING
    card leaves DOING.
  - [ ] AC2 — Mode `hand_back_now` → the DOING card goes to TODO unassigned with a system note
    (`WorkHandedBack` by `system`), queued TODO cards are unassigned, then `AgentDisabled` (E16).
  - [ ] AC3 — The PM cannot be disabled (`ProjectManagerRequired`).
  - [ ] AC4 — `EnableAgent` → `AgentEnabled`; the agent becomes eligible again.
  - [ ] AC5 — When no executor is enabled, an `OfficeHasNoExecutors` state flag is exposed for the
    PM (used in WP17) and the UI.
- **Tasks:** cross-aggregate service (office + cards), events.
- **Tests:** GWT incl. E16; property test: disabling never leaves cards assigned to a disabled
  agent after completion.
- **Done when:** all AC green.

#### US-09.07 — Edit developer competence tags

- [ ] **US-09.07 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want to specialize developers (e.g. frontend vs backend), so that
  assignments match their strengths.
- **Acceptance criteria:**
  - [ ] AC1 — `SetCompetenceTags(agent, tags)` → `AgentCompetenceTagsChanged`; tags must belong to
    the role's tag set (§5.4–5.6); at least one tag.
  - [ ] AC2 — Changes apply to future assignments only.
- **Tasks:** decision.
- **Tests:** GWT.
- **Done when:** all AC green.

#### US-09.08 — Pause and resume a single agent

- [ ] **US-09.08 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to pause one agent, so that I can stop it without disabling it
  (Constitution P4).
- **Acceptance criteria:**
  - [ ] AC1 — `PauseAgent` → `AgentPaused`; `ResumeAgent` → `AgentResumed`.
  - [ ] AC2 — Paused agents are not eligible and their running job (later WPs) stops at the next
    checkpoint; `domainStatus = paused` keeps the previous status for resume.
- **Tasks:** decision, status handling.
- **Tests:** GWT.
- **Done when:** all AC green.

### D09.3 — Staff API & catalog client

#### US-09.09 — Staff endpoints and extended staff projection

- [ ] **US-09.09 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the frontend, I want endpoints for staff customization and a richer projection.
- **Acceptance criteria:**
  - [ ] AC1 — `PATCH /api/agents/{id}` (name, faceId, competenceTags), `POST
    /api/agents/{id}/enable|disable|pause|resume` (disable with `mode`).
  - [ ] AC2 — `GET /api/agents` adds `previousNames`, `disableScheduled`, `paused`, `stats`
    placeholders.
  - [ ] AC3 — Errors mapped to problem details (`AgentNameTaken`, `UnknownFace`,
    `ProjectManagerRequired`).
- **Tasks:** routers, DTOs, projector updates.
- **Tests:** API tests.
- **Done when:** OpenAPI regenerated.

#### US-09.10 — Core catalog client with anti-corruption layer

- [ ] **US-09.10 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As `core`, I want a typed client for the catalog that never leaks catalog DTOs into
  the domain, so that the services stay decoupled.
- **Acceptance criteria:**
  - [ ] AC1 — `infrastructure/catalog/client.py` uses httpx with 5 s timeout, ETag cache, retries
    on connection errors only.
  - [ ] AC2 — It maps DTOs to domain `FaceId`s / `CharacterInfo` read models.
  - [ ] AC3 — Catalog unavailable → readiness reports it; cached data used if present.
- **Tasks:** client, port `CharacterCatalog`, cache.
- **Tests:** respx-mocked tests.
- **Done when:** used by face validation.

### D09.4 — Staff Room UI

#### US-09.11 — Staff Room window

- [ ] **US-09.11 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want a Staff Room window, so that I see and customize my team.
- **Acceptance criteria:**
  - [ ] AC1 — Lists slots (PM, Developer 1, Developer 2, Architect, Designer, Support, QA) with
    portrait, name, role, status, enabled/paused state, current card.
  - [ ] AC2 — Detail panel: rename field, face button (opens picker), competence tags (developers),
    enable/disable, pause/resume.
  - [ ] AC3 — The PM row shows "Always present" and has no disable control.
  - [ ] AC4 — All actions available by keyboard; errors shown inline.
- **Tasks:** `windows/staff/` components; Staff icon enabled.
- **Tests:** component tests; E2E rename.
- **Done when:** all AC green.

#### US-09.12 — Portrait picker

- [ ] **US-09.12 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to pick a face from a grid of Amiga-style portraits.
- **Acceptance criteria:**
  - [ ] AC1 — Requester with a 4×4 grid of 32×32 portraits with archetype names; deprecated faces
    hidden; current face selected.
  - [ ] AC2 — Arrow keys move the selection; Enter confirms; Esc cancels.
  - [ ] AC3 — Faces used by other agents show a small badge with their names.
- **Tasks:** picker component.
- **Tests:** component tests; visual baseline.
- **Done when:** all AC green.

#### US-09.13 — Disable flows and duplicate-face warning in the UI

- [ ] **US-09.13 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want clear choices when disabling a busy agent and a warning on
  duplicate faces.
- **Acceptance criteria:**
  - [ ] AC1 — Disabling an agent with a DOING card opens a requester with *Finish first* and
    *Hand back now* (E16) explaining the consequences.
  - [ ] AC2 — Choosing a face already used shows "Two {Name}s in the office may confuse you" with
    *Use anyway* / *Cancel*.
  - [ ] AC3 — Disabling all executors shows a warning that the PM will not pull cards.
- **Tasks:** requesters wired to commands.
- **Tests:** E2E E16 (without animation).
- **Done when:** all AC green.

#### US-09.14 — Faces on board tiles and agent cards

- [ ] **US-09.14 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want to see who works on what at a glance.
- **Acceptance criteria:**
  - [ ] AC1 — Board tiles show the assignee's 16×16 mini-portrait with the name as accessible text.
  - [ ] AC2 — Renames and face changes update tiles live.
- **Tasks:** component update; asset lookup by face id.
- **Tests:** component tests.
- **Done when:** all AC green.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP09 closing: Staff & character catalog`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; E15 and E16 green (animation parts deferred to WP14).
- [ ] Constitution Appendix B updated with staff events; Glossary terms aligned.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Catalog unavailable at startup | Cached data + readiness reporting; seed before core starts |
| Hand-back races with an agent finishing | Cross-aggregate service in one transaction with optimistic concurrency |
| Placeholder portraits confuse reviewers | Placeholders clearly labeled with face ids until WP12 |

## 7. Blockers

None.

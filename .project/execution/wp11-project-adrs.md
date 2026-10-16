# WP11 — Project ADRs

| Field        | Value |
| ------------ | ----- |
| Milestone    | M2 — Workbench |
| Status       | READY |
| Depends on   | WP05, WP06, WP08 |
| Enables      | WP20 (Architect writes Project ADRs), WP18 (PM cites ADRs) |
| Constitution | §4.3.8, §5.5, §8.4 (item 4), Article XII (§12.4–12.6), Appendix A (`ProjectAdr`), Appendix E (E14 domain part) |
| Guides       | [BACKEND.md](../../.docs/BACKEND.md) · [FRONTEND.md](../../.docs/FRONTEND.md) · [DESIGN.md](../../.docs/DESIGN.md) |
| Skills       | `writing-adrs`, `tracing-events`, `designing-amiga-ui`, `delivering-features` |
| Estimate     | 24 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-11.01 — ADR aggregate: propose, accept, reject, deprecate, supersede (5 pts)
- [ ] US-11.02 — Link ADRs to cards and enforce the architecture DoD (3 pts)
- [ ] US-11.03 — ADR endpoints and projection (3 pts)
- [ ] US-11.04 — Markdown export of Project ADRs (2 pts)
- [ ] US-11.05 — ADR Library window (3 pts)
- [ ] US-11.06 — ADR viewer with status history (3 pts)
- [ ] US-11.07 — ADR editor for the user (3 pts)
- [ ] US-11.08 — Card ↔ ADR linking in the UI (2 pts)

## 1. Objective

Give each project its own decision log: Project ADRs numbered `ADR-<KEY>-NNNN`, with the status
lifecycle of the Constitution, linked to cards, required for completing architecture cards, and
browsable/editable in the ADR Library window — ready for the Architect agent in WP20.

## 2. Scope

**In:** `domain/decisions` aggregate; card link commands; DoD hook; API; projection; Markdown
export; ADR Library window; viewer; editor; linking UI.

**Out:** Architect agent generation (WP20); repository ADRs (they live in `.docs/adr/`).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D11.1 | ADR domain | `Adr` aggregate with per-project numbering, lifecycle, supersede; links with cards; architecture-card DoD requires an Accepted ADR | GWT tests incl. E14 domain part | US-11.01, US-11.02 |
| D11.2 | ADR API | Endpoints, projection, Markdown export | API tests | US-11.03, US-11.04 |
| D11.3 | ADR Library UI | List with status chips and filters, viewer with history, editor with template, linking | E2E create → accept → link flow | US-11.05 – US-11.08 |

## 4. User stories

### D11.1 — ADR domain

#### US-11.01 — ADR aggregate: propose, accept, reject, deprecate, supersede

- [ ] **US-11.01 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user or the Architect, I want to record project decisions with a clear status,
  so that the reasoning behind the project is never lost.
- **Acceptance criteria:**
  - [ ] AC1 — `ProposeAdr(project, title, markdown, related_cards)` → `AdrProposed` with id
    `ADR-<KEY>-NNNN` sequential per project.
  - [ ] AC2 — Allowed transitions: Proposed → Accepted | Rejected; Accepted → Deprecated |
    Superseded; anything else → `AdrTransitionNotAllowed`.
  - [ ] AC3 — `SupersedeAdr(old, new)` requires `new` Accepted and marks `old` Superseded with
    `superseded_by`.
  - [ ] AC4 — Markdown must contain the template sections of Constitution §12.6 (Context,
    Decision, Alternatives Considered, Consequences, Compliance) → else `AdrIncomplete` listing
    missing sections.
  - [ ] AC5 — Edits allowed only while Proposed (`AdrEdited` with diff); Accepted content is
    immutable.
- **Tasks:** `domain/decisions/adr.py`, events, errors; numbering on the project stream.
- **Tests:** GWT tests per transition and error.
- **Done when:** all AC green.

#### US-11.02 — Link ADRs to cards and enforce the architecture DoD

- [ ] **US-11.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the QA or the user, I want architecture cards to be done only with an accepted
  decision, so that architecture work always leaves a record (Constitution §8.4.4).
- **Acceptance criteria:**
  - [ ] AC1 — `LinkAdrToCard(card, adr)` / `UnlinkAdrFromCard` → `CardEdited` (adr ids diff).
  - [ ] AC2 — Approving an `architecture` card without at least one linked Accepted ADR returns
    `DefinitionOfDoneNotMet` with item `accepted ADR` (E14 domain part).
  - [ ] AC3 — ADRs from another project cannot be linked (`AdrProjectMismatch`).
- **Tasks:** extend card DoD with an injected ADR status lookup.
- **Tests:** GWT tests.
- **Done when:** all AC green.

### D11.2 — ADR API

#### US-11.03 — ADR endpoints and projection

- [ ] **US-11.03 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the frontend, I want to list, read and change ADRs over the API.
- **Acceptance criteria:**
  - [ ] AC1 — `GET /api/projects/{key}/adrs?status=` and `GET /api/adrs/{id}` (with status
    history and linked cards).
  - [ ] AC2 — Commands through `/api/commands` (propose, edit, accept, reject, deprecate,
    supersede, link, unlink) with problem details.
  - [ ] AC3 — Projection `projection.adrs` rebuildable.
- **Tasks:** router, DTOs, projector.
- **Tests:** API tests.
- **Done when:** OpenAPI regenerated.

#### US-11.04 — Markdown export of Project ADRs

- [ ] **US-11.04 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want to export a project's ADRs as Markdown, so that I can commit
  them to the project's own repository.
- **Acceptance criteria:**
  - [ ] AC1 — `GET /api/adrs/{id}/markdown` returns the ADR with a header (status, date, deciders,
    related).
  - [ ] AC2 — `GET /api/projects/{key}/adrs/export` returns one Markdown document with an index
    and all ADRs in order.
- **Tasks:** renderer.
- **Tests:** snapshot tests of output.
- **Done when:** all AC green.

### D11.3 — ADR Library UI

#### US-11.05 — ADR Library window

- [ ] **US-11.05 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to browse decisions per project.
- **Acceptance criteria:**
  - [ ] AC1 — Project selector (Cycle), list with id, title, status chip (text + color), author
    face/name, date, linked card count.
  - [ ] AC2 — Status filter; search by title.
  - [ ] AC3 — "Decisions" desktop icon enabled; deep link `/adrs/:id`.
- **Tasks:** `windows/adrs/`.
- **Tests:** component tests.
- **Done when:** all AC green.

#### US-11.06 — ADR viewer with status history

- [ ] **US-11.06 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to read an ADR comfortably and see how its status evolved.
- **Acceptance criteria:**
  - [ ] AC1 — Markdown rendered safely with the readable bitmap font; Mermaid blocks shown as code
    (no external rendering in v1).
  - [ ] AC2 — Status history timeline; superseded ADRs link to their successor.
  - [ ] AC3 — Status actions (accept, reject, deprecate, supersede) available to the user.
- **Tasks:** viewer component.
- **Tests:** component tests; XSS test.
- **Done when:** all AC green.

#### US-11.07 — ADR editor for the user

- [ ] **US-11.07 completed** · **Points:** 3 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want to write a Project ADR myself from the template.
- **Acceptance criteria:**
  - [ ] AC1 — "New ADR" pre-fills the §12.6 template; save → `AdrProposed`.
  - [ ] AC2 — Missing sections highlighted before saving (server rule mirrored).
  - [ ] AC3 — Editing allowed only while Proposed.
- **Tasks:** editor component (multi-line `AmigaTextField` with monospace bitmap font).
- **Tests:** component tests; E2E.
- **Done when:** all AC green.

#### US-11.08 — Card ↔ ADR linking in the UI

- [ ] **US-11.08 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to link decisions and cards from either side.
- **Acceptance criteria:**
  - [ ] AC1 — Card Detail shows linked ADRs (id, title, status) with link/unlink controls.
  - [ ] AC2 — ADR viewer shows linked cards with link/unlink controls.
- **Tasks:** components.
- **Tests:** E2E link flow.
- **Done when:** all AC green.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP11 closing: Project ADRs`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; E14 domain part green.
- [ ] Appendix B ADR events aligned; Glossary "Project ADR" unchanged or amended.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Confusion between repository and Project ADRs | UI labels "Project decision"; ids always carry the project key |
| Template validation too strict for quick notes | Proposed ADRs may be incomplete drafts only in the editor (client-side), server enforces on propose |

## 7. Blockers

None.

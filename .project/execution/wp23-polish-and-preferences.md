# WP23 — Polish & Preferences

| Field        | Value |
| ------------ | ----- |
| Milestone    | M6 — Demo Scene |
| Status       | READY |
| Depends on   | WP22, WP18, WP14 |
| Enables      | WP24 |
| Constitution | §4.3.9, §4.4, §13.5, Article XIV (§14.2, §14.7, §14.9, §14.10), success criterion S7 |
| Guides       | [DESIGN.md](../../.docs/DESIGN.md) · [FRONTEND.md](../../.docs/FRONTEND.md) · [OLLAMA.md](../../.docs/OLLAMA.md) §2 |
| Skills       | `designing-amiga-ui`, `building-office-scene`, `delivering-features`, `writing-adrs` |
| Estimate     | 29 points |

> **No audio, ever** (Constitution §14.10). This WP contains no sound work of any kind; all
> feedback is visual.

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-23.01 — Preferences as office settings events (3 pts)
- [ ] US-23.02 — Preferences window: visual and office sections (3 pts)
- [ ] US-23.03 — Preferences window: AI section (3 pts)
- [ ] US-23.04 — Preferences window: budgets section (2 pts)
- [ ] US-23.05 — Ambient office animations and idle variety (3 pts)
- [ ] US-23.06 — Archetype-specific idle animations (2 pts)
- [ ] US-23.07 — Global error boundary and Guru Meditation (3 pts)
- [ ] US-23.08 — Consistent recoverable error requesters (2 pts)
- [ ] US-23.09 — Correlation ids end to end (2 pts)
- [ ] US-23.10 — Optional CRT overlay (3 pts)
- [ ] US-23.11 — Workbench 2.0 theme finish (2 pts)
- [ ] US-23.12 — Design sign-off (1 pt)

## 1. Objective

Give My Workbench its final polish: a Preferences window (visual, office, AI models per role,
budgets), a livelier office through silent ambient animations and idle variety, an end-to-end error
experience culminating in the Guru Meditation screen, an optional CRT overlay, the finished
Workbench 2.0 theme, and the owner's design sign-off (S7).

## 2. Scope

**In:** preferences domain/API/UI; ambient and idle animations; error boundary, requesters,
correlation ids; CRT filter; theme finish; sign-off.

**Out:** any audio (forbidden); new features beyond the Constitution.

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D23.1 | Preferences | Settings as events; window with Visual, Office, AI, Budgets sections (no Sound section) | E2E change → effect; events in Logbook | US-23.01 – US-23.04 |
| D23.2 | Idle behaviors & ambient life | Silent ambient animations, idle variety, archetype idles; off under reduced motion | Visual baselines; E20 still green | US-23.05, US-23.06 |
| D23.3 | Guru & errors | Error boundary → Guru for fatal client errors; consistent requesters; correlation ids visible and searchable | Fault-injection E2E | US-23.07 – US-23.09 |
| D23.4 | CRT & theme | Optional CRT overlay; wb20 theme complete; S7 sign-off | Baselines; sign-off note in closing ADR | US-23.10 – US-23.12 |

## 4. User stories

### D23.1 — Preferences

#### US-23.01 — Preferences as office settings events

- [ ] **US-23.01 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want my preferences stored as office settings, so that they are
  traceable and survive reinstalls via export.
- **Acceptance criteria:**
  - [ ] AC1 — `ChangeOfficeSettings{theme, scale_override, crt, reduced_motion_override,
    idle_behaviors, animation_speed_default, chat_mode}` → `OfficeSettingsChanged{before, after}`.
  - [ ] AC2 — Per-role model assignment `AssignRoleModel{role, model_tag, provider}` validated
    against `models.lock` / configured providers → `RoleModelAssigned`.
  - [ ] AC3 — No setting related to sound exists (schema test).
- **Tasks:** domain, API `GET/PATCH /api/office/settings`, projection.
- **Tests:** GWT + API tests; schema test.
- **Done when:** all AC green.

#### US-23.02 — Preferences window: visual and office sections

- [ ] **US-23.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to tune how My Workbench looks and how lively the office is.
- **Acceptance criteria:**
  - [ ] AC1 — "Prefs" icon opens the window with sections Visual (theme wb13/wb20, scale auto/×2/×3/
    ×4, CRT on/off, reduced motion override) and Office (default speed, idle behaviors on/off,
    name tags default).
  - [ ] AC2 — Changes apply live; *Use* / *Save* / *Cancel* buttons behave like Workbench
    Preferences (Use = this session, Save = persist as settings event).
- **Tasks:** `windows/prefs/`.
- **Tests:** component + E2E tests.
- **Done when:** all AC green.

#### US-23.03 — Preferences window: AI section

- [ ] **US-23.03 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to choose the model for each role.
- **Acceptance criteria:**
  - [ ] AC1 — A table of roles with a Cycle of allowed models (from the lock and configured
    providers), current concurrency, max tokens per call.
  - [ ] AC2 — Selecting a cloud provider shows a warning that data leaves the machine.
  - [ ] AC3 — Changing a model shows the latest eval pass rate of that model for the role (if
    available).
- **Tasks:** UI, eval summary endpoint.
- **Tests:** component + API tests.
- **Done when:** all AC green.

#### US-23.04 — Preferences window: budgets section

- [ ] **US-23.04 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to see and change budgets per project.
- **Acceptance criteria:**
  - [ ] AC1 — Per project: monthly budget (tokens and USD), used so far, threshold state.
  - [ ] AC2 — Raising a budget resumes scheduling on the next tick (WP17).
- **Tasks:** UI, API.
- **Tests:** E2E.
- **Done when:** all AC green.

### D23.2 — Idle behaviors & ambient life

#### US-23.05 — Ambient office animations and idle variety

- [ ] **US-23.05 completed** · **Points:** 3 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want the office to feel alive even when nothing happens — silently.
- **Acceptance criteria:**
  - [ ] AC1 — Animated tiles (monitor flicker, coffee steam, plant sway) run at low frequency.
  - [ ] AC2 — Idle choreographies extended: coffee, stretch, look at the Kanban wall, chat in pairs
    at the meeting table (bubbles with `…` only, no invented content).
  - [ ] AC3 — All disabled under reduced motion or when idle behaviors are off; E20 still green.
  - [ ] AC4 — No audio (lint and asset checks green).
- **Tasks:** engine idle scheduler additions; renderer animated tiles.
- **Tests:** unit tests (seeded); visual baselines.
- **Done when:** all AC green.

#### US-23.06 — Archetype-specific idle animations

- [ ] **US-23.06 completed** · **Points:** 2 · **Priority:** Could · **ADR:** —
- **Story:** As the user, I want each character to have a little personality.
- **Acceptance criteria:**
  - [ ] AC1 — Optional `idle-special` tag per face (e.g. the cat on face-16, the joystick on
    face-13) used occasionally by the idle scheduler.
  - [ ] AC2 — Missing tags fall back to standard idles.
- **Tasks:** atlas tags (art from WP12 or small additions), scheduler.
- **Tests:** unit tests.
- **Done when:** all AC green.

### D23.3 — Guru & errors

#### US-23.07 — Global error boundary and Guru Meditation

- [ ] **US-23.07 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want fatal errors to be honest, recognizable and recoverable
  (Constitution §4.4).
- **Acceptance criteria:**
  - [ ] AC1 — `app.config.errorHandler` and `window.onerror`/`unhandledrejection` route fatal client
    errors to `AmigaGuru` with error code and correlation id; the error is reported to `core`
    (`POST /api/client-errors`) and logged.
  - [ ] AC2 — Left click / Enter reloads application state (stores reset, realtime resync).
  - [ ] AC3 — Non-fatal errors never show the Guru screen.
- **Tasks:** error boundary, endpoint, logging.
- **Tests:** fault-injection E2E.
- **Done when:** all AC green.

#### US-23.08 — Consistent recoverable error requesters

- [ ] **US-23.08 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want every recoverable error presented the same way.
- **Acceptance criteria:**
  - [ ] AC1 — All windows use `useRequester` error variant with *OK* / *Retry* / *Details*.
  - [ ] AC2 — A lint/grep check forbids `console.error`-only handling in windows.
- **Tasks:** audit and refactor.
- **Tests:** component tests.
- **Done when:** all AC green.

#### US-23.09 — Correlation ids end to end

- [ ] **US-23.09 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As an operator, I want to find the server logs of any error the user sees.
- **Acceptance criteria:**
  - [ ] AC1 — Every request carries `X-Correlation-Id`; requesters and Guru show it; the Logbook
    supports searching by correlation id.
  - [ ] AC2 — DOCKER.md documents how to grep logs by correlation id.
- **Tasks:** client header injection; Logbook filter.
- **Tests:** E2E.
- **Done when:** all AC green.

### D23.4 — CRT & theme

#### US-23.10 — Optional CRT overlay

- [ ] **US-23.10 completed** · **Points:** 3 · **Priority:** Could · **ADR:** —
- **Story:** As a nostalgic user, I want an optional CRT look.
- **Acceptance criteria:**
  - [ ] AC1 — A Pixi filter (scanlines + subtle phosphor bloom) applied after integer upscale in the
    Office View, and a CSS scanline overlay for the Workbench; off by default.
  - [ ] AC2 — Disabled under reduced motion; does not affect hit testing; fps budget still met.
- **Tasks:** filter, CSS overlay, preference wiring.
- **Tests:** visual baselines; perf check.
- **Done when:** all AC green.

#### US-23.11 — Workbench 2.0 theme finish

- [ ] **US-23.11 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want the Workbench 2.0 grey theme to be as polished as 1.3.
- **Acceptance criteria:**
  - [ ] AC1 — Every gallery state and every window has wb20 baselines.
  - [ ] AC2 — Contrast pairs re-verified for wb20.
- **Tasks:** fixes, baselines.
- **Tests:** visual + contrast checks.
- **Done when:** all AC green.

#### US-23.12 — Design sign-off

- [ ] **US-23.12 completed** · **Points:** 1 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want to confirm the result looks like an Amiga 500 Workbench
  (success criterion S7).
- **Acceptance criteria:**
  - [ ] AC1 — A review session over a checklist (DESIGN.md §12) and the full demo; findings become
    stories or are accepted.
  - [ ] AC2 — Sign-off recorded in the WP closing ADR.
- **Tasks:** session, notes.
- **Tests:** none.
- **Done when:** sign-off recorded.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP23 closing: Polish & preferences`) incl. S7 sign-off; story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; no audio anywhere (checks green); E20 still green.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Polish scope creep | Only Constitution-backed items; everything else post-v1 |
| CRT filter hurts performance | Off by default; perf check |

## 7. Blockers

None.

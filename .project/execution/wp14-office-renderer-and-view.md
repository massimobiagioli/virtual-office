# WP14 — Office Renderer & View

| Field        | Value |
| ------------ | ----- |
| Milestone    | M3 — Office |
| Status       | READY |
| Depends on   | WP12, WP13, WP09 (staff), WP06 (realtime) |
| Enables      | WP17 (PM choreographies visible), WP20–WP22 (agent work visible), WP23 (CRT overlay) |
| Constitution | §4.3.3, Article XIII (§13.1, §13.4–13.6), §14.7, §14.9, §14.10, §18.6, Appendix E (E8 visual part, E9 walk, E15/E16 animation, E20) |
| Guides       | [FRONTEND.md](../../.docs/FRONTEND.md) §8 · [STACK.md](../../.docs/STACK.md) §4 · [DESIGN.md](../../.docs/DESIGN.md) §7 |
| Skills       | `building-office-scene`, `designing-amiga-ui`, `delivering-features`, `writing-adrs` |
| Estimate     | 37 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-14.01 — PixiJS application lifecycle in `OfficeCanvas.vue` (3 pts)
- [ ] US-14.02 — Tilemap and sprite rendering with interpolation and y-sorting (5 pts)
- [ ] US-14.03 — Integer scaling, pixel snapping and object pools (3 pts)
- [ ] US-14.04 — Speech bubbles and emotes (3 pts)
- [ ] US-14.05 — Carried cards, stamp and confetti effects (3 pts)
- [ ] US-14.06 — Office View window and controls (5 pts)
- [ ] US-14.07 — Click-through to agents, desks and the Kanban wall (3 pts)
- [ ] US-14.08 — Office pause as a domain command (2 pts)
- [ ] US-14.09 — Accessible text mirror and agent table (2 pts)
- [ ] US-14.10 — Reduced motion mode (2 pts)
- [ ] US-14.11 — Performance budget test (3 pts)
- [ ] US-14.12 — Office E2E scenarios (3 pts)

## 1. Objective

Render the office engine with PixiJS as smooth, pixel-perfect Amiga-style animation inside an
Office View window: interpolated movement, y-sorting, bubbles, emotes, carried cards and
effects; controls to pause, change speed and follow agents; click-through to cards and agents;
an accessible text mirror; reduced motion; and a verified 60 fps budget — silently.

## 2. Scope

**In:** `office-renderer/` (only module importing PixiJS), `OfficeCanvas.vue`, Office View window,
controls, click-through, office pause command (backend + frontend), mirror, reduced motion,
performance and E2E tests.

**Out:** CRT overlay (WP23), sounds (forbidden), new choreographies (WP13 mapping is the source).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D14.1 | Renderer | Pixi app lifecycle, tilemap, sprites, interpolation, y-sort, integer scale, pixel snapping, pools | Visual baseline at fixed seed; zero per-frame allocations (heap test) | US-14.01 – US-14.03 |
| D14.2 | Effects | Bubbles, emotes, carried cards, stamp, confetti per DESIGN.md §7.3 | Visual baselines per effect | US-14.04, US-14.05 |
| D14.3 | Office View | Window with pause (domain), speed, follow; click-through | E2E interactions | US-14.06 – US-14.08 |
| D14.4 | Accessibility & performance | Text mirror, agent table, reduced motion, 60 fps budget, E2E scenarios | Perf test report; E20 green; E2E green | US-14.09 – US-14.12 |

## 4. User stories

### D14.1 — Renderer

#### US-14.01 — PixiJS application lifecycle in `OfficeCanvas.vue`

- [ ] **US-14.01 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a developer, I want one component that owns the Pixi application safely, so that
  opening and closing the Office never leaks GPU memory.
- **Acceptance criteria:**
  - [ ] AC1 — `OfficeCanvas.vue` creates the `Application` in `onMounted` (async init), attaches
    the canvas, starts the ticker driving `engine.advance(dt)` and `renderer.draw(snapshot,
    alpha)`.
  - [ ] AC2 — `onBeforeUnmount` destroys the application with textures and children; opening and
    closing 20 times keeps memory stable (test in Playwright with `performance.memory` where
    available or object counters).
  - [ ] AC3 — The ticker pauses when the window is minimized/hidden or the tab is hidden; the
    engine keeps receiving events.
  - [ ] AC4 — Pixi objects are never reactive (`markRaw`), never stored in Pinia.
- **Tasks:** component; renderer facade; visibility handling.
- **Tests:** component test with a fake renderer; E2E memory check.
- **Done when:** all AC green.

#### US-14.02 — Tilemap and sprite rendering with interpolation and y-sorting

- [ ] **US-14.02 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want characters to glide smoothly between tiles like in a 16-bit game.
- **Acceptance criteria:**
  - [ ] AC1 — Tile layers rendered with `@pixi/tilemap`; `furniture-above` drawn over actors.
  - [ ] AC2 — Sprites drawn at `lerp(prev, curr, alpha)` positions from the engine snapshot,
    rounded to logical pixels; animation frames from atlas names.
  - [ ] AC3 — Actors layer y-sorted by feet position (`zIndex`), `sortableChildren` enabled.
  - [ ] AC4 — Name tags (Topaz 1×) above agents optional (toggle).
- **Tasks:** layers, sprite manager, atlas loader with manifest.
- **Tests:** visual baseline at fixed seed and fixed alpha.
- **Done when:** all AC green.

#### US-14.03 — Integer scaling, pixel snapping and object pools

- [ ] **US-14.03 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want crisp pixels at any window size and no stutter.
- **Acceptance criteria:**
  - [ ] AC1 — Stage rendered at 320×256 logical and scaled by the largest integer fitting the
    window content area; letterboxed with the desktop color; `scaleMode: 'nearest'`,
    `roundPixels: true`, CSS `image-rendering: pixelated`.
  - [ ] AC2 — Pools for bubbles, emotes, carried cards, particles; a test counts allocations per
    frame in the render loop = 0 after warm-up.
  - [ ] AC3 — Resizing the window recomputes scale without reloading textures.
- **Tasks:** scale manager; pools.
- **Tests:** unit tests for scale; allocation counter test.
- **Done when:** all AC green.

### D14.2 — Effects

#### US-14.04 — Speech bubbles and emotes

- [ ] **US-14.04 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want agents to "talk" and react visually.
- **Acceptance criteria:**
  - [ ] AC1 — Bubbles: Topaz 1× text ≤ 40 chars, 1-px ink border, tail toward the speaker, never
    off-screen (clamped), auto-dismiss per DESIGN.md §7.3.
  - [ ] AC2 — Emotes: 8×8 icons above the head with 1-frame pop in/out.
  - [ ] AC3 — Overlapping bubbles stack vertically without covering each other's speaker.
- **Tasks:** bubble and emote renderers.
- **Tests:** visual baselines.
- **Done when:** all AC green.

#### US-14.05 — Carried cards, stamp and confetti effects

- [ ] **US-14.05 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to see cards travel and celebrate approvals.
- **Acceptance criteria:**
  - [ ] AC1 — Carried card sprite (8×6, tinted by type) in hands; drop animates into trays/desks.
  - [ ] AC2 — Approval stamp animation (3 frames) and 12-particle 4-color confetti at the archive.
  - [ ] AC3 — Effects respect reduced motion (static icon flash instead).
- **Tasks:** effect renderers.
- **Tests:** visual baselines.
- **Done when:** all AC green.

### D14.3 — Office View

#### US-14.06 — Office View window and controls

- [ ] **US-14.06 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want an Office window I can control.
- **Acceptance criteria:**
  - [ ] AC1 — "Office" desktop icon opens an `AmigaWindow` hosting `OfficeCanvas`; deep link
    `/office`.
  - [ ] AC2 — Controls: *Pause office* / *Resume* (domain command, US-14.08), speed Cycle
    ×1/×2/×4 (animation only), *Follow agent* Cycle (camera centers on an agent within map
    bounds), name tags toggle.
  - [ ] AC3 — When the office is paused, a `PAUSED` overlay (Topaz 2×) shows and the LED is off.
  - [ ] AC4 — Below 1024 px width, the "Please use a larger screen" requester is shown.
- **Tasks:** window, controls, camera.
- **Tests:** component tests; E2E.
- **Done when:** all AC green.

#### US-14.07 — Click-through to agents, desks and the Kanban wall

- [ ] **US-14.07 completed** · **Points:** 3 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want to click things in the office to learn more.
- **Acceptance criteria:**
  - [ ] AC1 — Clicking an agent opens its Agent Card (persona, role, status, current card, last
    10 events, "Ask the PM about <name>" placeholder until WP18).
  - [ ] AC2 — Clicking a desk shows the current card; clicking the Kanban wall opens the most
    active project's board.
  - [ ] AC3 — Hit testing works at any scale; keyboard alternative via the agent table (US-14.09).
- **Tasks:** hit-test map; Agent Card component.
- **Tests:** E2E clicks at ×2 and ×3.
- **Done when:** all AC green.

#### US-14.08 — Office pause as a domain command

- [ ] **US-14.08 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want "Pause office" to stop the agents for real, not just the
  animation (Constitution P4).
- **Acceptance criteria:**
  - [ ] AC1 — `PauseOffice` / `ResumeOffice` commands → `OfficePaused` / `OfficeResumed` events;
    the office state exposes `paused`.
  - [ ] AC2 — The Orchestrator (WP17) will respect it within one tick; in WP14 the flag is
    exposed and tested.
  - [ ] AC3 — The scene freezes on `OfficePaused` and resumes on `OfficeResumed` (Appendix C).
- **Tasks:** domain + handler + endpoint + UI wiring.
- **Tests:** GWT, API, E2E.
- **Done when:** all AC green.

### D14.4 — Accessibility & performance

#### US-14.09 — Accessible text mirror and agent table

- [ ] **US-14.09 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a screen-reader user, I want the office in text form.
- **Acceptance criteria:**
  - [ ] AC1 — A side panel (toggle) lists narration lines in an `aria-live="polite"` region.
  - [ ] AC2 — An agent table (name, role, status, current card, location) with keyboard
    navigation; Enter opens the Agent Card.
- **Tasks:** components bound to engine narration and staff store.
- **Tests:** component tests; axe.
- **Done when:** all AC green.

#### US-14.10 — Reduced motion mode

- [ ] **US-14.10 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a user sensitive to motion, I want the office to stay calm (E20).
- **Acceptance criteria:**
  - [ ] AC1 — With `prefers-reduced-motion` or the Preferences override, idle behaviors are off,
    choreographies resolve instantly with a 1-frame fade, nothing blinks.
  - [ ] AC2 — E20 test: no idle wandering over 2 minutes of simulated time; choreographies finish
    in one step.
- **Tasks:** wire `useReducedMotion` into engine and renderer.
- **Tests:** unit + E2E E20.
- **Done when:** all AC green.

#### US-14.11 — Performance budget test

- [ ] **US-14.11 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want proof the office runs at 60 fps with the full staff.
- **Acceptance criteria:**
  - [ ] AC1 — A scripted scenario with 7 agents walking continuously for 60 s at ×3 scale runs in
    Playwright (Chromium) on the CI runner; average fps ≥ 58 and p99 frame time ≤ 25 ms.
  - [ ] AC2 — The result is reported in the job summary; regressions > 10 % fail the job.
- **Tasks:** perf scenario page (dev only), measurement harness.
- **Tests:** itself.
- **Done when:** job part of nightly (PR job runs a short version).

#### US-14.12 — Office E2E scenarios

- [ ] **US-14.12 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want the visible behavior of the office protected by tests.
- **Acceptance criteria:**
  - [ ] AC1 — Manual pull by the user → PM walks to the wall, carries the card to the assignee
    (choreography steps observed via a test hook exposing the engine queue).
  - [ ] AC2 — Rejection (manual) → QA walks to the assignee's desk with `✗` (E9 visual part).
  - [ ] AC3 — Rename → sparkle and new name tag (E15); disable → walks to the door (E16).
  - [ ] AC4 — Reconnect after missed events → correct placement without replay.
- **Tasks:** test hooks (dev/test builds only), scenarios.
- **Tests:** itself.
- **Done when:** scenarios in the `e2e` job.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP14 closing: Office renderer & view`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; S4 + E20 green; perf budget met; no audio.
- [ ] M3 exit criteria demonstrated; `v0.4.0` tagged after WP12–WP14 are DONE.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| GPU differences on CI runners | Perf thresholds measured on the pinned runner; nightly authoritative |
| WebGL unavailable | PixiJS fallback to WebGPU/WebGL as supported; requester if neither |
| Memory leaks on window close | Explicit destroy + leak test |

## 7. Blockers

None.

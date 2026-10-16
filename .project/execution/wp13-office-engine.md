# WP13 — Office Engine

| Field        | Value |
| ------------ | ----- |
| Milestone    | M3 — Office |
| Status       | READY |
| Depends on   | WP06 (event and projection types), WP12 D12.3 (map; a placeholder map is allowed to start) |
| Enables      | WP14 |
| Constitution | Principle P5, Article XIII (§13.2–13.5), §14.9, Appendix C, success criterion S4 |
| Guides       | [FRONTEND.md](../../.docs/FRONTEND.md) §1.1, §8, §10 · [DESIGN.md](../../.docs/DESIGN.md) §7.3 · [STACK.md](../../.docs/STACK.md) §4 |
| Skills       | `building-office-scene`, `tracing-events`, `delivering-features`, `writing-adrs` |
| Estimate     | 40 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-13.01 — Scene model and fixed-step loop with deterministic randomness (5 pts)
- [ ] US-13.02 — Map loader: walkable grid and points of interest (3 pts)
- [ ] US-13.03 — A* pathfinding (3 pts)
- [ ] US-13.04 — Tile reservation, re-pathing and waiting (5 pts)
- [ ] US-13.05 — Choreography DSL and step executor (5 pts)
- [ ] US-13.06 — Per-agent queues, compression and batching (5 pts)
- [ ] US-13.07 — Event-to-choreography mapping for Appendix C (5 pts)
- [ ] US-13.08 — S4 completeness test (2 pts)
- [ ] US-13.09 — Placement from projections on load and reconnect (3 pts)
- [ ] US-13.10 — Idle behaviors with seeded randomness (2 pts)
- [ ] US-13.11 — Narration for the accessible text mirror (2 pts)

## 1. Objective

Write the pure TypeScript office engine (`frontend/src/office-engine/`): a deterministic 50 Hz
simulation of the office that turns domain events into choreographies — walking, carrying,
speaking, emoting — with pathfinding, collision-free movement, bounded lag and a narration
stream for accessibility. It imports neither Vue nor PixiJS and is fully unit-testable.

## 2. Scope

**In:** scene state, loop, RNG, clock injection, map loader, A*, reservations, DSL, executor,
queues, compression, batching, mapping table, completeness test, placement, idle behaviors,
narration.

**Out:** drawing (WP14), audio (forbidden), domain logic (never — the engine only reads events).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D13.1 | Simulation core | Scene model, fixed 50 Hz step with accumulator, seeded RNG, injectable time, map loader | Determinism test: same seed + inputs → identical snapshots | US-13.01, US-13.02 |
| D13.2 | Movement | A* (4-dir, Manhattan), reservation table, re-path after 1 s, wait bubble | Pathfinding unit + property tests; no overlap invariant | US-13.03, US-13.04 |
| D13.3 | Choreographies | DSL (`walkTo`, `face`, `say`, `emote`, `carry`, `drop`, `animate`, `wait`), executor, per-agent queues, compression (> 3), batching by correlation id | Executor tests; lag ≤ 5 s invariant | US-13.05, US-13.06 |
| D13.4 | Mapping | Pure `mapEventToChoreographies` for every Appendix C row; S4 completeness test | Mapping tests per row; completeness test in CI | US-13.07, US-13.08 |
| D13.5 | Placement, idle, narration | Placement from projections on load/reconnect; idle behaviors; narration sentences | Unit tests; reduced-motion flag honored | US-13.09 – US-13.11 |

## 4. User stories

### D13.1 — Simulation core

#### US-13.01 — Scene model and fixed-step loop with deterministic randomness

- [ ] **US-13.01 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As a developer, I want a deterministic simulation, so that the office behaves the same
  in tests and in the browser.
- **Acceptance criteria:**
  - [ ] AC1 — `createEngine({map, seed, now})` returns an engine with `step(dtFixedMs = 20)`,
    `advance(realDtMs)` (accumulator, max 5 steps per frame to avoid spiral of death),
    `snapshot()` (previous + current states for interpolation), `dispatch(event)`.
  - [ ] AC2 — The RNG is a seeded PRNG (e.g. xoshiro/mulberry) implemented in `shared`; no
    `Math.random` in the engine (lint rule).
  - [ ] AC3 — Same seed + same event sequence + same step count → deep-equal snapshots.
  - [ ] AC4 — Speed multiplier ×1/×2/×4 scales simulated time only.
  - [ ] AC5 — `pause()`/`resume()` freezes the simulation (used for office pause and hidden tab).
- **Tasks:** `office-engine/core/`; RNG; lint rule `no-restricted-properties` for `Math.random`.
- **Tests:** determinism test; accumulator tests.
- **Done when:** all AC green.

#### US-13.02 — Map loader: walkable grid and points of interest

- [ ] **US-13.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the engine, I want to read the Tiled map into a walkable grid and named POIs.
- **Acceptance criteria:**
  - [ ] AC1 — `loadMap(json)` validates the structure (layers, size 20×16, objects) and returns
    `{grid, pois, homeDesks}`; invalid maps throw a descriptive error.
  - [ ] AC2 — Every POI has `approach` and `facing`; all approach tiles reachable from `poi.door`
    (test).
  - [ ] AC3 — Row 0 is not walkable (status strip).
- **Tasks:** loader + types; placeholder map until WP12 delivers.
- **Tests:** unit tests with the real and a broken map.
- **Done when:** all AC green.

### D13.2 — Movement

#### US-13.03 — A* pathfinding

- [ ] **US-13.03 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As an agent sprite, I want the shortest path between tiles avoiding furniture.
- **Acceptance criteria:**
  - [ ] AC1 — `findPath(grid, from, to)` returns the shortest 4-direction path (Manhattan
    heuristic) or `null` if unreachable.
  - [ ] AC2 — Property tests: path is contiguous, never crosses non-walkable tiles, length equals
    BFS shortest length.
  - [ ] AC3 — Ties broken deterministically (prefer horizontal then vertical moves) for
    reproducible paths.
  - [ ] AC4 — 1 000 path queries on the office map < 20 ms.
- **Tasks:** binary-heap open set; pooled node arrays.
- **Tests:** unit + fast-check.
- **Done when:** all AC green.

#### US-13.04 — Tile reservation, re-pathing and waiting

- [ ] **US-13.04 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want agents never to walk through each other, so that the office looks
  real.
- **Acceptance criteria:**
  - [ ] AC1 — A reservation table allows one agent per tile per step; an agent whose next tile is
    reserved waits.
  - [ ] AC2 — After 1 s blocked, the agent re-paths treating occupied tiles as blocked; if still
    blocked, it waits with a `…` bubble and retries every 500 ms.
  - [ ] AC3 — Movement at 2 tiles/s (×1) with sub-pixel positions; direction changes only on
    tile centres; walk frame advances every 4 px.
  - [ ] AC4 — Invariant (property test): two agents never occupy the same tile in the same step;
    no deadlock persists longer than 5 s in random scenarios with 7 agents.
- **Tasks:** movement system, reservations, deadlock breaker (lower-priority agent steps aside).
- **Tests:** unit + fast-check scenario tests.
- **Done when:** all AC green.

### D13.3 — Choreographies

#### US-13.05 — Choreography DSL and step executor

- [ ] **US-13.05 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As a developer, I want to describe what agents do as data, so that choreographies are
  easy to write and test.
- **Acceptance criteria:**
  - [ ] AC1 — Steps: `walkTo(poi|agentDesk)`, `face(dir)`, `say(text, ms)` (≤ 40 chars,
    truncated with …), `emote(icon, ms)`, `carry(cardRef)`, `drop(target)`, `animate(name, ms)`,
    `wait(ms)`; typed discriminated union.
  - [ ] AC2 — The executor runs steps sequentially per agent, emits state changes (pose, bubble,
    carried item) into the scene, and completes steps deterministically.
  - [ ] AC3 — Each step has a `finalPose()` used by compression.
  - [ ] AC4 — Timings follow DESIGN.md §7.3.
- **Tasks:** `office-engine/choreography/{dsl,executor}.ts`.
- **Tests:** executor unit tests per step.
- **Done when:** all AC green.

#### US-13.06 — Per-agent queues, compression and batching

- [ ] **US-13.06 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want the office to keep up with reality even when many events arrive.
- **Acceptance criteria:**
  - [ ] AC1 — Each agent has a FIFO queue of choreographies; multi-agent choreographies are
    synchronized (e.g. handover waits for both).
  - [ ] AC2 — Queue length > 3 → the oldest pending choreographies jump to their final pose and
    position; the visible lag never exceeds ~5 s of animation (property test).
  - [ ] AC3 — N `CardCreated` events with the same `correlationId` within 2 s → one walk to the
    Kanban wall with N pin animations.
  - [ ] AC4 — Pausing the office freezes queues; resuming continues.
- **Tasks:** queue manager, sync barrier, batcher.
- **Tests:** unit + property tests.
- **Done when:** all AC green.

### D13.4 — Mapping

#### US-13.07 — Event-to-choreography mapping for Appendix C

- [ ] **US-13.07 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want every meaningful event to move people in the office, so that it
  feels like a game and tells the truth (Principle P5).
- **Acceptance criteria:**
  - [ ] AC1 — `mapEventToChoreographies(event, scene)` implements every row of Constitution
    Appendix C (note submitted, triage, card created, pulled, work started, consultation, blocked,
    submitted, review started, approved, rejected, escalated, agent enabled/disabled/renamed/face
    changed, chat, office paused, job failed).
  - [ ] AC2 — The function is pure; actors are resolved from event payload and scene state;
    missing agents (disabled) are skipped with narration.
  - [ ] AC3 — Each row has a unit test asserting the exact step list.
- **Tasks:** `office-engine/choreography/map.ts`.
- **Tests:** unit tests per row.
- **Done when:** all AC green.

#### US-13.08 — S4 completeness test

- [ ] **US-13.08 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want a guarantee that no office-relevant event is forgotten
  (success criterion S4).
- **Acceptance criteria:**
  - [ ] AC1 — The generated OpenAPI event schemas carry an `affectsOffice` marker (set in the
    backend registry); the test lists them and fails if any lacks a mapping.
  - [ ] AC2 — The test also fails if Appendix C lists an event the mapping ignores (parsed from a
    machine-readable copy `office-engine/choreography/appendix-c.json` checked against the
    Constitution in review).
- **Tasks:** marker in backend event registry; test.
- **Tests:** itself.
- **Done when:** test required in CI.

### D13.5 — Placement, idle, narration

#### US-13.09 — Placement from projections on load and reconnect

- [ ] **US-13.09 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want the office to look right immediately when I open it, without
  replaying history.
- **Acceptance criteria:**
  - [ ] AC1 — `placeFromProjections(agents, board)` positions each agent: `working` → home desk
    working pose; `reviewing` → QA bench; `idle`/`blocked`/`paused` → home desk; `offline` → not
    rendered.
  - [ ] AC2 — On WebSocket `resync`, queues are cleared and placement re-run.
- **Tasks:** placement function.
- **Tests:** unit tests per status.
- **Done when:** all AC green.

#### US-13.10 — Idle behaviors with seeded randomness

- [ ] **US-13.10 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want idle agents to look alive (coffee, stretch, look at the board).
- **Acceptance criteria:**
  - [ ] AC1 — Every 20–60 s (seeded), an idle agent with an empty queue performs one idle
    choreography; never when reduced motion or idle behaviors are off.
  - [ ] AC2 — Idle choreographies are cancelled immediately when a real choreography arrives.
- **Tasks:** idle scheduler.
- **Tests:** unit tests with fixed seed.
- **Done when:** all AC green.

#### US-13.11 — Narration for the accessible text mirror

- [ ] **US-13.11 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a screen-reader user, I want to know what happens in the office in words.
- **Acceptance criteria:**
  - [ ] AC1 — Every choreography start emits a narration sentence (e.g. "Copper walks SHOP-12 to
    the QA bench").
  - [ ] AC2 — Idle choreographies are not narrated.
  - [ ] AC3 — Narration is available even when rendering is paused.
- **Tasks:** narration emitter.
- **Tests:** unit tests.
- **Done when:** consumed by WP14.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP13 closing: Office engine`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; `office-engine` coverage ≥ 90 %; boundaries rule (no Vue/Pixi) green.
- [ ] S4 completeness test required; Appendix C and mapping in sync.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Deadlocks in narrow corridors | Reservation + re-path + step-aside rule; property tests |
| Lag under event bursts | Compression and batching; lag invariant test |
| Appendix C drift | Machine-readable copy + completeness test |

## 7. Blockers

None.

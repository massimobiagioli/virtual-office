---
name: building-office-scene
description: Implementation guide for the Virtual Office top-down Amiga-style office scene - 320x256 canvas with integer scaling, 16x16 tile map, sprites and animation frames, A* pathfinding, choreographies mapped from domain events, queue compression, reconnect placement, accessible text mirror and reduced motion. Use when working in frontend/src/office-engine, frontend/src/office-renderer, sprite assets, the tile map, or the Office View window.
---

# Building the office scene

Authoritative source: Constitution Article XIII, §14.9, Appendix C.

## Non-negotiable principle

The scene is a **projection** (Principle P5). It consumes events and projections typed by the
generated OpenAPI types; it never sends domain commands except through explicit user clicks
handled by the app. Animations never delay the domain.

## Module split (decided in STACK.md §4)

- `frontend/src/office-engine/` — plain TypeScript: fixed-step simulation, map, A*,
  choreographies, queues. Imports **neither Vue nor PixiJS**. Fully unit-testable.
- `frontend/src/office-renderer/` — the only module importing **PixiJS 8** and
  `@pixi/tilemap`; draws engine state with interpolation.
- `OfficeCanvas.vue` — mounts/destroys the Pixi `Application`, wires Pinia stores to the
  engine. No game logic in Vue.

## Rendering setup

- Logical 320×256, tile 16×16, map 20×16 (row 0 is the status strip).
- Scale = largest integer that fits the window; nearest-neighbour; CSS
  `image-rendering: pixelated`; PixiJS `roundPixels: true`, textures `scaleMode: 'nearest'`.
- Logic at fixed 50 Hz (accumulator loop on the Pixi `Ticker`), render at display rate.
- **Smoothness:** draw at `lerp(prev, curr, alpha)` (render interpolation), simulate in
  sub-pixels, snap output to the logical pixel grid, integer stage scale. Walk-cycle frames
  advance by distance travelled (every 4 px) so feet never slide at ×2/×4.
- No per-frame allocations in the hot path (object pools for bubbles, emotes, paths).
- Pause rendering when the window is hidden.

## Map

- Tiled-compatible JSON in `assets/maps/office.json`. Named objects:
  `desk.pm`, `desk.dev.1`, `desk.dev.2`, `desk.arch`, `desk.design`, `desk.support`,
  `bench.qa`, `wall.kanban`, `table.meeting`, `poi.coffee`, `poi.archive`, `poi.door`.
- Each object has an `approach` tile (where the agent stands) and a `facing` direction.

## Sprites

- 16×24 px characters, 4 directions × 4 walk frames, 2 idle, 2 working frames; y-sorted.
- Carried card: 8×6 paper sprite tinted by card type.
- Atlas JSON + indexed PNG; colors OCS 12-bit compliant (see `designing-amiga-ui`).

## Movement

- A* on a 4-neighbour grid, Manhattan heuristic, pure function `findPath(map, from, to)`.
- Speed 2 tiles/s at ×1, sub-pixel accumulation, draw at integer pixels.
- Reservation table: one agent per tile per step; blocked > 1 s → re-path; still blocked →
  wait with "…" bubble.

## Choreographies

- Step DSL: `walkTo(poi)`, `face(dir)`, `say(text, ms)`, `emote(icon)`, `carry(card)`,
  `drop()`, `animate(name, ms)`, `wait(ms)`.
- `mapEventToChoreographies(event, sceneState) → Choreography[]` is pure and lives in
  `frontend/src/office-engine/choreography/map.ts`. Keep it in sync with Constitution Appendix C.
- Per-agent queue. Queue length > 3 → compress: jump older choreographies to their final pose
  and position. The scene must never lag reality by more than ~5 s.
- Batch: N `CardCreated` events with the same `correlationId` → one walk to the wall.
- Speed ×1/×2/×4 affects animation only.

## Reconnect / load

Do not replay history. Place each agent from projections: `working` → at home desk working
pose; `reviewing` → `bench.qa`; `idle` → home desk; `offline` → not rendered.

## Accessibility

- Live region text mirror: one sentence per choreography start ("Copper walks SHOP-12 to QA").
- Reduced motion: no idle wandering; choreographies resolve instantly with a 1-frame fade; no
  blinking.

## Tests

- `findPath` correctness and no path through walls (Vitest + fast-check properties).
- **Completeness test (S4):** every event type in Appendix B flagged `affectsOffice` has a
  mapping; fails CI otherwise.
- Deterministic scene snapshot at fixed seed after a scripted event sequence.
- Playwright visual regression of the Office View at fixed seed and scale ×2.

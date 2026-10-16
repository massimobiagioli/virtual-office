# WP12 — Pixel Art & Assets

| Field        | Value |
| ------------ | ----- |
| Milestone    | M3 — Office |
| Status       | READY |
| Depends on   | WP07 (tokens, palette check), WP09 (face ids) |
| Enables      | WP13 (map), WP14 (rendering), WP09/WP23 (final portraits and icons in UI) |
| Constitution | §13.1–13.3, §14.2, §14.6, §14.8, §14.10, Appendix D |
| Guides       | [DESIGN.md](../../.docs/DESIGN.md) §3.4, §6–8 · [FRONTEND.md](../../.docs/FRONTEND.md) §8 |
| Skills       | `designing-amiga-ui`, `building-office-scene`, `delivering-features`, `writing-adrs` |
| Estimate     | 45 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-12.01 — Office palette file and mapping to tokens (2 pts)
- [ ] US-12.02 — Asset validation checks in CI (3 pts)
- [ ] US-12.03 — Character sprite template and animation specification (3 pts)
- [ ] US-12.04 — Characters face-01 to face-04 (5 pts)
- [ ] US-12.05 — Characters face-05 to face-08 (5 pts)
- [ ] US-12.06 — Characters face-09 to face-12 (5 pts)
- [ ] US-12.07 — Characters face-13 to face-16 (5 pts)
- [ ] US-12.08 — Representation and quality review of the cast (1 pt)
- [ ] US-12.09 — Office tileset (5 pts)
- [ ] US-12.10 — Tiled office map with named objects (3 pts)
- [ ] US-12.11 — Desktop icons (3 pts)
- [ ] US-12.12 — UI icons, card-type icons, emotes and cursors (3 pts)
- [ ] US-12.13 — Asset licenses and export pipeline documentation (2 pts)

## 1. Objective

Produce every original pixel-art asset Virtual Office needs — 16 characters (portrait, mini
portrait, sprite sheet), the office tileset and map, desktop/UI/card icons, emotes and cursors —
in the exact formats of DESIGN.md, OCS-palette compliant, validated by CI and fully licensed. No
audio assets exist (Constitution §14.10).

## 2. Scope

**In:** palette `.gpl`; Aseprite sources and exports; atlases; tileset; Tiled map; icons;
emotes; cursors; CI checks; `assets/LICENSES.md`; export documentation.

**Out:** rendering code (WP14), engine logic (WP13), any sound (forbidden).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D12.1 | Palette & checks | One office palette ≤ 32 colors (OCS 12-bit), aligned with chrome tokens; CI validates every PNG and atlas | Palette check + asset check green; negative fixtures fail | US-12.01, US-12.02 |
| D12.2 | Characters | 16 original characters with 32×32 portrait (+ blink), 16×16 mini, 16×24 sprite sheet (4 dirs × walk 4, idle 2, work 2, carry walk 4) | Atlas frame names complete; visual review sign-off | US-12.03 – US-12.08 |
| D12.3 | Tileset & map | 16×16 tileset and Tiled map 20×16 with layers and named objects of Constitution §13.2 | Map loads in Tiled and in engine tests; objects present | US-12.09, US-12.10 |
| D12.4 | Icons & licenses | Desktop icons (9), UI icons, card-type icons (7), emotes, cursors; LICENSES.md complete | Asset check; LICENSES.md row per asset | US-12.11 – US-12.13 |

## 4. User stories

### D12.1 — Palette & checks

#### US-12.01 — Office palette file and mapping to tokens

- [ ] **US-12.01 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As an artist, I want one authoritative office palette, so that every sprite and tile
  shares the same 32 colors.
- **Acceptance criteria:**
  - [ ] AC1 — `assets/src/palette/office.gpl` contains ≤ 32 entries; index 0 transparent;
    indices 1–4 equal the wb13 chrome tokens; all entries OCS 12-bit.
  - [ ] AC2 — Floor, wall, desk, plant and the four skin tones of DESIGN.md §3 are present with
    names.
  - [ ] AC3 — A script verifies that `tokens.css` semantic colors used in the scene exist in the
    palette.
- **Tasks:** palette file; mapping script.
- **Tests:** palette check run.
- **Done when:** palette merged and referenced by DESIGN.md.

#### US-12.02 — Asset validation checks in CI

- [ ] **US-12.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a reviewer, I want broken assets rejected automatically.
- **Acceptance criteria:**
  - [ ] AC1 — Every PNG under `frontend/src/assets/` is indexed, its palette ⊂ office palette (or
    chrome palette for UI icons).
  - [ ] AC2 — Dimensions are multiples of the cell size declared in the atlas.
  - [ ] AC3 — Every frame name referenced in code (registry of animations) exists in an atlas.
  - [ ] AC4 — No audio file types (`.wav`, `.ogg`, `.mp3`, `.flac`, …) exist anywhere in the repo.
- **Tasks:** extend `scripts/check_palette.py`; `scripts/check_assets.py` (stdlib PNG parsing).
- **Tests:** good/bad fixtures.
- **Done when:** checks required in CI.

### D12.2 — Characters

#### US-12.03 — Character sprite template and animation specification

- [ ] **US-12.03 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As an artist and a developer, I want one template that fixes sizes, frames and tags,
  so that all 16 characters are interchangeable in code.
- **Acceptance criteria:**
  - [ ] AC1 — `assets/src/characters/_template.aseprite` with layers (outline, body, clothes,
    hair, accessories), tags `walk-{up,down,left,right}`, `idle-*`, `work-*`, `carry-*`.
  - [ ] AC2 — Export settings produce `face-NN.png` + JSON atlas with frame names
    `face-NN/<animation>/<direction>/<index>` (DESIGN.md §8).
  - [ ] AC3 — A portrait template (32×32 + blink frame) and mini (16×16).
  - [ ] AC4 — A sample character exported and loaded by an engine test.
- **Tasks:** template files; export script/notes.
- **Tests:** atlas validation via US-12.02.
- **Done when:** template approved in review.

#### US-12.04 — Characters face-01 to face-04

- [ ] **US-12.04 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want the Organizer, the Hacker, the Demo Coder and the Pixel Artist
  drawn in Amiga style, so that the default PM, developers and designer have faces.
- **Acceptance criteria:**
  - [ ] AC1 — For each of face-01…04: sprite sheet with all tags, portrait (+ blink), mini,
    matching Appendix D visual notes.
  - [ ] AC2 — ≤ 3 own colors + outline + shared skin tone per character; palette check green.
  - [ ] AC3 — Walk cycles read clearly at ×2 in the four directions (review GIF attached to the PR,
    generated from frames).
- **Tasks:** draw, export, commit sources and exports.
- **Tests:** asset checks.
- **Done when:** review approved.

#### US-12.05 — Characters face-05 to face-08

- [ ] **US-12.05 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want the Architect, the Tracker Musician, the Support Hero and the
  Inspector drawn, so that the default architect, support and QA have faces.
- **Acceptance criteria:** same as US-12.04 for face-05…08 (Appendix D notes).
  - [ ] AC1 — Sheets, portraits, minis complete.
  - [ ] AC2 — Palette constraints respected.
  - [ ] AC3 — Review GIF attached.
- **Tasks:** draw, export.
- **Tests:** asset checks.
- **Done when:** review approved.

#### US-12.06 — Characters face-09 to face-12

- [ ] **US-12.06 completed** · **Points:** 5 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want the Veteran, the Intern, the Strategist and the Night Owl
  available for customization.
- **Acceptance criteria:**
  - [ ] AC1 — Sheets, portraits, minis complete for face-09…12.
  - [ ] AC2 — Palette constraints respected.
  - [ ] AC3 — Review GIF attached.
- **Tasks:** draw, export.
- **Tests:** asset checks.
- **Done when:** review approved.

#### US-12.07 — Characters face-13 to face-16

- [ ] **US-12.07 completed** · **Points:** 5 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want the Gamer, the Minimalist, the Robot and the Cat Person available.
- **Acceptance criteria:**
  - [ ] AC1 — Sheets, portraits, minis complete for face-13…16 (the cat appears in idle frames of
    face-16).
  - [ ] AC2 — Palette constraints respected.
  - [ ] AC3 — Review GIF attached.
- **Tasks:** draw, export.
- **Tests:** asset checks.
- **Done when:** review approved.

#### US-12.08 — Representation and quality review of the cast

- [ ] **US-12.08 completed** · **Points:** 1 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want the 16 characters reviewed together, so that the cast is
  diverse, respectful and coherent (Constitution Appendix D).
- **Acceptance criteria:**
  - [ ] AC1 — A contact sheet of all portraits and sprites at ×2 and ×4 is reviewed by the owner.
  - [ ] AC2 — Varied skin tones, genders, ages and styles; no stereotypes; feedback items fixed.
- **Tasks:** generate contact sheet; review session; fixes.
- **Tests:** none (review).
- **Done when:** owner sign-off recorded in the WP closing ADR.

### D12.3 — Tileset & map

#### US-12.09 — Office tileset

- [ ] **US-12.09 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want a charming top-down office in Amiga style.
- **Acceptance criteria:**
  - [ ] AC1 — `tiles-office.png` (16×16 tiles, indexed) with floor variants, walls and corners,
    glass wall (PM office), door, desks (single, twin monitor), PM desk with in-tray, architect
    whiteboard, designer tablet, support headset desk, QA bench with review tray and magnifier,
    Kanban wall, meeting table, coffee machine, plant, archive cabinet.
  - [ ] AC2 — Light from top-left (DESIGN.md §7.2); dithering allowed; palette check green.
  - [ ] AC3 — Animated tiles (monitor flicker, coffee steam) as 2-frame tiles.
- **Tasks:** draw, export, Tiled tileset `.tsx`/JSON.
- **Tests:** asset checks.
- **Done when:** review approved.

#### US-12.10 — Tiled office map with named objects

- [ ] **US-12.10 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the office engine, I want a data map with walkable tiles and named points, so that
  layout changes never require code changes.
- **Acceptance criteria:**
  - [ ] AC1 — `assets/maps/office.json` 20×16 tiles, layers `floor`, `walls`, `furniture-below`,
    `furniture-above`, `objects`; row 0 reserved for the status strip.
  - [ ] AC2 — Objects: `desk.pm`, `desk.dev.1`, `desk.dev.2`, `desk.arch`, `desk.design`,
    `desk.support`, `bench.qa`, `wall.kanban`, `table.meeting`, `poi.coffee`, `poi.archive`,
    `poi.door`, each with `approach` tile and `facing` properties.
  - [ ] AC3 — A walkability property per tile (or a collision layer); every POI approach tile is
    reachable from the door (verified by an engine test in WP13).
- **Tasks:** build map in Tiled; export JSON.
- **Tests:** schema validation script; reachability test (WP13).
- **Done when:** map loads in WP13 tests.

### D12.4 — Icons & licenses

#### US-12.11 — Desktop icons

- [ ] **US-12.11 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want real Workbench-style desktop icons.
- **Acceptance criteria:**
  - [ ] AC1 — 32×32, 4 chrome colors, for Projects, Office, Inbox, Talk to PM, Staff, Logbook,
    Decisions, Prefs, Trashcan; normal and selected states.
  - [ ] AC2 — Replace placeholders in WP08 desktop; visual baselines updated.
- **Tasks:** draw, export, swap in UI.
- **Tests:** asset checks; visual tests.
- **Done when:** merged.

#### US-12.12 — UI icons, card-type icons, emotes and cursors

- [ ] **US-12.12 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want consistent small icons everywhere.
- **Acceptance criteria:**
  - [ ] AC1 — 8×8 card-type icons (book, check, bug, lightning, brush, compass, wrench).
  - [ ] AC2 — 8×8 emotes: `!`, `!!`, `?!`, `✗`, `sweat`, `sparkle`, `…`, `disk-error`, `zz`.
  - [ ] AC3 — Cursor PNGs: default pointer, busy "zZ".
  - [ ] AC4 — 8×6 carried-card sprite tinted per card type.
- **Tasks:** draw, export, swap placeholders.
- **Tests:** asset checks; visual tests.
- **Done when:** merged.

#### US-12.13 — Asset licenses and export pipeline documentation

- [ ] **US-12.13 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want every asset's origin and license recorded, so that we
  ship nothing we are not allowed to ship (Constitution §14.8).
- **Acceptance criteria:**
  - [ ] AC1 — `assets/LICENSES.md` has one row per asset file: path, author, source, license.
  - [ ] AC2 — A CI check fails if an exported asset has no row.
  - [ ] AC3 — DESIGN.md §8 documents the export steps from Aseprite and Tiled.
- **Tasks:** LICENSES.md; check script; docs.
- **Tests:** check script fixtures.
- **Done when:** check required.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP12 closing: Pixel art & assets`), including the owner's cast sign-off; story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; asset, palette, license and no-audio checks required in CI.
- [ ] Placeholders removed from UI; visual baselines updated.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Art takes longer than planned | Faces 01–08 (defaults) first; 09–16 can follow in M3 tail |
| Inconsistent style across characters | Single template, shared palette, contact-sheet review |
| Licensing doubts | Original work only; LICENSES.md check |

## 7. Blockers

None.

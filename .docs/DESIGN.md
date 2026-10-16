# Virtual Office — Design Guide (Amiga 500 Workbench)

| Field   | Value                                                                                   |
| ------- | --------------------------------------------------------------------------------------- |
| Scope   | Every pixel of My Workbench: UI chrome, board, windows, icons, office scene, sprites, tiles, fonts, copy |
| Related | [CONSTITUTION.md](CONSTITUTION.md) Articles IV, XIII, XIV, Appendix D · [FRONTEND.md](FRONTEND.md) · skill `designing-amiga-ui` |

The Constitution sets the design **principles** (Article XIV). This guide is the **design
specification**: exact tokens, measures, component anatomy, asset formats and naming. If two
screens look different for no reason, one of them is breaking this guide.

---

## 1. Design principles

1. **Workbench 1.3 first.** When in doubt, ask: "How would this look on a 1987 Amiga 500 with
   Workbench 1.3 in PAL?"
2. **Pixels are sacred.** Integer scaling, hard edges, no anti-aliasing on chrome and sprites.
3. **Few colors, used consistently.** Four chrome colors; semantic colors only for meaning.
4. **Modern ergonomics, invisible.** Accessibility, keyboard, responsiveness and performance
   are non-negotiable but must not break the look.
5. **Truthful motion.** Everything that moves in the office means something happened
   (Constitution P1/P5).

### 1.1 Forbidden in UI chrome

`border-radius`, blurred `box-shadow`, gradients, translucency/opacity effects, `filter: blur`,
easing curves, smooth scrolling animations, emoji, vector icons, system fonts, colors outside
the token list. Dithering patterns are allowed.

---

## 2. Grid, scale and geometry

| Concept            | Value |
| ------------------ | ----- |
| Logical pixel      | `--px` = current integer scale (2 by default on ≥ 1280 px wide screens, 3 on ≥ 1920, 4 on ≥ 2560) |
| Base unit          | 1 logical px; spacing scale is multiples of **2** logical px |
| Spacing tokens     | `--sp-1: 2`, `--sp-2: 4`, `--sp-3: 6`, `--sp-4: 8`, `--sp-6: 12`, `--sp-8: 16` (× `--px`) |
| Screen title bar   | 10 logical px high |
| Window border      | 2 logical px (left/right), title bar 10, bottom 2 (9 with size gadget row) |
| Gadget size        | 10 × 10 logical px (close, depth, zoom); size gadget 16 × 9 |
| Text line height   | 9 logical px (8 px glyph + 1 px leading) at 1× |
| Minimum hit target | 10 × 10 logical px (≥ 20 CSS px at ×2, ≥ 24 CSS px recommended → gadgets render at ×3 on touch-capable devices) |
| Office canvas      | 320 × 256 logical px, tiles 16 × 16 |

All CSS sizes are written as `calc(var(--px) * N)`; never raw CSS pixels.

---

## 3. Color tokens

All values are **OCS 12-bit** (each channel a doubled hex nibble). Defined only in
`frontend/src/ui-amiga/tokens.css`; referenced everywhere else by name.

### 3.1 Chrome — Workbench 1.3 (default theme `wb13`)

| Token          | Hex       | Role                                                      |
| -------------- | --------- | --------------------------------------------------------- |
| `--wb-bg`      | `#0055AA` | Desktop, window interiors                                 |
| `--wb-fg`      | `#FFFFFF` | Text on `--wb-bg`, bevel light                            |
| `--wb-ink`     | `#000022` | Text on light surfaces, borders, bevel dark               |
| `--wb-accent`  | `#FF8800` | Active title bar fill, selection, focus ring, text cursor |

### 3.2 Chrome — Workbench 2.0 (theme `wb20`)

| Token          | Hex       |
| -------------- | --------- |
| `--wb-bg`      | `#AAAAAA` |
| `--wb-fg`      | `#FFFFFF` |
| `--wb-ink`     | `#000000` |
| `--wb-accent`  | `#6688BB` |

Themes swap **only** these four tokens (`[data-wb-theme="wb20"]` on `:root`). Semantic tokens
are shared.

### 3.3 Semantic tokens (shared)

| Token              | Hex       | Use |
| ------------------ | --------- | --- |
| `--c-backlog`      | `#778899` | BACKLOG column stripe |
| `--c-todo`         | `#FFCC00` | TODO stripe |
| `--c-doing`        | `#33AAFF` | DOING stripe |
| `--c-review`       | `#CC66FF` | REVIEW stripe |
| `--c-done`         | `#33CC33` | DONE stripe |
| `--c-danger`       | `#EE2222` | Blocked, errors, Guru frame |
| `--c-warning`      | `#FF8800` | WIP overflow, budget warning |
| `--c-p0` … `--c-p3`| `#EE2222`, `#FF8800`, `#FFCC00`, `#778899` | Priority badges |

Color is **never the only signal**: every stripe/badge also carries text or an icon.

### 3.4 Office palette (32 colors max on screen)

Index 0 transparent; indices 1–4 mirror the chrome tokens; the remaining indices are allocated
in `assets/src/palette/office.gpl` (GIMP palette, the single source for Aseprite and the CI
palette check). Includes floor, wall, desk, plant and the four skin tones of Constitution §14.2.

### 3.5 Contrast pairs (verified AA)

| Foreground  | Background | Allowed for |
| ----------- | ---------- | ----------- |
| `--wb-fg`   | `--wb-bg` (wb13) | All text |
| `--wb-ink`  | `--wb-fg`  | All text |
| `--wb-ink`  | `--wb-accent` | Title bar text, selection |
| `--wb-ink`  | `--c-todo`, `--c-done`, `--c-doing` | Badge text |
| `--wb-fg`   | `--c-danger` | Badge text ≥ 2× size only |

Any new pair is checked with the contrast script before use.

---

## 4. Typography

| Token           | Value |
| --------------- | ----- |
| `--font-ui`     | Topaz-style bitmap font (8 × 8 glyphs), licensed per ADR; fallback `"Courier New", monospace` |
| `--font-read`   | A second, more readable bitmap font for long text (card descriptions, ADRs, chat) — licensed per ADR |
| Sizes           | 1× (8 logical px) for chrome; 2× (16 logical px) for window headings and the PAUSED/Guru texts. No other sizes. |
| Weight          | Regular only. Emphasis = inverse video (ink on accent) or underline; never bold synthesis |
| Case            | Sentence case in UI copy; UPPERCASE only for column names (`BACKLOG`, `TODO`, …) and IDs |
| Rendering       | `-webkit-font-smoothing: none; font-smooth: never;` text rendered at integer multiples only |

---

## 5. Components

Each component lives in `frontend/src/ui-amiga/` as `Amiga<Name>.vue` and supports these
states where applicable: **default, hover, focus, pressed, selected, disabled, loading, error,
empty**. Every state has a visual-regression screenshot.

### 5.1 Screen (`AmigaScreen`)

- Title bar: `--wb-fg` background, `--wb-ink` text, left: `My Workbench`, then status text
  (`3 agents busy · 2 cards in review`), right: drive LED (on while any LLM job runs, red
  when the WebSocket is disconnected) and depth gadget.
- Desktop: `--wb-bg`, icons in a free grid (positions persisted).

### 5.2 Window (`AmigaWindow`)

```
┌[■]─ Title ───────────────────────────[◫][▣]┐   ■ close (left)  ◫ zoom  ▣ depth (right)
│                                            ▲│
│  content                                   ║│   proportional scroller (right)
│                                            ▼│
└────────────────────────────────────────[⋰]┘   ⋰ size gadget
```

- Active: title bar filled `--wb-accent` with horizontal 1-px ink "drag lines"; inactive:
  `--wb-fg` with no lines.
- Drag by title bar; resize by size gadget; depth gadget toggles front/back; zoom toggles
  between user size and maximum.
- Minimum size 120 × 60 logical px. Windows never go fully off-screen (title bar stays
  reachable).
- Open animation: optional 4-step zoom-box outline (≤ 120 ms), disabled under reduced motion.

### 5.3 Requester (`AmigaRequester`)

- Modal, centered on the active window, `--wb-fg` body, `--wb-ink` text.
- 1–3 buttons; **affirmative left, cancel right**; `Enter` = affirmative, `Esc` = cancel.
- Copy: one-sentence title + optional detail; no question marks in button labels
  (`Retry`, `Cancel`, `OK`).

### 5.4 Gadgets

| Component        | Anatomy / behavior |
| ---------------- | ------------------ |
| `AmigaButton`    | Raised bevel (1 px `--wb-fg` top/left, 1 px `--wb-ink` bottom/right); pressed inverts bevel; focus = 1 px dotted `--wb-accent` outline inset 1 px |
| `AmigaTextField` | Recessed bevel; block cursor `--wb-accent`; selection inverse video |
| `AmigaCheckbox`  | 14 × 9 recessed box with checkmark glyph |
| `AmigaRadio`     | Workbench 2.0 style, used only in Preferences |
| `AmigaCycle`     | Button with cycle glyph; click cycles; `Alt+↓` opens a list |
| `AmigaSlider`    | Proportional knob in recessed track |
| `AmigaScroller`  | Proportional knob + arrow buttons; replaces native scrollbars in windows |
| `AmigaIcon`      | 32 × 32 icon + label below; selected = inverse colors on icon and label |
| `AmigaMenu`      | Right-mouse menu bar over the screen title; items show `Right-Amiga+<key>` (mapped to Ctrl/⌘) |
| `AmigaShell`     | CLI window: `--wb-bg` background, prompt `1.SYS:> `, block cursor |
| `AmigaPointer`   | Custom CSS cursors (PNG, 2 colors + outline); busy pointer = "zZ" clock |
| `AmigaGuru`      | Fatal error screen (Constitution §4.4); red 2-px frame blinking 1 Hz (static under reduced motion) |

### 5.5 Kanban board

- Column = recessed panel with stripe (semantic color) 4 logical px on top, header
  `TODO 2/3` (count in `--c-warning` inverse when over limit).
- Card tile (`CardTile`) 1 raised bevel, width = column width − 8 px; content rows:
  1. type icon (8 × 8) · ID · priority badge;
  2. title (max 2 lines, ellipsis);
  3. assignee mini-portrait (16 × 16) · estimate · rework counter `↺2` · `BLOCKED` stripe.
- Dragging shows the card outline only (XOR-style dotted rectangle), like Workbench icon drags.
- Forbidden drop: screen border flashes `--c-danger` for 2 frames (the "DisplayBeep"), then a
  requester explains the rule.

---

## 6. Icons

| Set              | Size    | Colors | Location |
| ---------------- | ------- | ------ | -------- |
| Desktop icons    | 32 × 32 | 4 chrome colors | `assets/icons/desktop/` |
| Small UI icons   | 16 × 16 | 4 chrome colors | `assets/icons/ui/` |
| Card type icons  | 8 × 8   | 4 chrome colors | `assets/icons/card/` |
| Emotes (office)  | 8 × 8   | office palette  | `assets/sprites/emotes/` |

Card type glyphs: story = book, task = check, bug = bug, spike = lightning, design = brush,
architecture = compass, chore = wrench. Desktop icons are drawers and disks, as in
Constitution §4.2.

---

## 7. Office scene art

### 7.1 Characters

| Asset           | Size     | Frames |
| --------------- | -------- | ------ |
| Portrait        | 32 × 32  | 1 (+ 1 blink frame) |
| Mini portrait   | 16 × 16  | 1 |
| Sprite          | 16 × 24  | 4 directions × (4 walk + 2 idle + 2 work) + carry variants of walk |

- Each character uses at most **3 colors + transparent + 1 outline** of its own plus the
  shared skin tone (hardware-sprite homage).
- 1-px dark outline on sprites for readability on the floor.
- Characters are **original** (Constitution §14.8); the 16 archetypes are listed in
  Constitution Appendix D.

### 7.2 Tiles and map

- 16 × 16 tiles, one tileset `office.png` (indexed), map `assets/maps/office.json` (Tiled).
- Layers: `floor`, `walls`, `furniture-below`, `actors` (runtime), `furniture-above`,
  `objects` (named points: desks, POIs — Constitution §13.2).
- Light comes from the top-left: highlights on top/left edges, shadows bottom/right (same as
  bevels).

### 7.3 Animation timing (at speed ×1)

| Animation         | Timing |
| ----------------- | ------ |
| Walk              | 2 tiles/s; frame advance every 4 px travelled |
| Idle breathe      | 2 frames, 600 ms each |
| Working (typing)  | 2 frames, 150 ms each |
| Emote pop         | appears 1 frame, holds 1200 ms, disappears 1 frame |
| Speech bubble     | 40 chars max, 2500 ms, Topaz 1× text, 1-px ink border, tail toward speaker |
| Stamp (approve)   | 3 frames, 80 ms each |
| Confetti          | 12 particles, 4 colors, 700 ms |

---

## 8. Asset pipeline and naming

| Topic        | Standard |
| ------------ | -------- |
| Sources      | `assets/src/**/*.aseprite`, `assets/src/maps/*.tmx` (Tiled), palette `.gpl` files |
| Exports      | Indexed PNG + JSON atlas (`array` format, frame tags = animation names) into `frontend/src/assets/` |
| File names   | `kebab-case`: `face-07.png`, `sprites-characters.png`, `tiles-office.png` |
| Atlas frames | `<asset>/<animation>/<direction>/<index>` e.g. `face-07/walk/left/2`, `face-07/work/down/0` |
| Directions   | `up`, `down`, `left`, `right` |
| Checks (CI)  | Palette ⊂ allowed palette; PNG is indexed; dimensions are multiples of the cell size; every frame referenced by code exists |
| Licensing    | Every asset has a row in `assets/LICENSES.md` (source, author, license) |

Generated exports are committed so the build does not need Aseprite.

---

## 9. No audio

Virtual Office has **no sound at all** (Constitution §14.10): no audio assets, no audio code,
no sound preferences. Feedback that the original Amiga gave with sound is always visual:
DisplayBeep = screen border flash in `--c-danger` for 2 frames; drive activity = the LED in the
screen title bar; "Guru" = the red blinking frame. A design proposal containing sound is
rejected in review.

## 10. Copy and tone

- English, short, friendly-retro, never mocking the user.
- Patterns: `Insert note to continue`, `Not enough slots in TODO (3/3)`,
  `Copper is busy with SHOP-12`, `Please wait… Paula is thinking`.
- Errors explain **what happened** and **what to do**: `QA is offline. Enable QA in the Staff
  room or review SHOP-12 yourself.`
- Numbers and IDs are always shown (`SHOP-12`, `ADR-SHOP-0003`, `N-42`) and clickable.

---

## 11. Responsiveness

- Target ≥ 1024 CSS px width. The integer scale drops (×4 → ×3 → ×2) before layout changes.
- Below 1024 px: windows open maximized one at a time; the Office View shows the
  "Please use a larger screen" requester (Constitution Article XXI).

---

## 12. Design review checklist

```
- [ ] Tokens only (colors, spacing, fonts); OCS palette check green
- [ ] Integer scaling; no forbidden effects (§1.1)
- [ ] All component states designed and screenshot-tested
- [ ] Contrast pairs from §3.5 only
- [ ] Keyboard + focus + reduced motion verified
- [ ] Assets: indexed PNG, atlas naming §8, LICENSES.md updated
- [ ] Copy follows §10
- [ ] No audio of any kind (§9)
```

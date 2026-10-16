# WP07 — Amiga UI Kit

| Field        | Value |
| ------------ | ----- |
| Milestone    | M1 — Kickstart |
| Status       | READY |
| Depends on   | WP01 (frontend skeleton), WP03 (visual/axe jobs wiring) |
| Enables      | WP08, WP09, WP10, WP11, WP12 (palette), WP14, WP16, WP18, WP23 |
| Constitution | §4.1, §4.4, Article XIV (§14.1–14.10) |
| Guides       | [DESIGN.md](../../.docs/DESIGN.md) · [FRONTEND.md](../../.docs/FRONTEND.md) §3, §7, §9–10 |
| Skills       | `designing-amiga-ui`, `delivering-features`, `writing-adrs` |
| Estimate     | 47 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-07.01 — Design tokens and themes (2 pts)
- [ ] US-07.02 — Integer scale and logical pixels (3 pts)
- [ ] US-07.03 — Bitmap fonts with verified license (3 pts)
- [ ] US-07.04 — Screen and title bar with drive LED (3 pts)
- [ ] US-07.05 — Window manager: drag, depth, zoom, close, resize, focus (8 pts)
- [ ] US-07.06 — Window keyboard control and accessibility (3 pts)
- [ ] US-07.07 — Button and bevels (2 pts)
- [ ] US-07.08 — Text field, checkbox and radio (3 pts)
- [ ] US-07.09 — Cycle, slider and scroller (5 pts)
- [ ] US-07.10 — Icon and right-mouse menu (5 pts)
- [ ] US-07.11 — Requester (modal dialog) (3 pts)
- [ ] US-07.12 — Pointer and Guru Meditation component (2 pts)
- [ ] US-07.13 — Component gallery and visual regression (3 pts)
- [ ] US-07.14 — Automated accessibility checks (2 pts)

## 1. Objective

Build the reusable Amiga Workbench 1.3 component kit (`frontend/src/ui-amiga/`) exactly as
specified in DESIGN.md: tokens, themes, integer scaling, bitmap fonts, screen, window manager,
gadgets, requesters, pointer and Guru screen — every component in every state, accessible,
screenshot-tested, and silent (no audio).

## 2. Scope

**In:** tokens and themes; `useIntegerScale`; fonts (license ADR); `AmigaScreen`,
`AmigaWindow` + window manager store (`workbench`), `AmigaButton`, `AmigaTextField`,
`AmigaCheckbox`, `AmigaRadio`, `AmigaCycle`, `AmigaSlider`, `AmigaScroller`, `AmigaIcon`,
`AmigaMenu`, `AmigaRequester`, `AmigaPointer`, `AmigaGuru`; dev-only gallery route; Playwright
visual regression and axe checks.

**Out:** domain windows (WP08+), office canvas (WP14), pixel-art icons beyond placeholders
(WP12), CRT overlay (WP23).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D07.1 | Foundations | Tokens (wb13/wb20), OCS palette check green, integer `--px`, licensed bitmap fonts | Palette check; scale unit tests; font ADR | US-07.01 – US-07.03 |
| D07.2 | Screen & windows | Screen with title bar + LED; window manager with drag/depth/zoom/close/resize, focus stack, keyboard | Component tests; visual baselines | US-07.04 – US-07.06 |
| D07.3 | Gadgets | Button, TextField, Checkbox, Radio, Cycle, Slider, Scroller, Icon, Menu, Requester, Pointer, Guru — all states | Component tests; visual baselines per state | US-07.07 – US-07.12 |
| D07.4 | Quality harness | Dev gallery, Playwright visual regression, axe zero violations | `visual` and axe jobs green | US-07.13, US-07.14 |

## 4. User stories

### D07.1 — Foundations

#### US-07.01 — Design tokens and themes

- [ ] **US-07.01 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a UI developer, I want all colors and spacings as tokens with two themes, so that
  every component looks consistent and themes switch by changing four values.
- **Acceptance criteria:**
  - [ ] AC1 — `tokens.css` defines exactly the tokens of DESIGN.md §2–3 (chrome, semantic,
    spacing) on `:root`; `[data-wb-theme="wb20"]` overrides only the four chrome tokens.
  - [ ] AC2 — The palette check (WP03) passes; a fixture with `#0056AA` fails.
  - [ ] AC3 — A lint/CI grep fails if a hex color appears in any `.vue` `<style>` block.
  - [ ] AC4 — `base.css` applies `image-rendering: pixelated`, disables font smoothing, sets the
    desktop background, and contains no forbidden properties (DESIGN.md §1.1).
- **Tasks:**
  - [ ] Write `tokens.css`, `base.css`.
  - [ ] Add the hex-in-style check to the frontend lint script.
- **Tests:** palette check fixtures; a Vitest test parsing `tokens.css`.
- **Done when:** tokens imported in `main.ts`.

#### US-07.02 — Integer scale and logical pixels

- [ ] **US-07.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want the Workbench crisp at any screen size, so that pixels are never
  blurry.
- **Acceptance criteria:**
  - [ ] AC1 — `useIntegerScale()` sets `--px` to the largest integer such that the 640×256
    logical Workbench fits the viewport, with thresholds of DESIGN.md §2 (×2 ≥ 1280, ×3 ≥ 1920,
    ×4 ≥ 2560 CSS px wide) and a user override (Preferences later).
  - [ ] AC2 — Window resize recomputes the scale (debounced 100 ms).
  - [ ] AC3 — `devicePixelRatio` is taken into account so a logical pixel maps to whole device
    pixels when possible.
  - [ ] AC4 — Below 1024 px width the composable reports `compact=true` (used by WP08).
- **Tasks:** composable, unit tests with mocked `window`.
- **Tests:** Vitest table-driven tests.
- **Done when:** `--px` used by all components.

#### US-07.03 — Bitmap fonts with verified license

- [ ] **US-07.03 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want an authentic Topaz-style font that we are legally
  allowed to ship, so that text looks Amiga without licensing risk.
- **Acceptance criteria:**
  - [ ] AC1 — A repository ADR records the chosen `--font-ui` and `--font-read` fonts, source,
    author, license text, and why they are compatible.
  - [ ] AC2 — Fonts are self-hosted WOFF2 in `frontend/src/assets/fonts/`, listed in
    `assets/LICENSES.md`, `font-display: block`.
  - [ ] AC3 — Text renders only at 1× (8 px logical) and 2× (16 px logical); a utility class set
    enforces it.
  - [ ] AC4 — Fallback stack works when the font fails to load (test with blocked request).
- **Tasks:** font research spike (time-box 2 h), ADR, `@font-face` rules.
- **Tests:** Playwright visual baseline of a text sample.
- **Done when:** ADR accepted by the owner.

### D07.2 — Screen & windows

#### US-07.04 — Screen and title bar with drive LED

- [ ] **US-07.04 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want the Workbench screen with its title bar, so that the app feels
  like an Amiga from the first second.
- **Acceptance criteria:**
  - [ ] AC1 — `AmigaScreen` renders the title bar (10 logical px) with left text
    `My Workbench`, a status slot, a drive LED and a depth gadget, over the desktop area.
  - [ ] AC2 — The LED has states `idle`, `busy` (LLM job running), `offline` (WebSocket
    disconnected, red) passed as a prop; under reduced motion it never blinks.
  - [ ] AC3 — The status slot accepts text (e.g. `3 agents busy · 2 cards in review`) and is an
    `aria-live="polite"` region.
- **Tasks:** component, props types, styles.
- **Tests:** component tests; visual baselines for LED states.
- **Done when:** used by `App.vue`.

#### US-07.05 — Window manager: drag, depth, zoom, close, resize, focus

- [ ] **US-07.05 completed** · **Points:** 8 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want real Workbench windows I can move, stack, zoom, resize and close,
  so that I can arrange my dashboard freely.
- **Acceptance criteria:**
  - [ ] AC1 — `AmigaWindow` renders drag bar with title, close gadget (left), zoom and depth
    gadgets (right), size gadget (bottom-right) and Amiga scrollers when content overflows.
  - [ ] AC2 — Dragging the title bar moves the window in whole logical pixels; the title bar can
    never leave the screen.
  - [ ] AC3 — Depth gadget toggles front/back; clicking a window activates it (accent title bar
    with drag lines); inactive windows show the inactive style.
  - [ ] AC4 — Zoom toggles between user size and maximum; resize respects the 120×60 minimum.
  - [ ] AC5 — The `workbench` Pinia store holds open windows, z-order, active window,
    geometry; it exposes `open(id, props)`, `close(id)`, `focus(id)`, `toFront`, `toBack`.
  - [ ] AC6 — Optional zoom-box opening outline (4 steps, ≤ 120 ms), disabled under reduced
    motion.
- **Tasks:** component, `useWindowDrag`, `useWindowResize`, store.
- **Tests:** component tests with simulated pointer events; store unit tests; visual baselines
  active/inactive.
- **Done when:** gallery shows three overlapping windows.

#### US-07.06 — Window keyboard control and accessibility

- [ ] **US-07.06 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a keyboard user, I want to operate windows without a mouse.
- **Acceptance criteria:**
  - [ ] AC1 — Each window is `role="dialog"` (non-modal) with `aria-labelledby` its title.
  - [ ] AC2 — `Ctrl/⌘+\`` cycles windows; `Esc` closes the active window (unless it opts out);
    arrow keys with `Alt` move, with `Alt+Shift` resize the active window.
  - [ ] AC3 — Gadgets are focusable buttons with labels (`Close window`, `Zoom`, `Depth`).
  - [ ] AC4 — Focus moves into a window on open and returns to the previous element on close.
- **Tasks:** keyboard composable; aria wiring.
- **Tests:** component tests; Playwright keyboard-only test.
- **Done when:** axe has no violations in the window gallery.

### D07.3 — Gadgets

#### US-07.07 — Button and bevels

- [ ] **US-07.07 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a UI developer, I want the Workbench button and bevel primitives.
- **Acceptance criteria:**
  - [ ] AC1 — `AmigaButton` raised bevel per DESIGN.md §5.4; pressed inverts; focus dotted accent
    outline; disabled ghosted with a dither pattern (no opacity).
  - [ ] AC2 — CSS utilities `.bevel-raised`, `.bevel-recessed` reused by other components.
  - [ ] AC3 — Native `<button>` underneath; `type` prop defaults to `button`.
- **Tasks:** component + utilities.
- **Tests:** component tests; visual baselines for 4 states.
- **Done when:** used by window gadgets.

#### US-07.08 — Text field, checkbox and radio

- [ ] **US-07.08 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want Amiga-style inputs for forms (project creation, notes, staff).
- **Acceptance criteria:**
  - [ ] AC1 — `AmigaTextField` (single and multi-line) with recessed bevel, block accent cursor,
    inverse-video selection, `defineModel<string>()`, label association, error state with text.
  - [ ] AC2 — `AmigaCheckbox` and `AmigaRadio` per DESIGN.md §5.4 with keyboard (Space/arrows).
  - [ ] AC3 — All inputs expose `aria-invalid` and `aria-describedby` for errors.
- **Tasks:** three components.
- **Tests:** component tests; visual baselines (default, focus, error, disabled).
- **Done when:** gallery shows a sample form.

#### US-07.09 — Cycle, slider and scroller

- [ ] **US-07.09 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want the Amiga cycle gadget, sliders and proportional scrollers.
- **Acceptance criteria:**
  - [ ] AC1 — `AmigaCycle` cycles options on click; `Alt+↓` opens a listbox; implements the
    ARIA combobox/listbox pattern.
  - [ ] AC2 — `AmigaSlider` proportional knob in a recessed track; keyboard arrows/PageUp/PageDown;
    `role="slider"` with value attributes.
  - [ ] AC3 — `AmigaScroller` replaces native scrollbars in windows: knob size proportional to
    the visible fraction; arrow buttons; wheel and keyboard scrolling still work.
- **Tasks:** three components + `useProportional` helper.
- **Tests:** component tests; visual baselines.
- **Done when:** windows use `AmigaScroller`.

#### US-07.10 — Icon and right-mouse menu

- [ ] **US-07.10 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want desktop icons and the right-mouse menu bar, so that navigation
  feels like Workbench — with a visible keyboard alternative.
- **Acceptance criteria:**
  - [ ] AC1 — `AmigaIcon` 32×32 image + label; single click selects (inverse), double click or
    Enter opens; draggable on the desktop in logical pixels.
  - [ ] AC2 — `AmigaMenu`: holding the right mouse button over the title bar shows the menu
    bar; releasing over an item activates it; items show `Right-Amiga+<key>` mapped to
    `Ctrl/⌘+<key>`.
  - [ ] AC3 — Every menu action is also reachable through a visible button or a keyboard
    shortcut; `F10` opens the menu bar for keyboard users (ARIA menubar pattern).
  - [ ] AC4 — The native context menu is suppressed only over the title bar.
- **Tasks:** components, shortcut registry composable.
- **Tests:** component tests; Playwright test of right-button interaction.
- **Done when:** gallery shows icons and a menu.

#### US-07.11 — Requester (modal dialog)

- [ ] **US-07.11 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want Workbench requesters for confirmations and errors.
- **Acceptance criteria:**
  - [ ] AC1 — `AmigaRequester` is a modal `<dialog>` with focus trap, 1–3 buttons, affirmative
    left, cancel right; `Enter` affirmative, `Esc` cancel.
  - [ ] AC2 — A `useRequester()` composable returns a promise resolving to the chosen button.
  - [ ] AC3 — Error variant shows title, detail and the correlation id in small text.
- **Tasks:** component, composable, host in `AmigaScreen`.
- **Tests:** component tests; Playwright keyboard test.
- **Done when:** used by WP08 refusals.

#### US-07.12 — Pointer and Guru Meditation component

- [ ] **US-07.12 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want the Workbench pointer and, if something fatal happens, the Guru
  Meditation screen.
- **Acceptance criteria:**
  - [ ] AC1 — CSS cursors (PNG, 2 colors + outline) for default and busy ("zZ"); busy only for
    blocking operations.
  - [ ] AC2 — `AmigaGuru` renders exactly the text of Constitution §4.4 with error code and
    correlation id; the red frame blinks at 1 Hz, static under reduced motion; left click or
    Enter triggers `@continue`.
  - [ ] AC3 — No sound is produced anywhere (lint rule verified).
- **Tasks:** cursor assets (placeholders until WP12), component.
- **Tests:** component tests; visual baseline (static frame).
- **Done when:** gallery shows the Guru screen.

### D07.4 — Quality harness

#### US-07.13 — Component gallery and visual regression

- [ ] **US-07.13 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a reviewer, I want every component state visible in one page and protected by
  screenshots, so that visual regressions are caught automatically.
- **Acceptance criteria:**
  - [ ] AC1 — Route `/__gallery` (dev builds only) renders every component in every state of
    DESIGN.md §5 with both themes.
  - [ ] AC2 — Playwright visual tests capture each section at scale ×2 with fonts loaded and
    animations disabled; baselines committed.
  - [ ] AC3 — CI job `visual` runs against the frontend dev image and fails on pixel diffs above
    0 (exact match, since pixel art must be exact).
- **Tasks:** gallery view, Playwright project config, CI job.
- **Tests:** itself.
- **Done when:** `visual` job required.

#### US-07.14 — Automated accessibility checks

- [ ] **US-07.14 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a user with assistive technology, I want the kit to be accessible by default.
- **Acceptance criteria:**
  - [ ] AC1 — `@axe-core/playwright` runs on every gallery section with zero violations.
  - [ ] AC2 — Contrast of every token pair used for text is verified against DESIGN.md §3.5.
- **Tasks:** axe test; contrast test script.
- **Tests:** itself.
- **Done when:** checks part of the `visual` job.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP07 closing: Amiga UI kit`); story ADR ids filled in (font ADR mandatory).
- [ ] File status set to `DONE`.
- [ ] All stories checked; every component documented in the gallery with all states.
- [ ] Visual and axe checks required in CI; no audio anywhere.
- [ ] DESIGN.md updated with any measured deviation.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| No suitably licensed Topaz-style font | Spike early (US-07.03); fallback: draw our own bitmap font in Aseprite (WP12) |
| Pixel-exact screenshots differ across platforms | Run visual tests only in the pinned container; fonts self-hosted |
| Right-mouse menu conflicts with browser behavior | Suppress only over the title bar; keyboard path always present |

## 7. Blockers

None.

---
name: designing-amiga-ui
description: Amiga 500 Workbench 1.3 design system for My Workbench - OCS 12-bit palette tokens, Topaz-style bitmap typography, bevels, windows, gadgets, requesters, icons, Guru Meditation screen, pixel-perfect rendering, asset licensing, and WCAG 2.2 AA accessibility. Use when building or reviewing any Vue component, CSS, icon, font, or visual asset in frontend/src/ui-amiga or frontend/src/windows.
---

# Designing Amiga UI

Authoritative sources: Constitution Articles IV and XIV (principles) and `.docs/DESIGN.md`
(full specification: tokens, measures, components, assets). Code rules: `.docs/FRONTEND.md`.

## Hard rules

- No gradients, no rounded corners, no blur shadows, no translucency in chrome. Dithering OK.
- Hard pixel edges: `image-rendering: pixelated`; integer scaling only; text never sub-pixel
  scaled.
- Every color is **OCS 12-bit**: each channel is a doubled nibble (`#0055AA` ✅, `#0056AA` ❌).
  Run the palette lint; it fails CI otherwise.
- Use only tokens from `frontend/src/ui-amiga/tokens.css`; never inline hex values in
  components.
- UI chrome is DOM (accessible), built as Vue SFCs (`<script setup lang="ts">`) — no third-party
  UI component library. Only the Office View is canvas (PixiJS).
- **No audio, ever** (Constitution §14.10): no sound files, libraries or settings; the Amiga
  "beep" is the visual DisplayBeep (screen border flash).
- Assets: original or compatibly licensed, recorded in `assets/LICENSES.md`. Never rip
  Amiga ROM/disk/game assets.

## Tokens (Workbench 1.3 default)

```css
:root {
  --wb-bg: #0055AA;     /* desktop + window background */
  --wb-fg: #FFFFFF;     /* text on blue, bevel highlight */
  --wb-ink: #000022;    /* text, borders, bevel shadow */
  --wb-accent: #FF8800; /* selection, focus, cursor, pointer */
  --px: 2px;            /* one logical pixel at current integer scale; set by JS */
}
```

Workbench 2.0 theme swaps only these four tokens (`#AAAAAA`, `#FFFFFF`, `#000000`, `#6688BB`).
Semantic tokens and contrast pairs: DESIGN.md §3 — status color is never the only signal.

## Geometry (logical pixels, multiply by `--px`)

- Bevel raised: 1 px white top/left, 1 px black bottom/right; pressed = inverted.
- Window border 2 px; title bar 10 px; gadgets 10×10 (close left; depth/zoom right; size
  bottom-right).
- Text: Topaz-style 8 px at 1×, headings 2×. No other sizes.

## Component inventory

`Screen`, `Window`, `Requester`, `Button`, `TextField`, `Checkbox`, `Radio`, `Cycle`, `Slider`,
`Scroller`, `Icon`, `Menu`, `Shell`, `Pointer`, `Guru`. Check Constitution §14.4 for the Amiga
reference of each. Build each with all states: default, hover, focus, pressed, disabled, error,
loading, empty.

## Behavior

- Transitions instant or stepwise; optional 4-step zoom-box outline on window open (≤ 120 ms).
- Requesters: max 3 buttons, affirmative left, `Cancel` right; Esc cancels.
- Right-mouse menu bar on the screen title, **and** a visible keyboard alternative
  (`Right-Amiga+X` label mapped to Ctrl/⌘+X).
- Busy pointer only for blocking operations.
- Guru Meditation only for fatal client errors: black background, red blinking frame,
  `Software Failure.  Press left mouse button to continue.` /
  `Guru Meditation #<errorCode>.<correlationId>`. Static frame under reduced motion.

## Accessibility (WCAG 2.2 AA)

- Semantic elements first (`button`, `dialog`, `input`); ARIA only when needed.
- Focus visible: 1 logical px orange dotted outline.
- Full keyboard support: Tab order, arrows in lists/menus, Enter/Space activate, Esc closes.
- `prefers-reduced-motion` disables blinking and zoom-box animation.
- Contrast: verify every text/background token pair (white on `#0055AA` passes).

## Copy tone

English, short, friendly-retro: "Insert note to continue", "Not enough slots in TODO (3/3)".

## Review checklist

```
- [ ] Only tokens used; palette lint green
- [ ] Integer scaling, no blur, no rounded corners
- [ ] All states implemented; keyboard path works; focus visible
- [ ] Visual regression screenshot updated intentionally
- [ ] New assets listed in assets/LICENSES.md
```

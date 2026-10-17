# ADR-0011: US-01.06: Strict ESLint flat config loaded natively, a boundaries matrix, a no-audio lint set and committed lint fixtures

- Status: Proposed
- Date: 2026-10-17
- Deciders: Project owner
- Related: Constitution §14.10, §15.2, §18.2; [STACK.md](../STACK.md) §1.1, §1.4, §1.7, §3, §9;
  [FRONTEND.md](../FRONTEND.md) §1, §1.1, §2, §8.6, §11; [DOCKER.md](../DOCKER.md) §6;
  [ADR-0004](0004-per-service-python-projects.md),
  [ADR-0009](0009-us-01-04-quality-gates-as-tool-config-and-stdlib-scripts.md),
  [ADR-0010](0010-us-01-05-frontend-scaffold-pnpm-settings-and-nginx-image.md); US-01.06;
  review findings R8, R9, R10, R18 (`.project/execution/wp01-repository-and-toolchain.review.md`)

## Context

US-01.06 makes the frontend strictly checked: every FRONTEND.md §2 compiler option in
`tsconfig.app.json` and `tsconfig.node.json`, an `eslint.config.ts` that enforces the §2 rules,
the §1.1 module boundaries and the no-audio rule (Constitution §14.10), a Prettier config, and a
`check:tooling` script proving that negative fixtures fail and positive fixtures pass. The forces:

1. ADR-0009 (Alternative 3) rejected committed, lint-excluded fixture files for the Python
   services and generated negative fixtures at test time instead. The TypeScript rules in use
   are *typed* (`strictTypeChecked`, `consistent-type-imports`, `boundaries` with `import type`),
   so a fixture must belong to a TypeScript project to be linted at all.
2. ESLint 10 loads a `.ts` config either through the optional `jiti` package or through Node's
   native type stripping behind the flag `unstable_native_nodejs_ts_config`. STACK.md §1.1
   wants stable tools, §1.7 minimal dependencies.
3. `eslint@10.13.0`, the STACK.md §3 pin, was published 2026-10-16T14:24Z and is younger than
   pnpm's default `minimumReleaseAge`; a frozen install fails without an exemption. STACK.md is
   changed only through an ADR.
4. `eslint-plugin-boundaries` must encode the FRONTEND.md §1.1 matrix, including type-only edges
   and the "no framework" rule of `shared/`, `api/`, `office-engine/` and `office-renderer/`.
5. Constitution §14.10 forbids any sound: audio libraries, Web Audio, speech synthesis, audio
   files and `<audio>`/`<video>` with sound.
6. Config files and the tooling script run on Node 24 and need its types; Prettier and ESLint
   must not fight over style.

## Decision

We will:

1. **Commit the lint fixtures under `frontend/tooling-fixtures/`** (departing from ADR-0009
   Alternative 3, R8). Typed linting needs a tsconfig, so `tooling-fixtures/tsconfig.json`
   extends `tsconfig.app.json` and includes only `tooling-fixtures/src/`; the fixtures are never
   built, never part of `pnpm typecheck` and absent from the runtime image. The ESLint `ignores`
   entry is scoped to `tooling-fixtures/src/` only (the check script itself is linted).
   `tooling-fixtures/check-tooling.ts` lints the fixtures with `ignore: false` and asserts each
   expected message by rule id, file, line and severity (and message text where two config
   entries share a rule id), rejects fatal parse errors, requires every positive fixture to lint
   clean, and asserts the strict compiler options of both tsconfigs (read with
   `ts.readConfigFile` + `parseJsonConfigFileContent`, so JSONC and `extends` work).
2. **Load `eslint.config.ts` with Node's native type stripping** (R9):
   `eslint --flag unstable_native_nodejs_ts_config` in `pnpm lint`, and
   `flags: ['unstable_native_nodejs_ts_config']` in the check script. The config uses erasable
   syntax only. **Re-check trigger:** at every ESLint update, and as soon as the flag becomes
   stable (switch to the stable behavior) or is renamed/removed (adapt, or fall back to
   Alternative 2a/2b below through a new ADR).
3. **Adopt the STACK.md §1.4 release-age exemption policy** (R10, R18): pnpm's
   `minimumReleaseAge` stays on; a pinned latest-stable release younger than the quarantine may
   be exempted only by an exact `name@version` entry in `minimumReleaseAgeExclude` of
   `frontend/pnpm-workspace.yaml`, with a comment naming the publish date; the entry is removed
   as soon as a frozen install passes without it, and at the latest at the next update of that
   package. The current entry is `eslint@10.13.0` (still required on 2026-10-17 at 07:17Z).
4. **Add two direct dependencies**: `eslint-config-prettier` 10.1.8 (turns off the stylistic rules
   Prettier owns, applied last) and `@types/node` 24.19.2 (types for config files and the tooling
   script; the major is held to the pinned Node.js 24 runtime, STACK.md §9 hold row, although
   26.x exists).
5. **Add no import resolver package**: `import/resolver` uses the built-in `node` resolver with
   `.ts`, `.d.ts` and `.vue` extensions. **Add no `@` path alias yet** (as ADR-0010): relative
   imports suffice while `src/` is a skeleton; a later story may add the alias with its resolver.
6. **Encode the FRONTEND.md §1.1 matrix** with `boundaries/dependencies`, `default: 'disallow'`,
   `checkAllOrigins: true` and `checkInternals: false` (imports inside one element are not
   checked). Every element may use core modules and external packages, except: one shared
   `frameworkPackages` constant (`vue`, `vue-router`, `pinia`, `@vue/*`) is disallowed for
   `shared`, `api`, `office-engine` and `office-renderer`; `office-engine` also disallows
   `pixi.js`/`@pixi/*` and may import types from `api/` only from `api/schema.d.ts`; `stores` may
   import `office-engine` types only; PixiJS imports are restricted to `office-renderer` by
   `no-restricted-imports`. Elements match `src/<type>` from the right of the path, so the
   fixtures are classified like the real folders.
7. **Accept two known limits of the matrix**, documented in FRONTEND.md §11 and checked in
   review: files outside the elements (`main.ts`, `App.vue`, `router.ts`, `assets/`) are
   unclassified and imports of them are not checked; `ui-amiga → composables` is allowed for
   every composable, since the lint cannot tell the "generic ones only" of §1.1 apart.
8. **Enforce no audio in lint** (Constitution §14.10): `no-restricted-globals` and
   `no-restricted-properties` (on `window`, `globalThis`, `self`) for `Audio`, `AudioContext`,
   `OfflineAudioContext`, `webkitAudioContext`, `HTMLAudioElement`, `speechSynthesis`,
   `SpeechSynthesisUtterance`; `no-restricted-imports` for `@pixi/sound`, `howler`, `tone` and
   audio file extensions (any case, optional Vite `?query`), repeated in the `office-renderer`
   override; `no-restricted-syntax` for `createElement`/`createElementNS` with `audio`/`video` as
   a string or static template literal; `vue/no-restricted-html-elements` for `<audio>`; and
   `vue/no-restricted-syntax` for a `<video>` whose own start tag lacks a static `muted`. Every
   message cites §14.10. **Known limit:** runtime-computed tag names and dynamic imports built at
   runtime are not caught; review checks them.
9. **Run the full frontend gate everywhere it is documented**: DOCKER.md §6 runs `pnpm lint`,
   `format:check`, `typecheck`, `test`, `build` and `check:tooling` in both the compose and the
   interim `docker build --target dev` lines.

## Alternatives Considered

1. **Fixtures generated at test time, as ADR-0009 decided for Python** — no excluded files in
   the tree; but typed rules need the files inside a TypeScript project, so the script would have
   to write a temporary tsconfig and the whole fixture tree on every run, and the fixtures would
   be invisible to reviewers. Rejected. **Fixtures inside `src/` with inline disables** — no
   ignore entry, but they would ship in the build and disables hide rules. Rejected.
2. **Load the TypeScript config another way** — (a) **`jiti`**: stable ESLint path, but an extra
   dependency only to read one file, against STACK.md §1.7; rejected for now. (b)
   **`eslint.config.js`**: no flag and no dependency, but the config loses type checking (it
   is part of the strict `tsconfig.node.json` project) and departs from the story AC and
   FRONTEND.md §11, which name `eslint.config.ts`; rejected.
3. **Release-age quarantine** — (a) **disable `minimumReleaseAge`** globally: simplest, but drops
   a supply-chain control for every package; rejected. (b) **pin `eslint@10.12.x`** until the
   quarantine passes: violates STACK.md §1.1 "latest stable on the day it is added" and churns the
   pin a day later; rejected.
4. **`eslint-import-resolver-typescript`** — resolves `paths` aliases, but there is no alias yet,
   so it would be a dependency without a use; rejected until an alias exists.
5. **Classify `main.ts`, `App.vue`, `router.ts` as an `app` element** — would check them, but
   §1.1 defines no row for them; inventing one is a design decision for WP08. Deferred.

## Consequences

- Positive: every ESLint rule and boundary edge is proven both ways (45 expected errors,
  11 clean positive fixtures; container mutation runs caught every mutation in review Round 2);
  no-audio is enforced at lint time; no extra dependency for TS config loading or resolution.
- Negative: `tooling-fixtures/src/` is an ignore entry where code could hide (mitigated: it
  contains only fixtures, each asserted by the check); the unstable ESLint flag can change in a
  minor release; the release-age exemption is manual upkeep; two matrix limits are left to review.
- Risks and mitigations: a renamed flag breaks `pnpm lint` loudly, not silently (re-check at each
  ESLint update); a stale exemption is removed by the STACK.md §1.4 trigger and Renovate
  (US-01.10); holding `@types/node` at 24 is re-checked with the Node.js hold (STACK.md §9).

## Compliance

- `pnpm check:tooling` (DOCKER.md §6 gate, CI from WP03) fails if any negative fixture stops
  failing with its exact rule/file/line, if any positive fixture reports a message, or if a
  strict compiler option is missing from `tsconfig.app.json` or `tsconfig.node.json`.
- `pnpm lint --max-warnings 0` stays green on the real code with the fixtures ignored.
- `scripts/check_frontend_pins.py` keeps `eslint-config-prettier` and `@types/node` equal to
  STACK.md §3.
- Review checks: the `minimumReleaseAgeExclude` list holds only exact `name@version` entries with
  a publish-date comment and is emptied per STACK.md §1.4; the ESLint flag is re-checked at every
  ESLint update; unclassified files and generic-only composables follow FRONTEND.md §1.1.

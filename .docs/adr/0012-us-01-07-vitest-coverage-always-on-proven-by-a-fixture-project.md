# ADR-0012: US-01.07: Vitest coverage always on with explicit include, proven by a fixture project, and seeded property tests

- Status: Proposed
- Date: 2026-10-17
- Deciders: Project owner
- Related: Constitution §15.11, §18.2; [PRINCIPLES.md](../PRINCIPLES.md) (deterministic tests);
  [FRONTEND.md](../FRONTEND.md) §1, §10, §11; [STACK.md](../STACK.md) §3;
  [ADR-0009](0009-us-01-04-quality-gates-as-tool-config-and-stdlib-scripts.md),
  [ADR-0011](0011-us-01-06-eslint-boundaries-no-audio-lint-and-committed-fixtures.md)
  (refines its Decision 1); US-01.07; review findings R1–R6, R8, R16–R20
  (`.project/execution/wp01-repository-and-toolchain.review.md`)

## Context

US-01.07 gives the frontend a Vitest gate: specs in `src/**/*.spec.ts` under jsdom, v8 coverage,
a 70 % global threshold that fails the run, and a fast-check property test that proves the wiring.
The forces:

1. Constitution §18.2 sets coverage gates ("others ≥ 70 %"; stricter for some areas later) and CI
   must block on them. A gate that only fires when a script remembers `--coverage`, or that
   ignores files no spec imports, reports 100 % while code is untested (review R1, R2).
2. ADR-0009 taught that a rule nobody has seen fail is not a rule: the threshold must be proven to
   fire from the real configuration, not from a copy of it.
3. ADR-0011 Decision 1 placed lint fixtures in `tooling-fixtures/src/`, ESLint-ignored and never
   type-checked, on the premise that the folder holds only asserted lint fixtures. A coverage
   fixture is ordinary code and should be checked like `src/` (R4).
4. The root `.gitignore` ignores every `coverage/` folder, so a fixture at
   `tooling-fixtures/coverage/` would never be committed.
5. PRINCIPLES.md requires deterministic tests; fast-check picks a random seed per run (R3, R16).
6. Constitution §15.11 says all configuration is a `VO_`-prefixed environment variable in
   `.env.example`; a seed override for the test runner is an environment variable too (R17).
7. WP03 needs a machine-readable coverage artifact in CI (R6).

## Decision

We will:

1. **Enable v8 coverage in `vitest.config.ts` itself** (`coverage.enabled: true`), so every
   `vitest run` — `pnpm test`, `pnpm coverage` or a bare call — measures coverage and enforces the
   thresholds. Only `pnpm test:watch` opts out (`--coverage.enabled=false`) for the TDD loop.
2. **Set an explicit `coverage.include: ['src/**/*.{ts,vue}']`**, so a file no spec imports counts
   as 0 %. **Exclude** specs, `*.d.ts` and `src/main.ts` (it only mounts the app on the real DOM;
   what it wires is covered by `App.spec.ts`).
3. **Use a 70 % global threshold on all four metrics** (lines, functions, statements, branches),
   Constitution §18.2 "others". Stricter per-folder thresholds (e.g. `office-engine`) are added in
   the same change as the code they cover.
4. **Set the reporters only in the config**: `text` (the table), `json-summary`
   (`coverage/coverage-summary.json`) and `html` (`coverage/index.html`). No script passes
   `--coverage.reporter`, because a CLI list replaces the configured one. WP03 adds the cobertura
   XML reporter for the CI artifact.
5. **Prove the gate in `pnpm check:tooling`** by running the real `pnpm run test` script with
   `--root tooling-fixtures/under-covered/` (so the real `vitest.config.ts` applies; `setupFiles`
   is an absolute path for that reason) and a temporary `reportsDirectory`. The fixture has one
   passing spec that fully covers `shared/covered.ts` and a `shared/never-imported.ts` that nothing
   imports. The check expects the run to fail on all four metrics, expects the never-imported file
   at 0 % and the covered file at ≥ 70 % in `coverage-summary.json`, and reads the test counts from
   Vitest's `json` reporter (`--reporter=json --outputFile.json=<tmp>`), not from the human summary.
   Dropping `coverage.include`, `coverage.enabled` or the `json-summary` reporter fails the check.
6. **Place the fixture at `tooling-fixtures/under-covered/`**, not `tooling-fixtures/coverage/`,
   which the root `.gitignore` rule `coverage/` would hide.
7. **Refine ADR-0011 Decision 1**: `tooling-fixtures/` now holds two kinds of fixture.
   - Lint fixtures in `tooling-fixtures/src/`: ESLint-ignored, linted only by
     `check-tooling.ts` (with `ignore: false`), not type-checked by `pnpm typecheck`
     (unchanged).
   - The coverage fixture project `tooling-fixtures/under-covered/`: ordinary source, linted by
     `pnpm lint` and type-checked by `pnpm typecheck` like `src/`. It has its own `tsconfig.json`
     (extends `tsconfig.app.json`), referenced from the root `tsconfig.json`. It is never built
     and never in the runtime image.
8. **Seed fast-check deterministically**: `vitest.setup.ts` (a Vitest `setupFiles` entry) calls
   `fc.configureGlobal({ seed: propertySeed(process.env['FC_SEED']) })`; `vitest.seed.ts` exports
   the fixed `defaultPropertySeed = 20261017` and `propertySeed`, which returns the default when
   `FC_SEED` is unset or empty, the integer when it is a safe integer, and throws `RangeError`
   otherwise. `vitest.seed.spec.ts` asserts the parsing and that the configured global seed
   equals `propertySeed(FC_SEED)`.
9. **Name the override `FC_SEED`, without the `VO_` prefix.** We read Constitution §15.11 as
   covering the *runtime configuration of the services* (what `.env.example` documents and the
   compose stack injects), not test-runner knobs. `FC_SEED` is never read by application code,
   never set in compose and not in `.env.example`. FRONTEND.md §10 records this.
10. **Use `clamp` as the sample pure util** in `src/shared/clamp.ts`. It rejects an inverted or
    `NaN` range with `RangeError`. `shared/clamp.spec.ts` (examples plus fast-check properties) is
    the reference example of FRONTEND.md §10.

## Alternatives Considered

1. **Coverage only through the CLI** (`vitest run --coverage` in the `test` script) — the
   Vitest default; but `vitest run` alone, or a script edit, silently drops the gate (R2), and the
   check would have to repeat the flag. Rejected.
2. **Coverage of imported files only (no `coverage.include`)** — fewer config lines, but an
   untested module is invisible and the totals stay at 100 % (R1, mutation-checked). Rejected.
3. **Assert the thresholds by reading `vitest.config.ts`** instead of running Vitest — fast, but
   it proves the numbers are written, not that the run fails; rejected after ADR-0009. **Spawn
   `node_modules/vitest/vitest.mjs` with `--coverage`** — depends on an internal path and bypasses
   the real script (R9, R2). Rejected.
4. **Keep the coverage fixture in `tooling-fixtures/src/`** (ESLint-ignored) — no new tsconfig, but
   the fixture would be neither linted nor type-checked, against ADR-0011's premise (R4).
   Rejected. **`tooling-fixtures/coverage/`** — clearer name, but ignored by `.gitignore`.
   Rejected.
5. **Unseeded property tests**, or a seed hard-coded in every `fc.assert` — the first is
   non-deterministic (R3); the second repeats the seed in each spec and has no override for
   exploration. Rejected.
6. **`VO_FC_SEED`** — literal compliance with §15.11, but it would mark a test-only knob as service
   configuration and suggest it belongs in `.env.example`. Rejected; the reading in Decision 9 is
   for the owner to accept or reject with this ADR.

## Consequences

- Positive: the coverage gate cannot be bypassed by a script edit; untested files count; the gate
  is proven from the real config on every `check:tooling` run (mutations of `include`, `enabled`,
  reporter and seed are caught); property tests are reproducible, and a failing seed can be
  replayed with `FC_SEED`.
- Negative: every `vitest run` pays for coverage (small on the skeleton); `test:watch` has no
  threshold feedback; a second fixture kind in `tooling-fixtures/` with its own tsconfig; the
  fixed seed explores one sequence per run unless someone sets `FC_SEED`.
- Risks and mitigations: a Vitest major may rename `coverage.enabled`, reporter options or the
  `json` reporter fields — `check:tooling` fails loudly; the §15.11 reading may be rejected by the
  owner — then a follow-up renames `FC_SEED` to `VO_FC_SEED` (one constant and FRONTEND.md §10);
  the cobertura reporter is a WP03 follow-up.

## Compliance

- `pnpm check:tooling` (DOCKER.md §6, CI from WP03) fails if the under-covered fixture run does
  not fail on all four metrics, if `never-imported.ts` is not reported at 0 %, or if the test
  counts differ.
- `pnpm test` runs `vitest.seed.spec.ts`, which fails on a non-fixed default seed or a global seed
  different from `propertySeed(FC_SEED)`.
- `pnpm lint` and `pnpm typecheck` cover `tooling-fixtures/under-covered/`; `eslint.config.ts`
  ignores only `tooling-fixtures/src/`.
- `scripts/check_frontend_pins.py` keeps `vitest`, `@vitest/coverage-v8`, `fast-check`, `jsdom`
  and `@vue/test-utils` equal to STACK.md §3.
- Review checks: no script passes `--coverage` or `--coverage.reporter`; new environment variables
  read by application code carry the `VO_` prefix and are in `.env.example`; per-folder thresholds
  arrive with the code they cover.

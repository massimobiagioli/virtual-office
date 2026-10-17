// Seed of the fast-check property tests (FRONTEND.md §10), applied by `vitest.setup.ts` and
// unit-tested by `vitest.seed.spec.ts`. Property tests are deterministic (PRINCIPLES.md): the
// default seed is fixed. `FC_SEED=<integer> pnpm test` explores another seed or replays the one a
// failure printed; it is a test-only knob, not runtime configuration, so it does not take the
// `VO_` prefix.

export const defaultPropertySeed = 20261017

// The seed for an `FC_SEED` value: the fixed default when unset or empty, else the integer.
export function propertySeed(value: string | undefined): number {
  if (value === undefined || value === '') {
    return defaultPropertySeed
  }
  const seed = Number(value)
  if (!Number.isSafeInteger(seed)) {
    throw new RangeError(`FC_SEED must be an integer, found "${value}"`)
  }
  return seed
}

// Vitest setup file (FRONTEND.md §10), run before every spec file. Property tests are
// deterministic (PRINCIPLES.md): fast-check uses a fixed seed. `FC_SEED=<integer> pnpm test`
// explores another seed or replays the one a failure printed; it is a test-only knob, not
// runtime configuration, so it does not take the `VO_` prefix.
import process from 'node:process'

import fc from 'fast-check'

const defaultSeed = 20261017

function propertySeed(value: string | undefined): number {
  if (value === undefined || value === '') {
    return defaultSeed
  }
  const seed = Number(value)
  if (!Number.isSafeInteger(seed)) {
    throw new RangeError(`FC_SEED must be an integer, found "${value}"`)
  }
  return seed
}

fc.configureGlobal({ seed: propertySeed(process.env['FC_SEED']) })

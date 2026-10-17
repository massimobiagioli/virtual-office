// Vitest setup file (FRONTEND.md §10), run before every spec file: fast-check uses the seed of
// `vitest.seed.ts` (fixed, or `FC_SEED`), so property tests are deterministic.
import process from 'node:process'

import fc from 'fast-check'

import { propertySeed } from './vitest.seed.ts'

fc.configureGlobal({ seed: propertySeed(process.env['FC_SEED']) })

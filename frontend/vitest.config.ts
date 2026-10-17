import { defineConfig, mergeConfig } from 'vitest/config'

import viteConfig from './vite.config.ts'

// Unit and component tests (FRONTEND.md §10): specs beside the source, jsdom, v8 coverage.
// Every run measures coverage (`enabled`, so a plain `vitest run` is the gate too; only
// `pnpm test:watch` opts out) and fails below the global thresholds of
// Constitution §18.2 ("others ≥ 70 %"); stricter per-folder thresholds (office-engine) are added
// with the code they cover.
export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      include: ['src/**/*.spec.ts'],
      coverage: {
        provider: 'v8',
        enabled: true,
        // Explicit include: files no spec imports still count, as 0 %.
        include: ['src/**/*.{ts,vue}'],
        // `main.ts` only mounts the app on the real DOM; what it wires (App, router, Pinia) is
        // covered by `App.spec.ts`. Specs and declaration files are not source.
        exclude: ['src/**/*.spec.ts', 'src/**/*.d.ts', 'src/main.ts'],
        // `text` prints the table; `json-summary` writes `coverage-summary.json`, which
        // `pnpm check:tooling` reads (WP03 adds the cobertura XML for CI artifacts).
        reporter: ['text', 'json-summary'],
        reportsDirectory: 'coverage',
        thresholds: {
          lines: 70,
          functions: 70,
          statements: 70,
          branches: 70,
        },
      },
    },
  }),
)

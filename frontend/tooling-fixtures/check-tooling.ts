// Tooling check (US-01.06): the strict TypeScript options are set, and every negative lint
// fixture fails with the exact rule, file and line it exists for. A non-zero exit alone is not
// enough: a fixture that fails for another reason (a typo, a parse error) would hide a broken
// rule (ADR-0009). Run with `pnpm check:tooling`; ESLint loads `eslint.config.ts` natively.
import { readFile } from 'node:fs/promises'
import process from 'node:process'

import { ESLint } from 'eslint'

interface LintExpectation {
  readonly file: string
  readonly ruleId: string
  readonly line: number
}

// FRONTEND.md §2: compiler options `tsconfig.app.json` must set, with their values.
const requiredCompilerOptions: Readonly<Record<string, unknown>> = {
  strict: true,
  noUncheckedIndexedAccess: true,
  exactOptionalPropertyTypes: true,
  noImplicitOverride: true,
  noFallthroughCasesInSwitch: true,
  noPropertyAccessFromIndexSignature: true,
  verbatimModuleSyntax: true,
  isolatedModules: true,
  moduleResolution: 'bundler',
  types: ['vite/client'],
}

const lintExpectations: readonly LintExpectation[] = [
  {
    file: 'tooling-fixtures/src/windows/OptionsApiWindow.vue',
    ruleId: 'vue/component-api-style',
    line: 5,
  },
  {
    file: 'tooling-fixtures/src/office-engine/imports-vue.ts',
    ruleId: 'boundaries/dependencies',
    line: 2,
  },
  {
    file: 'tooling-fixtures/src/office-engine/imports-pixi.ts',
    ruleId: 'boundaries/dependencies',
    line: 2,
  },
  {
    file: 'tooling-fixtures/src/office-engine/imports-pixi.ts',
    ruleId: 'no-restricted-imports',
    line: 2,
  },
  {
    file: 'tooling-fixtures/src/ui-amiga/imports-store.ts',
    ruleId: 'boundaries/dependencies',
    line: 2,
  },
  { file: 'tooling-fixtures/src/shared/uses-audio.ts', ruleId: 'no-restricted-imports', line: 2 },
  { file: 'tooling-fixtures/src/shared/uses-audio.ts', ruleId: 'no-restricted-globals', line: 4 },
  { file: 'tooling-fixtures/src/shared/uses-audio.ts', ruleId: 'no-restricted-globals', line: 5 },
]

function sameJson(left: unknown, right: unknown): boolean {
  return JSON.stringify(left) === JSON.stringify(right)
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

async function checkCompilerOptions(path: string): Promise<string[]> {
  const parsed: unknown = JSON.parse(await readFile(path, 'utf8'))
  const options = isRecord(parsed) ? parsed['compilerOptions'] : undefined
  if (!isRecord(options)) {
    return [`${path}: no compilerOptions object`]
  }
  return Object.entries(requiredCompilerOptions)
    .filter(([name, expected]) => !sameJson(options[name], expected))
    .map(
      ([name, expected]) =>
        `${path}: compilerOptions.${name} must be ${JSON.stringify(expected)}, ` +
        `found ${JSON.stringify(options[name])}`,
    )
}

async function checkLintFixtures(cwd: string): Promise<string[]> {
  // `ignore: false`: the fixtures are globally ignored by `pnpm lint`, which must stay green.
  const eslint = new ESLint({ cwd, ignore: false, flags: ['unstable_native_nodejs_ts_config'] })
  const files = [...new Set(lintExpectations.map((expectation) => expectation.file))]
  const results = await eslint.lintFiles(files)
  const failures: string[] = []

  for (const result of results) {
    for (const message of result.messages) {
      if (message.fatal === true) {
        failures.push(`${result.filePath}:${String(message.line)}: fatal: ${message.message}`)
      }
    }
  }
  for (const expectation of lintExpectations) {
    const reported = results.some(
      (result) =>
        result.filePath === `${cwd}/${expectation.file}` &&
        result.messages.some(
          (message) =>
            message.ruleId === expectation.ruleId &&
            message.line === expectation.line &&
            message.severity === 2,
        ),
    )
    if (!reported) {
      failures.push(
        `${expectation.file}:${String(expectation.line)}: expected error ${expectation.ruleId}`,
      )
    }
  }
  return failures
}

async function main(): Promise<void> {
  const cwd = process.cwd()
  const failures = [
    ...(await checkCompilerOptions(`${cwd}/tsconfig.app.json`)),
    ...(await checkLintFixtures(cwd)),
  ]
  for (const failure of failures) {
    console.error(failure)
  }
  if (failures.length > 0) {
    process.exitCode = 1
    return
  }
  console.log(`tooling check passed: ${String(lintExpectations.length)} expected lint errors found`)
}

await main()

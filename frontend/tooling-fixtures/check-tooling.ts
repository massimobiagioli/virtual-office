// Tooling check (US-01.06, US-01.07): the strict TypeScript options are set, every negative lint
// fixture fails with the exact rule, file and line it exists for, every positive fixture lints
// clean, and `pnpm test` with the real `vitest.config.ts` fails an under-covered fixture project
// on its global coverage thresholds. A non-zero exit alone is not enough: a fixture that fails for another
// reason (a typo, a parse error, a failing test) would hide a broken rule (ADR-0009). Run with
// `pnpm check:tooling`; ESLint loads `eslint.config.ts` natively.
import { spawnSync } from 'node:child_process'
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import process from 'node:process'

import { ESLint } from 'eslint'
import ts from 'typescript'

interface LintExpectation {
  readonly file: string
  readonly ruleId: string
  readonly line: number
  // Part of the message that proves which config entry reported it, when two entries share
  // a rule id (e.g. the audio and the PixiJS groups of `no-restricted-imports`).
  readonly messageIncludes?: string
}

// FRONTEND.md §2: compiler options every tsconfig must set, with their values; `types`
// differs between the app (`vite/client`) and the Node tooling (`node`).
const strictCompilerOptions: Readonly<Record<string, unknown>> = {
  strict: true,
  noUncheckedIndexedAccess: true,
  exactOptionalPropertyTypes: true,
  noImplicitOverride: true,
  noFallthroughCasesInSwitch: true,
  noPropertyAccessFromIndexSignature: true,
  verbatimModuleSyntax: true,
  isolatedModules: true,
  moduleResolution: 'bundler',
}
const requiredCompilerOptions: Readonly<Record<string, Readonly<Record<string, unknown>>>> = {
  'tsconfig.app.json': { ...strictCompilerOptions, types: ['vite/client'] },
  'tsconfig.node.json': { ...strictCompilerOptions, types: ['node'] },
}

const noSound = '§14.10'
const fixture = (file: string): string => `tooling-fixtures/src/${file}`

const lintExpectations: readonly LintExpectation[] = [
  // Vue: Composition API with <script setup> only.
  { file: fixture('windows/OptionsApiWindow.vue'), ruleId: 'vue/component-api-style', line: 5 },
  // Named exports only (FRONTEND.md §2 rule 5).
  { file: fixture('shared/default-export.ts'), ruleId: 'no-restricted-exports', line: 2 },
  // Module boundaries (FRONTEND.md §1.1).
  ...[2, 3].map((line) => ({
    file: fixture('office-engine/imports-vue.ts'),
    ruleId: 'boundaries/dependencies',
    line,
  })),
  { file: fixture('office-engine/imports-pixi.ts'), ruleId: 'boundaries/dependencies', line: 2 },
  {
    file: fixture('office-engine/imports-pixi.ts'),
    ruleId: 'no-restricted-imports',
    line: 2,
    messageIncludes: 'office-renderer',
  },
  {
    file: fixture('office-engine/imports-api-module.ts'),
    ruleId: 'boundaries/dependencies',
    line: 3,
  },
  {
    file: fixture('office-engine/imports-api-module.ts'),
    ruleId: 'boundaries/dependencies',
    line: 4,
  },
  {
    file: fixture('stores/imports-engine-value.ts'),
    ruleId: 'boundaries/dependencies',
    line: 2,
  },
  { file: fixture('ui-amiga/imports-store.ts'), ruleId: 'boundaries/dependencies', line: 2 },
  ...['shared/imports-vue.ts', 'office-renderer/imports-vue.ts'].flatMap((file) =>
    [2, 3, 4, 5].map((line) => ({ file: fixture(file), ruleId: 'boundaries/dependencies', line })),
  ),
  { file: fixture('api/imports-pinia.ts'), ruleId: 'boundaries/dependencies', line: 2 },
  // No audio, ever (Constitution §14.10): one line per banned name.
  ...[3, 4, 5, 6, 7, 8].map((line) => ({
    file: fixture('shared/uses-audio.ts'),
    ruleId: 'no-restricted-imports',
    line,
    messageIncludes: noSound,
  })),
  ...[12, 13, 14, 15, 16, 17, 18].map((line) => ({
    file: fixture('shared/uses-audio.ts'),
    ruleId: 'no-restricted-globals',
    line,
    messageIncludes: noSound,
  })),
  ...[19, 20, 21].map((line) => ({
    file: fixture('shared/uses-audio.ts'),
    ruleId: 'no-restricted-properties',
    line,
    messageIncludes: noSound,
  })),
  ...[22, 23, 24, 25].map((line) => ({
    file: fixture('shared/uses-audio.ts'),
    ruleId: 'no-restricted-syntax',
    line,
    messageIncludes: noSound,
  })),
  ...[2, 3].map((line) => ({
    file: fixture('office-renderer/imports-sound.ts'),
    ruleId: 'no-restricted-imports',
    line,
    messageIncludes: noSound,
  })),
  {
    file: fixture('windows/AudioWindow.vue'),
    ruleId: 'vue/no-restricted-html-elements',
    line: 3,
    messageIncludes: noSound,
  },
  ...[4, 5, 6].map((line) => ({
    file: fixture('windows/AudioWindow.vue'),
    ruleId: 'vue/no-restricted-syntax',
    line,
    messageIncludes: noSound,
  })),
]

// Positive fixtures: every edge FRONTEND.md §1.1 allows, intra-element imports, a muted
// <video> and plain externals. They must produce no message at all, so a rule that rejects an
// allowed edge (with `default: 'disallow'`) is caught too.
const cleanFixtures: readonly string[] = [
  'shared/geometry.ts',
  'shared/point-label.ts',
  'api/schema.d.ts',
  'api/types.ts',
  'office-engine/scene.ts',
  'office-renderer/draw-scene.ts',
  'stores/use-board-store.ts',
  'composables/use-board.ts',
  'ui-amiga/use-focus-label.ts',
  'windows/BoardWindow.vue',
  'windows/board-title.ts',
].map(fixture)

// Coverage fixture: a project shaped like `src/` whose single spec passes and fully covers
// `shared/covered.ts`, while `shared/never-imported.ts` is imported by nothing. Only the explicit
// `coverage.include` of `vitest.config.ts` counts that file (as 0 %), and only that file pulls
// the totals under the thresholds. The check runs the real `pnpm test` script with the real
// config (`--root` points at the fixture), so it proves the gate as developers and CI run it.
// `globalThreshold` is the Constitution §18.2 expectation (others ≥ 70 %) the config must match.
const coverageFixture = 'tooling-fixtures/under-covered'
const coveredFile = 'src/shared/covered.ts'
const neverImportedFile = 'src/shared/never-imported.ts'
const globalThreshold = 70
const coverageMetrics = ['lines', 'functions', 'statements', 'branches'] as const

type CoverageMetric = (typeof coverageMetrics)[number]
// `coverage-summary.json` (the `json-summary` reporter): one entry per file, keyed by its
// absolute path, plus `total`.
type CoverageSummary = Readonly<
  Record<string, Readonly<Record<CoverageMetric, { readonly pct: number }>> | undefined>
>
// The fields of Vitest's `json` reporter the check relies on.
interface TestResults {
  readonly numTotalTests: number
  readonly numPassedTests: number
  readonly numFailedTests: number
}

function sameJson(left: unknown, right: unknown): boolean {
  return JSON.stringify(left) === JSON.stringify(right)
}

function diagnosticText(diagnostic: ts.Diagnostic): string {
  return ts.flattenDiagnosticMessageText(diagnostic.messageText, '\n')
}

// Reads a tsconfig as TypeScript does: JSONC comments, trailing commas and `extends` included.
function checkCompilerOptions(
  configPath: string,
  required: Readonly<Record<string, unknown>>,
): string[] {
  const read = ts.readConfigFile(configPath, (file) => ts.sys.readFile(file))
  if (read.error !== undefined) {
    return [`${configPath}: ${diagnosticText(read.error)}`]
  }
  const directory = path.dirname(configPath)
  const parsed = ts.parseJsonConfigFileContent(
    read.config,
    ts.sys,
    directory,
    undefined,
    configPath,
  )
  const expected = ts.convertCompilerOptionsFromJson(required, directory)
  const errors = [...parsed.errors, ...expected.errors].map(
    (diagnostic) => `${configPath}: ${diagnosticText(diagnostic)}`,
  )
  const options: Readonly<Record<string, unknown>> = parsed.options
  const mismatches = Object.keys(required)
    .filter((name) => !sameJson(options[name], expected.options[name]))
    .map(
      (name) =>
        `${configPath}: compilerOptions.${name} must be ${JSON.stringify(required[name])}, ` +
        `found ${JSON.stringify(options[name])}`,
    )
  return [...errors, ...mismatches]
}

function formatMessage(
  result: ESLint.LintResult,
  message: ESLint.LintResult['messages'][number],
): string {
  return `${result.filePath}:${String(message.line)}: ${message.ruleId ?? 'fatal'}: ${message.message}`
}

async function checkLintFixtures(cwd: string): Promise<string[]> {
  // `ignore: false`: the fixtures are globally ignored by `pnpm lint`, which must stay green.
  const eslint = new ESLint({ cwd, ignore: false, flags: ['unstable_native_nodejs_ts_config'] })
  const files = [
    ...new Set([...lintExpectations.map((expectation) => expectation.file), ...cleanFixtures]),
  ]
  const results = await eslint.lintFiles(files)
  const clean = new Set(cleanFixtures.map((file) => path.resolve(cwd, file)))
  const failures: string[] = []

  for (const result of results) {
    for (const message of result.messages) {
      if (message.fatal === true) {
        failures.push(`fatal: ${formatMessage(result, message)}`)
      } else if (clean.has(result.filePath)) {
        failures.push(`positive fixture must lint clean: ${formatMessage(result, message)}`)
      }
    }
  }
  for (const expectation of lintExpectations) {
    const reported = results.some(
      (result) =>
        result.filePath === path.resolve(cwd, expectation.file) &&
        result.messages.some(
          (message) =>
            message.ruleId === expectation.ruleId &&
            message.line === expectation.line &&
            message.severity === 2 &&
            message.message.includes(expectation.messageIncludes ?? ''),
        ),
    )
    if (!reported) {
      const detail =
        expectation.messageIncludes === undefined ? '' : ` with "${expectation.messageIncludes}"`
      failures.push(
        `${expectation.file}:${String(expectation.line)}: expected error ${expectation.ruleId}${detail}`,
      )
    }
  }
  return failures
}

function readJson(file: string): unknown {
  return JSON.parse(readFileSync(file, 'utf8')) as unknown
}

function checkFileCoverage(
  summary: CoverageSummary,
  root: string,
  file: string,
  accept: (pct: number) => boolean,
  expectation: string,
): string[] {
  const entry = summary[path.resolve(root, file)]
  if (entry === undefined) {
    return [`${coverageFixture}: ${file} is missing from the coverage report`]
  }
  return coverageMetrics
    .filter((metric) => !accept(entry[metric].pct))
    .map(
      (metric) =>
        `${coverageFixture}: ${file} ${metric} must be ${expectation}, ` +
        `found ${String(entry[metric].pct)} %`,
    )
}

function checkCoverageThreshold(cwd: string): string[] {
  const root = path.resolve(cwd, coverageFixture)
  const outputDirectory = mkdtempSync(path.join(os.tmpdir(), 'vo-coverage-'))
  const reportsDirectory = path.join(outputDirectory, 'coverage')
  const resultsFile = path.join(outputDirectory, 'results.json')
  try {
    // `pnpm run test` adds only where to look and where to write: coverage itself must come
    // from the script and the config.
    const run = spawnSync(
      'pnpm',
      [
        'run',
        'test',
        '--config',
        path.resolve(cwd, 'vitest.config.ts'),
        '--root',
        root,
        `--coverage.reportsDirectory=${reportsDirectory}`,
        '--reporter=default',
        '--reporter=json',
        `--outputFile.json=${resultsFile}`,
      ],
      { cwd, encoding: 'utf8', env: { ...process.env, NO_COLOR: '1', CI: '1' } },
    )
    if (run.error !== undefined) {
      return [`${coverageFixture}: pnpm test did not start: ${run.error.message}`]
    }
    const output = `${run.stdout}\n${run.stderr}`
    const failures: string[] = []
    if (run.status === 0) {
      failures.push(`${coverageFixture}: pnpm test exited 0, expected a coverage threshold failure`)
    }
    // The fixture spec must pass: the run may fail on coverage only.
    const results = existsSync(resultsFile) ? (readJson(resultsFile) as Partial<TestResults>) : {}
    if (
      results.numTotalTests !== 1 ||
      results.numPassedTests !== 1 ||
      results.numFailedTests !== 0
    ) {
      failures.push(`${coverageFixture}: expected its single spec to pass\n${output}`)
    }
    for (const metric of coverageMetrics) {
      const message = new RegExp(
        `Coverage for ${metric} \\([\\d.]+%\\) does not meet global threshold ` +
          `\\(${String(globalThreshold)}%\\)`,
      )
      if (!message.test(output)) {
        failures.push(
          `${coverageFixture}: expected the ${metric} coverage to fail the global ` +
            `${String(globalThreshold)} % threshold`,
        )
      }
    }
    const summaryFile = path.join(reportsDirectory, 'coverage-summary.json')
    if (!existsSync(summaryFile)) {
      failures.push(`${coverageFixture}: no coverage-summary.json (json-summary reporter)`)
      return failures
    }
    const summary = readJson(summaryFile) as CoverageSummary
    return [
      ...failures,
      ...checkFileCoverage(summary, root, coveredFile, (pct) => pct >= globalThreshold, 'covered'),
      ...checkFileCoverage(summary, root, neverImportedFile, (pct) => pct === 0, '0 %'),
    ]
  } finally {
    rmSync(outputDirectory, { recursive: true, force: true })
  }
}

async function main(): Promise<void> {
  const cwd = process.cwd()
  const failures = [
    ...Object.entries(requiredCompilerOptions).flatMap(([file, required]) =>
      checkCompilerOptions(path.resolve(cwd, file), required),
    ),
    ...(await checkLintFixtures(cwd)),
    ...checkCoverageThreshold(cwd),
  ]
  for (const failure of failures) {
    console.error(failure)
  }
  if (failures.length > 0) {
    process.exitCode = 1
    return
  }
  console.log(
    `tooling check passed: ${String(lintExpectations.length)} expected lint errors found, ` +
      `${String(cleanFixtures.length)} positive fixtures clean, ` +
      `an unimported file pulls coverage below ${String(globalThreshold)} % on: ` +
      coverageMetrics.join(', '),
  )
}

await main()

// Tooling check (US-01.06): the strict TypeScript options are set, every negative lint fixture
// fails with the exact rule, file and line it exists for, and every positive fixture lints
// clean. A non-zero exit alone is not enough: a fixture that fails for another reason (a typo,
// a parse error) would hide a broken rule (ADR-0009). Run with `pnpm check:tooling`; ESLint
// loads `eslint.config.ts` natively.
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
  {
    file: fixture('shared/uses-audio.ts'),
    ruleId: 'no-restricted-syntax',
    line: 22,
    messageIncludes: noSound,
  },
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
  ...[4, 5].map((line) => ({
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

function describe(result: ESLint.LintResult, message: ESLint.LintResult['messages'][number]) {
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
        failures.push(`fatal: ${describe(result, message)}`)
      } else if (clean.has(result.filePath)) {
        failures.push(`positive fixture must lint clean: ${describe(result, message)}`)
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

async function main(): Promise<void> {
  const cwd = process.cwd()
  const failures = [
    ...Object.entries(requiredCompilerOptions).flatMap(([file, required]) =>
      checkCompilerOptions(path.resolve(cwd, file), required),
    ),
    ...(await checkLintFixtures(cwd)),
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
      `${String(cleanFixtures.length)} positive fixtures clean`,
  )
}

await main()

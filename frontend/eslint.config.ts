// ESLint flat config (FRONTEND.md §11). Loaded with Node's native type stripping
// (`--flag unstable_native_nodejs_ts_config`), so this file uses erasable syntax only.
import { vueTsConfigs, withVueTs } from '@vue/eslint-config-typescript'
import boundaries from 'eslint-plugin-boundaries'
import pluginVue from 'eslint-plugin-vue'
import prettierConfig from 'eslint-config-prettier'

// Module boundaries of FRONTEND.md §1.1. The patterns match from the right of the path, so the
// negative fixtures in `tooling-fixtures/src/` and the coverage fixture project in
// `tooling-fixtures/under-covered/src/` (linted, not ignored) are classified like the real
// `src/` folders.
// `assets/` and the files at the root of `src/` (main.ts, App.vue, router.ts) are not modules of
// the matrix: they stay unclassified, and imports of unclassified files are not checked.
const elements = [
  'shared',
  'api',
  'office-engine',
  'office-renderer',
  'stores',
  'composables',
  'ui-amiga',
  'windows',
].map((type) => ({ type, pattern: `src/${type}` }))

const local = (...types: string[]) => ({ to: { element: { types: { anyOf: types } } } })
const typesOnly = (type: string, fileInternalPath = '**') => ({
  dependency: { kind: 'type' as const },
  to: { element: { type, fileInternalPath } },
})
const external = (...sources: string[]) => ({
  to: { module: { origin: 'external' as const, source: sources } },
})
// The UI framework: allowed only where FRONTEND.md §1.1 lets Vue in (stores, composables,
// ui-amiga, windows).
const frameworkPackages = ['vue', 'vue-router', 'pinia', '@vue/*']

// No audio, ever (Constitution §14.10, FRONTEND.md §8.6): libraries, Web Audio, speech
// synthesis, audio files, audio elements and <audio>/<video> with sound.
const noSound = 'Virtual Office never produces sound (Constitution §14.10).'
const audioNames = [
  'Audio',
  'AudioContext',
  'OfflineAudioContext',
  'webkitAudioContext',
  'HTMLAudioElement',
  'speechSynthesis',
  'SpeechSynthesisUtterance',
]
const audioGlobals = audioNames.map((name) => ({ name, message: noSound }))
const audioProperties = ['window', 'globalThis', 'self'].flatMap((object) =>
  audioNames.map((property) => ({ object, property, message: noSound })),
)
// A gitignore-style pattern also matches the subpaths of a package (`@pixi/sound/filters`).
const audioImports = {
  group: ['@pixi/sound', 'howler', 'tone'],
  message: noSound,
}
// Audio files, with or without a Vite query (`beep.mp3?url`), in any letter case.
const audioFileImports = {
  regex: String.raw`\.(aac|aif|aiff|flac|m4a|mid|midi|mp3|oga|ogg|opus|wav|weba)(\?.*)?$`,
  caseSensitive: false,
  message: noSound,
}
// Creating an <audio> or <video> element from script, with a string or a static template
// literal tag name; a muted <video> belongs in a template. Computed tag names are not caught.
const mediaTag = '/^(audio|video)$/i'
const audioElementCreation = [
  `CallExpression[callee.property.name='createElement'][arguments.0.value=${mediaTag}]`,
  `CallExpression[callee.property.name='createElementNS'][arguments.1.value=${mediaTag}]`,
  `CallExpression[callee.property.name=/^createElement(NS)?$/] > TemplateLiteral.arguments[expressions.length=0][quasis.0.value.raw=${mediaTag}]`,
].map((selector) => ({ selector, message: noSound }))
const soundingVideo = {
  // A <video> is allowed only with its own static `muted` attribute (a muted child such as
  // <source muted> does not count): the start tag holds only the element's own attributes.
  selector:
    "VElement[name='video'] > VStartTag:not(:has(VAttribute[directive=false][key.name='muted']))",
  message: noSound,
}
const pixiImports = {
  group: ['pixi.js', 'pixi.js/*', '@pixi/*'],
  message: 'PixiJS is imported only in office-renderer (FRONTEND.md §1.1).',
}

export default withVueTs(
  {
    ignores: ['dist/', 'coverage/', 'node_modules/', 'tooling-fixtures/src/'],
  },
  pluginVue.configs['flat/recommended'],
  vueTsConfigs.strictTypeChecked,
  vueTsConfigs.stylisticTypeChecked,
  {
    name: 'virtual-office/rules',
    rules: {
      'vue/block-order': ['error', { order: ['script', 'template', 'style'] }],
      'vue/component-api-style': ['error', ['script-setup']],
      'vue/define-macros-order': 'error',
      'vue/no-unused-properties': 'error',
      '@typescript-eslint/consistent-type-imports': 'error',
      'no-restricted-globals': ['error', ...audioGlobals],
      'no-restricted-properties': ['error', ...audioProperties],
      'no-restricted-syntax': ['error', ...audioElementCreation],
      'vue/no-restricted-html-elements': ['error', { element: ['audio'], message: noSound }],
      'vue/no-restricted-syntax': ['error', soundingVideo],
      'no-restricted-imports': [
        'error',
        { patterns: [audioImports, audioFileImports, pixiImports] },
      ],
    },
  },
  {
    // Named exports only (FRONTEND.md §2 rule 5); SFCs are exempt, being `.vue` files.
    name: 'virtual-office/named-exports',
    files: ['**/*.ts'],
    rules: {
      'no-restricted-exports': [
        'error',
        {
          restrictDefaultExports: {
            direct: true,
            named: true,
            defaultFrom: true,
            namedFrom: true,
            namespaceFrom: true,
          },
        },
      ],
    },
  },
  {
    name: 'virtual-office/office-renderer',
    files: ['**/src/office-renderer/**'],
    rules: {
      'no-restricted-imports': ['error', { patterns: [audioImports, audioFileImports] }],
    },
  },
  {
    name: 'virtual-office/boundaries',
    files: ['**/src/**/*.{ts,vue}'],
    plugins: { boundaries },
    settings: {
      'boundaries/elements': elements,
      'import/resolver': { node: { extensions: ['.ts', '.d.ts', '.vue'] } },
    },
    rules: {
      'boundaries/dependencies': [
        'error',
        {
          default: 'disallow',
          checkAllOrigins: true,
          // Imports inside one element (windows → windows) are never checked.
          checkInternals: false,
          policies: [
            // Any element may use the platform and every external package except the ones
            // restricted below; local elements follow the FRONTEND.md §1.1 matrix.
            { from: { element: { type: '*' } }, allow: { to: { module: { origin: 'core' } } } },
            {
              from: { element: { type: '*' } },
              allow: { to: { module: { origin: 'external' } } },
            },
            {
              // shared/, api/, office-engine/ and office-renderer/ are plain TypeScript (and
              // PixiJS for the renderer): no framework (FRONTEND.md §1, §1.1).
              from: {
                element: {
                  types: { anyOf: ['shared', 'api', 'office-engine', 'office-renderer'] },
                },
              },
              disallow: external(...frameworkPackages),
            },
            { from: { element: { type: 'api' } }, allow: local('shared') },
            {
              from: { element: { type: 'office-engine' } },
              allow: [local('shared'), typesOnly('api', 'schema.d.ts')],
            },
            {
              from: { element: { type: 'office-engine' } },
              disallow: external('pixi.js', '@pixi/*'),
            },
            {
              from: { element: { type: 'office-renderer' } },
              allow: local('office-engine', 'shared'),
            },
            {
              from: { element: { type: 'stores' } },
              allow: [local('api', 'shared'), typesOnly('office-engine')],
            },
            {
              from: { element: { type: 'composables' } },
              allow: local('stores', 'api', 'shared'),
            },
            {
              from: { element: { type: 'ui-amiga' } },
              allow: local('shared', 'composables'),
            },
            {
              from: { element: { type: 'windows' } },
              allow: local(
                'shared',
                'api',
                'office-engine',
                'office-renderer',
                'stores',
                'composables',
                'ui-amiga',
              ),
            },
          ],
        },
      ],
    },
  },
  {
    name: 'virtual-office/tooling',
    files: ['*.config.ts'],
    rules: {
      // Tools require a default export from their config files (FRONTEND.md §2 rule 5).
      'no-restricted-exports': 'off',
    },
  },
  prettierConfig,
)

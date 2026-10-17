// ESLint flat config (FRONTEND.md §11). Loaded with Node's native type stripping
// (`--flag unstable_native_nodejs_ts_config`), so this file uses erasable syntax only.
import { vueTsConfigs, withVueTs } from '@vue/eslint-config-typescript'
import boundaries from 'eslint-plugin-boundaries'
import pluginVue from 'eslint-plugin-vue'
import prettierConfig from 'eslint-config-prettier'

// Module boundaries of FRONTEND.md §1.1. The patterns match from the right of the path, so the
// negative fixtures in `tooling-fixtures/src/` are classified like the real `src/` folders.
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
const typesOnly = (...types: string[]) => ({
  dependency: { kind: 'type' as const },
  to: { element: { types: { anyOf: types } } },
})
const external = (...sources: string[]) => ({
  to: { module: { origin: 'external' as const, source: sources } },
})

// No audio, ever (Constitution §14.10, FRONTEND.md §8.6).
const audioGlobals = ['Audio', 'AudioContext', 'OfflineAudioContext', 'webkitAudioContext'].map(
  (name) => ({ name, message: 'Virtual Office never produces sound (Constitution §14.10).' }),
)
const audioImports = {
  group: ['@pixi/sound', '@pixi/sound/*', 'howler', 'tone'],
  message: 'Virtual Office never produces sound (Constitution §14.10).',
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
      'no-restricted-imports': ['error', { patterns: [audioImports, pixiImports] }],
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
      'no-restricted-imports': ['error', { patterns: [audioImports] }],
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
          policies: [
            // Any element may use the platform and every external package except the ones
            // restricted below; local elements follow the FRONTEND.md §1.1 matrix.
            { from: { element: { type: '*' } }, allow: { to: { module: { origin: 'core' } } } },
            {
              from: { element: { type: '*' } },
              allow: { to: { module: { origin: 'external' } } },
            },
            { from: { element: { type: 'api' } }, allow: local('shared') },
            {
              from: { element: { type: 'office-engine' } },
              allow: [local('shared'), typesOnly('api')],
            },
            {
              from: { element: { type: 'office-engine' } },
              disallow: external('vue', 'vue-router', 'pinia', 'pixi.js', '@pixi/*'),
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
                'windows',
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

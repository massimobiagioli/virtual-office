import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory } from 'vue-router'

import App from './App.vue'
import { createWorkbenchRouter } from './router'
import WorkbenchDesktop from './windows/WorkbenchDesktop.vue'

async function mountApp() {
  const router = createWorkbenchRouter(createMemoryHistory())
  await router.push('/')
  await router.isReady()

  return mount(App, { global: { plugins: [createPinia(), router] } })
}

describe('App', () => {
  it('renders the My Workbench title', async () => {
    const wrapper = await mountApp()

    expect(wrapper.get('h1').text()).toBe('My Workbench')
  })

  it('renders the root route view through RouterView', async () => {
    const wrapper = await mountApp()

    expect(wrapper.findComponent(WorkbenchDesktop).exists()).toBe(true)
  })
})

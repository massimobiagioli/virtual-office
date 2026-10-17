import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { describe, expect, it } from 'vitest'

import App from './App.vue'
import { createWorkbenchRouter } from './router'

describe('App', () => {
  it('renders the My Workbench title', async () => {
    const router = createWorkbenchRouter('memory')
    await router.push('/')

    const wrapper = mount(App, { global: { plugins: [createPinia(), router] } })

    expect(wrapper.get('h1').text()).toBe('My Workbench')
  })
})

import { describe, expect, it } from 'vitest'
import { createMemoryHistory } from 'vue-router'

import { createWorkbenchRouter } from './router'

describe('createWorkbenchRouter', () => {
  it('resolves the root path to the workbench route', () => {
    const router = createWorkbenchRouter(createMemoryHistory())

    expect(router.resolve('/').name).toBe('workbench')
  })
})

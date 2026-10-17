import { describe, expect, it } from 'vitest'

import { createWorkbenchRouter } from './router'

describe('createWorkbenchRouter', () => {
  it('resolves the root path to the workbench route', () => {
    const router = createWorkbenchRouter('memory')

    expect(router.resolve('/').name).toBe('workbench')
  })
})

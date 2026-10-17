import { describe, expect, it } from 'vitest'

import { increment } from './partly-covered'

describe('increment', () => {
  it('adds one to the value', () => {
    expect(increment(1)).toBe(2)
  })
})

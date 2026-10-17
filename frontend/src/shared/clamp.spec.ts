import fc from 'fast-check'
import { describe, expect, it } from 'vitest'

import { clamp } from './clamp'

// A pair of finite bounds with min <= max.
const bounds = fc
  .tuple(
    fc.double({ noNaN: true, noDefaultInfinity: true }),
    fc.double({ noNaN: true, noDefaultInfinity: true }),
  )
  .map(([a, b]) => (a <= b ? { min: a, max: b } : { min: b, max: a }))

describe('clamp', () => {
  it('keeps a value that is already inside the range', () => {
    expect(clamp(3, 1, 5)).toBe(3)
  })

  it('raises a value below the range to the minimum', () => {
    expect(clamp(-2, 1, 5)).toBe(1)
  })

  it('lowers a value above the range to the maximum', () => {
    expect(clamp(9, 1, 5)).toBe(5)
  })

  it('rejects a range whose minimum is above its maximum', () => {
    expect(() => clamp(3, 5, 1)).toThrow(RangeError)
  })

  it('rejects a range with a NaN bound', () => {
    expect(() => clamp(3, Number.NaN, 5)).toThrow(RangeError)
    expect(() => clamp(3, 1, Number.NaN)).toThrow(RangeError)
  })

  it('always returns a value inside the range', () => {
    fc.assert(
      fc.property(fc.double({ noNaN: true }), bounds, (value, { min, max }) => {
        const result = clamp(value, min, max)

        expect(result).toBeGreaterThanOrEqual(min)
        expect(result).toBeLessThanOrEqual(max)
      }),
    )
  })

  it('is idempotent', () => {
    fc.assert(
      fc.property(fc.double({ noNaN: true }), bounds, (value, { min, max }) => {
        const once = clamp(value, min, max)

        expect(clamp(once, min, max)).toBe(once)
      }),
    )
  })
})

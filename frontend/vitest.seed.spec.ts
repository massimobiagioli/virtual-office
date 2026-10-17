import process from 'node:process'

import fc from 'fast-check'
import { describe, expect, it } from 'vitest'

import { defaultPropertySeed, propertySeed } from './vitest.seed.ts'

describe('propertySeed', () => {
  it('uses the fixed default seed when FC_SEED is not set', () => {
    expect(propertySeed(undefined)).toBe(20261017)
    expect(defaultPropertySeed).toBe(20261017)
  })

  it('uses the fixed default seed when FC_SEED is empty', () => {
    expect(propertySeed('')).toBe(defaultPropertySeed)
  })

  it('uses the integer given in FC_SEED', () => {
    expect(propertySeed('42')).toBe(42)
    expect(propertySeed('-7')).toBe(-7)
  })

  it('rejects an FC_SEED that is not a safe integer', () => {
    expect(() => propertySeed('abc')).toThrow(RangeError)
    expect(() => propertySeed('1.5')).toThrow(RangeError)
    expect(() => propertySeed('9007199254740993')).toThrow(RangeError)
  })
})

describe('vitest.setup.ts', () => {
  it('configures fast-check with the seed of FC_SEED or the fixed default', () => {
    expect(fc.readConfigureGlobal().seed).toBe(propertySeed(process.env['FC_SEED']))
  })
})

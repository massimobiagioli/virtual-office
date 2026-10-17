// Coverage fixture (US-01.07): no spec imports this module. Only the explicit `coverage.include`
// of `vitest.config.ts` counts it, as 0 %, and that pulls every total under the 70 % threshold.
export function describeSign(value: number): string {
  if (value > 0) {
    return 'positive'
  }
  if (value < 0) {
    return 'negative'
  }
  return 'zero'
}

export function sumOfSquares(values: readonly number[]): number {
  let total = 0
  for (const value of values) {
    total += value * value
  }
  return total
}

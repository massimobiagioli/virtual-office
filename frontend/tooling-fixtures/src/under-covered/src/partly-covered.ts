// Coverage fixture (US-01.07): the spec beside it exercises only `increment`, so lines,
// statements, functions and branches stay well below the 70 % global threshold.
export function increment(value: number): number {
  return value + 1
}

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

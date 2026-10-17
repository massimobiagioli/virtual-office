// Limits a number to the closed range [min, max], e.g. a zoom factor or a scroll offset.
export function clamp(value: number, min: number, max: number): number {
  if (min > max) {
    throw new RangeError(`clamp: min (${String(min)}) is above max (${String(max)})`)
  }
  return Math.min(Math.max(value, min), max)
}

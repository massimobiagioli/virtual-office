// Limits a number to the closed range [min, max], e.g. a zoom factor or a scroll offset.
export function clamp(value: number, min: number, max: number): number {
  if (Number.isNaN(min) || Number.isNaN(max)) {
    throw new RangeError(`clamp: bounds must be numbers, found [${String(min)}, ${String(max)}]`)
  }
  if (min > max) {
    throw new RangeError(`clamp: min (${String(min)}) is above max (${String(max)})`)
  }
  return Math.min(Math.max(value, min), max)
}

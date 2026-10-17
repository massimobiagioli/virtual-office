// Positive lint fixture: an import inside the same element (shared → shared).
import type { Point } from './geometry'

export function pointLabel(point: Point): string {
  return `${String(point.x)},${String(point.y)}`
}

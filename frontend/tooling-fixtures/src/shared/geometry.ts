// Positive lint fixture: plain shared utility, imported by every other module.
export interface Point {
  readonly x: number
  readonly y: number
}

export function addPoints(left: Point, right: Point): Point {
  return { x: left.x + right.x, y: left.y + right.y }
}

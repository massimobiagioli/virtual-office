// Positive lint fixture: office-engine → shared (value) and → api/schema.d.ts (types only).
import type { CardSchema } from '../api/schema'
import { addPoints } from '../shared/geometry'
import type { Point } from '../shared/geometry'

export interface SceneCard {
  readonly card: CardSchema
  readonly position: Point
}

export function placeCard(card: CardSchema, position: Point): SceneCard {
  return { card, position: addPoints(position, { x: 1, y: 1 }) }
}

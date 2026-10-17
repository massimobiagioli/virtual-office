// Positive lint fixture: api → shared (value) and an intra-element type import.
import { pointLabel } from '../shared/point-label'
import type { CardSchema } from './schema'

export type Card = CardSchema

export function cardLabel(card: Card): string {
  return `${card.id} · ${card.title} @ ${pointLabel({ x: 0, y: 0 })}`
}

// Positive lint fixture: stores → api, → shared (values) and → office-engine (types only).
import { cardLabel } from '../api/types'
import type { Card } from '../api/types'
import type { SceneCard } from '../office-engine/scene'
import { pointLabel } from '../shared/point-label'

export function boardLabels(cards: readonly Card[], scene: readonly SceneCard[]): string[] {
  return [...cards.map(cardLabel), ...scene.map((item) => pointLabel(item.position))]
}

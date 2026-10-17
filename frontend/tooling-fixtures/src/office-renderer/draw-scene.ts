// Positive lint fixture: office-renderer → office-engine and → shared (values).
import { placeCard } from '../office-engine/scene'
import type { SceneCard } from '../office-engine/scene'
import { pointLabel } from '../shared/point-label'

export function drawCard(id: string): string {
  const scene: SceneCard = placeCard({ id, title: 'Card' }, { x: 0, y: 0 })
  return pointLabel(scene.position)
}

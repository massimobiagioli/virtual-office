// Positive lint fixture: ui-amiga → composables and → shared.
import type { ComputedRef } from 'vue'

import { useBoard } from '../composables/use-board'
import { pointLabel } from '../shared/point-label'

export function useFocusLabel(): { labels: ComputedRef<string[]>; origin: string } {
  return { labels: useBoard([]), origin: pointLabel({ x: 0, y: 0 }) }
}

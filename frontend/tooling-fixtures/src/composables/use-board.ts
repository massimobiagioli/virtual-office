// Positive lint fixture: composables → stores, → api and → shared.
import { computed } from 'vue'
import type { ComputedRef } from 'vue'

import { cardLabel } from '../api/types'
import type { Card } from '../api/types'
import { pointLabel } from '../shared/point-label'
import { boardLabels } from '../stores/use-board-store'

export function useBoard(cards: readonly Card[]): ComputedRef<string[]> {
  return computed(() => [
    ...boardLabels(cards, []),
    ...cards.map(cardLabel),
    pointLabel({ x: 0, y: 0 }),
  ])
}

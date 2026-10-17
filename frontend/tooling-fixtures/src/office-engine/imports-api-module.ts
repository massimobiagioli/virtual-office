// Negative lint fixture: office-engine takes types from api/schema.d.ts only (FRONTEND.md §1.1),
// never values and never other api/ modules.
import { cardLabel } from '../api/types'
import type { Card } from '../api/types'

export const label: (card: Card) => string = cardLabel

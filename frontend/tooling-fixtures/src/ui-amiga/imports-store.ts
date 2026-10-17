// Negative lint fixture (US-01.06 AC3): the UI kit never imports stores (FRONTEND.md §1.1).
import { kanbanStoreId } from '../stores/use-kanban-store'

export const storeId = kanbanStoreId

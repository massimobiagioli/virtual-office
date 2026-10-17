// Negative lint fixture: api/ may import only shared/ (FRONTEND.md §1.1), never Pinia.
import { defineStore } from 'pinia'

export const store = defineStore

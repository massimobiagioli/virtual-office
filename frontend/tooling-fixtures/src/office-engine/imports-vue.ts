// Negative lint fixture (US-01.06 AC3): office-engine must not import vue (FRONTEND.md §1.1).
import { ref } from 'vue'
import { reactive } from '@vue/reactivity'

export const counter = ref(0)
export const state = reactive({ tick: 0 })

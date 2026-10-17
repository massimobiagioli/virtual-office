<!-- Positive lint fixture: windows import every module of FRONTEND.md §1.1; a muted <video>. -->
<script setup lang="ts">
import { computed } from 'vue'

import { cardLabel } from '../api/types'
import { useBoard } from '../composables/use-board'
import { placeCard } from '../office-engine/scene'
import { drawCard } from '../office-renderer/draw-scene'
import { pointLabel } from '../shared/point-label'
import { boardLabels } from '../stores/use-board-store'
import { useFocusLabel } from '../ui-amiga/use-focus-label'
import { boardTitle } from './board-title'

const card = { id: 'VO-1', title: 'Card' }
const labels = useBoard([card])
const focus = useFocusLabel()
const summary = computed(() =>
  [
    boardTitle,
    cardLabel(card),
    pointLabel(placeCard(card, { x: 0, y: 0 }).position),
    drawCard(card.id),
    ...boardLabels([card], []),
    ...labels.value,
    focus.origin,
  ].join(' '),
)
</script>

<template>
  <h2>{{ summary }}</h2>
  <video src="clip.mp4" muted />
</template>
